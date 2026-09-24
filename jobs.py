"""Fila FIFO limitada, cancelamento cooperativo e métricas sem texto de conversa."""
from collections import deque
from contextlib import contextmanager
import resource
import secrets
import socket
import sys
import threading
import time

LOCAL = threading.local()
TERMINAL = {'done', 'error', 'cancelled'}


class Cancelled(Exception):
    pass


class QueueFull(Exception):
    pass


def current_job():
    return getattr(LOCAL, 'job', None)


@contextmanager
def stage(name):
    job = current_job()
    start = time.monotonic()
    if job:
        job.check()
        with job.lock:
            job.stage = name
    try:
        yield
    finally:
        if job:
            with job.lock:
                job.timings[name] = round(time.monotonic() - start, 4)


class Job:
    def __init__(self, messages):
        self.id = secrets.token_urlsafe(24)
        self.messages = messages
        self.lock = threading.RLock()
        self.cancelled = threading.Event()
        self.finished = threading.Event()
        self.created = self.last_seen = time.monotonic()
        self.started = self.ended = None
        self.state = self.stage = 'queued'
        self.result = self.error = None
        self.http_status = 200
        self.timings = {}
        self.upstream = None
        self.reason = None

    def check(self):
        if self.cancelled.is_set():
            raise Cancelled()

    def attach(self, sock):
        with self.lock:
            self.check()
            self.upstream = sock

    def cancel(self, reason='user'):
        with self.lock:
            if self.state in TERMINAL:
                return
            self.reason = reason
            self.cancelled.set()
            self.state = 'cancelling'
            if self.upstream:
                try:
                    # shutdown interrompe inclusive readline/getresponse bloqueados.
                    self.upstream.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    def snapshot(self):
        with self.lock:
            value = {'id': self.id, 'state': self.state, 'stage': self.stage,
                'elapsed_seconds': round((self.ended or time.monotonic()) - self.created, 2),
                'timings': dict(self.timings)}
            if self.state == 'done':
                value['result'] = self.result
            if self.error:
                value['error'] = self.error
            if self.reason:
                value['cancel_reason'] = self.reason
            return value


class JobQueue:
    def __init__(self, runner, concurrency=1, capacity=3, queue_timeout=120,
                 run_timeout=360, lease=20, retention=60):
        if not 1 <= concurrency <= 4 or not 0 <= capacity <= 16:
            raise ValueError('Concorrência deve ser 1–4 e fila deve ser 0–16.')
        self.runner = runner
        self.concurrency, self.capacity = concurrency, capacity
        self.queue_timeout, self.run_timeout = queue_timeout, run_timeout
        self.lease, self.retention = lease, retention
        self.condition = threading.Condition()
        self.pending = deque()
        self.jobs = {}
        self.records = deque(maxlen=100)
        self.active = 0
        self.closed = False
        self.stop = threading.Event()
        self.threads = [threading.Thread(target=self._worker, daemon=True)
                        for _ in range(concurrency)]
        self.threads.append(threading.Thread(target=self._watch, daemon=True))
        for thread in self.threads:
            thread.start()

    def submit(self, messages):
        with self.condition:
            if self.closed or self.active + len(self.pending) >= self.concurrency + self.capacity:
                raise QueueFull()
            job = Job(messages)
            self.jobs[job.id] = job
            self.pending.append(job)
            # Além do TTL, limite de resultados finalizados em memória.
            completed = [item for item in self.jobs.values() if item.finished.is_set()]
            for item in completed[:-32]:
                self.jobs.pop(item.id, None)
            self.condition.notify()
            return job

    def get(self, job_id, touch=True):
        with self.condition:
            job = self.jobs.get(job_id)
            if job and touch:
                job.last_seen = time.monotonic()
            return job

    def snapshot(self, job):
        with self.condition:
            value = job.snapshot()
            value['queue_position'] = list(self.pending).index(job) + 1 if job in self.pending else 0
            return value

    def cancel(self, job_id, reason='user'):
        with self.condition:
            job = self.jobs.get(job_id)
            if job:
                job.cancel(reason)
                if job in self.pending:
                    self.pending.remove(job)
                    self._finish(job)
                self.condition.notify_all()
            return job

    def _finish(self, job):
        with job.lock:
            if job.cancelled.is_set():
                job.state = 'cancelled'
                job.result = None
            job.ended = time.monotonic()
            job.timings['total'] = round(job.ended - job.created, 4)
            job.timings.setdefault('queue', round((job.started or job.ended) - job.created, 4))
            job.messages = None
            job.upstream = None
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            self.records.append({'state': job.state, 'timings': dict(job.timings),
                'cancel_reason': job.reason,
                'python_lifetime_peak_rss_mib': round(peak / (1024 ** 2 if sys.platform == 'darwin' else 1024), 2)})
            job.finished.set()

    def _worker(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.closed or self.pending)
                if self.closed:
                    return
                job = self.pending.popleft()
                self.active += 1
                with job.lock:
                    job.state = 'running'
                    job.started = time.monotonic()
                    job.timings['queue'] = round(job.started - job.created, 4)
            LOCAL.job = job
            try:
                job.check()
                status, result = self.runner(job.messages)
                with job.lock:
                    job.check()
                    job.http_status = status
                    if status == 200:
                        job.result, job.state = result, 'done'
                    else:
                        job.error, job.state = result['error'], 'error'
            except Cancelled:
                pass
            except Exception:
                # Exceções podem conter prompts: não registrar seu texto.
                with job.lock:
                    job.error, job.state, job.http_status = 'Falha interna ao processar a resposta.', 'error', 500
            finally:
                LOCAL.job = None
                with self.condition:
                    self.active -= 1
                    self._finish(job)
                    self.condition.notify_all()

    def _watch(self):
        while not self.stop.wait(.25):
            now = time.monotonic()
            with self.condition:
                for job in list(self.jobs.values()):
                    if job.finished.is_set():
                        if now - job.ended > self.retention:
                            self.jobs.pop(job.id, None)
                        continue
                    reason = None
                    if now - job.last_seen > self.lease:
                        reason = 'client_disconnected'
                    elif job.started and now - job.started > self.run_timeout:
                        reason = 'run_timeout'
                    elif not job.started and now - job.created > self.queue_timeout:
                        reason = 'queue_timeout'
                    if reason and not job.cancelled.is_set():
                        self.cancel(job.id, reason)

    def metrics(self):
        with self.condition:
            return {'concurrency': self.concurrency, 'queue_capacity': self.capacity,
                'active': self.active, 'waiting': len(self.pending), 'recent': list(self.records)}

    def close(self):
        with self.condition:
            self.closed = True
            for job in list(self.jobs.values()):
                self.cancel(job.id, 'server_shutdown')
            self.condition.notify_all()
        self.stop.set()
        for thread in self.threads:
            thread.join(timeout=6)
