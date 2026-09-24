import threading
import time
import unittest

from jobs import JobQueue, QueueFull, current_job


class QueueTests(unittest.TestCase):
    def queue(self, runner, **kwargs):
        queue = JobQueue(runner, **kwargs)
        self.addCleanup(queue.close)
        return queue

    def test_fifo_limit_cancel_waiting_and_metrics_without_text(self):
        started, release = threading.Event(), threading.Event()
        order = []
        def runner(messages):
            order.append(messages)
            started.set()
            release.wait(2)
            return 200, {'message': 'Resposta validada.'}
        queue = self.queue(runner, capacity=2)
        first = queue.submit('conteúdo privado')
        self.assertTrue(started.wait(1))
        second, third = queue.submit('segundo'), queue.submit('terceiro')
        with self.assertRaises(QueueFull):
            queue.submit('quarto')
        self.assertEqual(queue.snapshot(third)['queue_position'], 2)
        queue.cancel(second.id)
        self.assertTrue(second.finished.wait(1))
        fourth = queue.submit('quarto')
        self.assertNotIn('result', queue.snapshot(first))
        release.set()
        self.assertTrue(fourth.finished.wait(2))
        self.assertEqual(order, ['conteúdo privado', 'terceiro', 'quarto'])
        self.assertNotIn('conteúdo privado', str(queue.metrics()))
        self.assertIsNone(first.messages)

    def test_active_cancellation_keeps_slot_until_worker_exits(self):
        started, release = threading.Event(), threading.Event()
        def runner(messages):
            started.set()
            release.wait(2)
            current_job().check()
            return 200, {'message': 'Não deve aparecer'}
        queue = self.queue(runner, capacity=0)
        job = queue.submit([])
        self.assertTrue(started.wait(1))
        queue.cancel(job.id)
        self.assertEqual(job.state, 'cancelling')
        with self.assertRaises(QueueFull):
            queue.submit([])
        release.set()
        self.assertTrue(job.finished.wait(1))
        self.assertEqual(job.state, 'cancelled')
        self.assertNotIn('result', queue.snapshot(job))

    def test_deadline_disconnect_queue_timeout_and_expiration(self):
        def runner(messages):
            current_job().cancelled.wait(2)
            current_job().check()
        for options, reason in [({'lease': .05}, 'client_disconnected'),
                                ({'run_timeout': .05}, 'run_timeout')]:
            with self.subTest(reason=reason):
                queue = self.queue(runner, retention=.01, **options)
                job = queue.submit([])
                self.assertTrue(job.finished.wait(2))
                self.assertEqual(job.reason, reason)
                time.sleep(.3)
                self.assertIsNone(queue.get(job.id))
        queue = self.queue(runner, queue_timeout=.05)
        active = queue.submit([])
        waiting = queue.submit([])
        self.assertTrue(waiting.finished.wait(2))
        self.assertEqual(waiting.reason, 'queue_timeout')
        queue.cancel(active.id)

    def test_unexpected_error_frees_slot_without_exposing_exception(self):
        def runner(messages):
            raise RuntimeError('PROMPT PRIVADO')
        queue = self.queue(runner, capacity=0)
        job = queue.submit([])
        self.assertTrue(job.finished.wait(1))
        self.assertEqual(job.state, 'error')
        self.assertNotIn('PRIVADO', str(queue.snapshot(job)))
        self.assertTrue(queue.submit([]).finished.wait(1))

    def test_configured_concurrency_is_respected(self):
        started, release = threading.Event(), threading.Event()
        lock = threading.Lock()
        running = 0
        peak = 0
        def runner(messages):
            nonlocal running, peak
            with lock:
                running += 1
                peak = max(peak, running)
                if running == 2:
                    started.set()
            release.wait(2)
            with lock:
                running -= 1
            return 200, {'message': 'Resposta validada.'}
        queue = self.queue(runner, concurrency=2, capacity=1)
        jobs = [queue.submit([]) for _ in range(3)]
        self.assertTrue(started.wait(1))
        self.assertEqual(queue.metrics()['active'], 2)
        self.assertEqual(queue.metrics()['waiting'], 1)
        release.set()
        for job in jobs:
            self.assertTrue(job.finished.wait(2))
        self.assertEqual(peak, 2)
