"""Busca ao vivo, restrita a páginas HTML HTTPS de domínios gov.br."""
from datetime import datetime
from html.parser import HTMLParser
import http.client
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from jobs import current_job


SEARCH_URL = 'https://www.gov.br/saude/pt-br/@@search?SearchableText='
USER_AGENT = 'SUSANNA-HEALTHCHECK/0.2 (prototipo educacional; busca fontes oficiais)'
MAX_SEARCH_BYTES = 2_000_000
MAX_PAGE_BYTES = 2_000_000
MAX_RESULTS = 3
MAX_CANDIDATES = 3
PAGE_TEXT_LIMIT = 2600


class GovBrSearchError(Exception):
    """A busca ou leitura das fontes oficiais falhou."""


def is_gov_br_url(url):
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or '').lower().rstrip('.')
        labels = host.split('.')
        valid_host = (len(host) <= 253 and all(
            re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label)
            for label in labels))
        return (valid_host and parsed.scheme == 'https' and parsed.username is None
                and parsed.password is None and parsed.port in (None, 443)
                and (host == 'gov.br' or host.endswith('.gov.br')))
    except (TypeError, ValueError):
        return False


class _GovBrRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        target = urljoin(request.full_url, new_url)
        if not is_gov_br_url(target):
            raise GovBrSearchError('O portal tentou redirecionar para fora de gov.br.')
        return super().redirect_request(request, fp, code, message, headers, target)


class _HTMLText(HTMLParser):
    SUPPRESS = {'script', 'style', 'noscript', 'svg', 'header', 'footer', 'nav', 'aside'}
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
            'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.suppressed = 0
        self.anchors = []
        self.anchor = None
        self.title = ''
        self.in_title = False
        self.in_h1 = False
        self.h1 = ''
        self._search_stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        marker = ' '.join((attrs.get('class', ''), attrs.get('id', ''))).lower()
        parent_search = bool(self._search_stack and self._search_stack[-1][1])
        in_search = parent_search or any(term in marker for term in ('search', 'result', 'listing'))
        if tag not in self.VOID:
            self._search_stack.append((tag, in_search))
        if tag in self.SUPPRESS:
            self.suppressed += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'h1':
            self.in_h1 = True
        if tag == 'a' and attrs.get('href'):
            self.anchor = {'href': attrs['href'], 'text': [], 'priority': in_search}
        if not self.suppressed and tag in {'p', 'br', 'div', 'li', 'h1', 'h2', 'h3'}:
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in self.SUPPRESS and self.suppressed:
            self.suppressed -= 1
        if tag == 'title':
            self.in_title = False
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'a' and self.anchor is not None:
            self.anchors.append((self.anchor['href'], ' '.join(self.anchor['text']),
                                 self.anchor['priority']))
            self.anchor = None
        if not self.suppressed and tag in {'p', 'br', 'div', 'li', 'h1', 'h2', 'h3'}:
            self.parts.append(' ')
        for index in range(len(self._search_stack) - 1, -1, -1):
            if self._search_stack[index][0] == tag:
                del self._search_stack[index:]
                break

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1 += data
        if not self.suppressed:
            self.parts.append(data)
        if self.anchor is not None:
            self.anchor['text'].append(data)


def _clean(text):
    return re.sub(r'\s+', ' ', text).strip()


def _read(url, limit, timeout):
    if not is_gov_br_url(url):
        raise GovBrSearchError('A URL não pertence a um domínio gov.br HTTPS.')
    request = Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml;q=0.9',
        'Accept-Language': 'pt-BR,pt;q=0.9',
    })
    opener = build_opener(_GovBrRedirects())
    job = current_job()
    if job:
        job.check()
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            if not is_gov_br_url(final_url):
                raise GovBrSearchError('A página final não pertence a gov.br.')
            content_type = response.headers.get_content_type()
            if content_type not in {'text/html', 'application/xhtml+xml'}:
                return None
            sock = getattr(getattr(getattr(response, 'fp', None), 'raw', None), '_sock', None)
            if job and sock:
                job.attach(sock)
            try:
                raw = response.read(limit + 1)
                if len(raw) > limit:
                    raise GovBrSearchError('A página excede o limite de leitura segura.')
                charset = response.headers.get_content_charset() or 'utf-8'
                if job:
                    job.check()
            finally:
                if job and sock:
                    with job.lock:
                        if job.upstream is sock:
                            job.upstream = None
    except GovBrSearchError:
        raise
    except (HTTPError, URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
        if job:
            job.check()
        raise GovBrSearchError('Não foi possível consultar o portal gov.br agora.') from exc
    try:
        return final_url, raw.decode(charset, errors='replace')
    except LookupError:
        return final_url, raw.decode('utf-8', errors='replace')


def _search_links(html, base_url):
    parser = _HTMLText()
    parser.feed(html)
    links = []
    seen = set()
    candidates = sorted(parser.anchors, key=lambda item: not item[2])
    for href, label, _priority in candidates:
        target = urljoin(base_url, href).split('#', 1)[0]
        path = urlsplit(target).path.lower()
        if (not is_gov_br_url(target) or not _clean(label) or target in seen
                or path.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip'))
                or '/@@search' in path or path.rstrip('/') == '/search'):
            continue
        seen.add(target)
        links.append((target, _clean(label)))
        if len(links) >= 15:
            break
    return links


def _extract_page(url, html, retrieved_at):
    parser = _HTMLText()
    parser.feed(html)
    title = _clean(parser.h1) or _clean(parser.title)
    text = _clean(' '.join(parser.parts))
    if len(text) < 180:
        return None
    if not title:
        title = text[:120].rsplit(' ', 1)[0]
    return {
        'title': title[:300],
        'text': text[:PAGE_TEXT_LIMIT],
        'url': url,
        'reviewed_at': retrieved_at[:10],
        'retrieved_at': retrieved_at,
        'source_type': 'gov_br_live',
    }


def search_gov_br(question, *, timeout=5):
    """Busca no portal do Ministério e retorna até três páginas gov.br extraídas."""
    query = _clean(question)
    if not query:
        return []
    search_url = SEARCH_URL + quote_plus(query[:400])
    try:
        fetched = _read(search_url, MAX_SEARCH_BYTES, timeout)
    except GovBrSearchError:
        raise
    if fetched is None:
        raise GovBrSearchError('A busca oficial não retornou uma página HTML.')
    search_final_url, search_html = fetched
    links = _search_links(search_html, search_final_url)
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    sources = []
    for url, _label in links[:MAX_CANDIDATES]:
        try:
            page = _read(url, MAX_PAGE_BYTES, timeout)
        except GovBrSearchError:
            continue
        if page is None:
            continue
        final_url, html = page
        parsed = _extract_page(final_url, html, now)
        if parsed:
            sources.append(parsed)
        if len(sources) >= MAX_RESULTS:
            break
    return sources
