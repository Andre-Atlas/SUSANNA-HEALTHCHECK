"""Inspeção estática de HTML/CSS; não renderiza nem certifica acessibilidade."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def declared(css, selector, property_name):
    value = None
    for block in re.findall(re.escape(selector) + r'\s*\{([^{}]*)\}', css):
        for key, candidate in re.findall(r'([\w-]+)\s*:\s*([^;]+)', block):
            if key == property_name:
                value = candidate.strip()
    return value


def contrast(foreground, background):
    def luminance(color):
        color = color.lstrip('#')
        if len(color) == 3:
            color = ''.join(c * 2 for c in color)
        channels = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
        return sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722)))
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + .05) / (dark + .05)


def audit():
    html = (ROOT / 'index.html').read_text()
    css = (ROOT / 'styles.css').read_text()
    parser = Markup()
    parser.feed(html)
    nodes = parser.nodes
    ids = Counter(attrs['id'] for _, attrs in nodes if 'id' in attrs)
    by_id = {attrs['id']: attrs for _, attrs in nodes if 'id' in attrs}
    refs = [ref for _, attrs in nodes for key in ('aria-describedby', 'aria-labelledby')
            for ref in attrs.get(key, '').split()]
    anchors = [attrs['href'][1:] for tag, attrs in nodes
               if tag == 'a' and attrs.get('href', '').startswith('#')]
    checks = {
        'portuguese_lang': any(tag == 'html' and attrs.get('lang') == 'pt-BR' for tag, attrs in nodes),
        'viewport_allows_zoom': any(tag == 'meta' and attrs.get('name') == 'viewport'
            and 'device-width' in attrs.get('content', '') and 'user-scalable=no' not in attrs.get('content', '')
            and 'maximum-scale=1' not in attrs.get('content', '') for tag, attrs in nodes),
        'unique_ids': all(count == 1 for count in ids.values()),
        'accessible_references_exist': all(ref in ids for ref in refs),
        'internal_links_exist': all(ref in ids for ref in anchors),
        'question_has_label': any(tag == 'label' and attrs.get('for') == 'question' for tag, attrs in nodes),
        'messages_keyboard_focusable': by_id.get('messages', {}).get('tabindex') == '0',
        'separate_progress_status': by_id.get('chat-progress', {}).get('role') == 'status',
        'skip_link': any(tag == 'a' and attrs.get('href') == '#main-content' for tag, attrs in nodes),
        'single_main_heading': sum(tag == 'h1' for tag, _ in nodes) == 1,
    }
    pairs = []
    for selector, background_selector in [('.bubble', '.bubble'), ('.bubble.user', '.bubble.user'),
                                         ('.chat-foot', '.chat'), ('#question', '.chat')]:
        fg, bg = declared(css, selector, 'color'), declared(css, background_selector, 'background')
        if fg == 'white':
            fg = '#ffffff'
        ratio = contrast(fg, bg)
        pairs.append({'selector': selector, 'foreground': fg, 'assumed_background': bg,
                      'ratio': round(ratio, 2), 'at_least_4_5': ratio >= 4.5})
    return {'created_at': datetime.now(timezone.utc).isoformat(),
        'method': 'HTML e declarações CSS selecionadas; sem DOM renderizado, layout ou estilos computados.',
        'checks': checks, 'selected_contrast_pairs': pairs,
        'static_pass': all(checks.values()) and all(item['at_least_4_5'] for item in pairs),
        'hashes': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                   for name in ('index.html', 'styles.css', 'app.js', 'audit_interface.py')},
        'pending': ['navegador desktop', '320/375/390/768 px e zoom 200%/400%',
                    'celular físico e teclado virtual', 'VoiceOver/TalkBack',
                    'foco/ordem de tabulação', 'dimensões renderizadas de alvos e contraste de todos os estados'],
        'browser_blocker': 'agent-browser ausente; cua.getState não encontrou apps/navegadores e informou falha no native pipe.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/interface-static.json')
    args = parser.parse_args()
    report = audit()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'checks': report['checks'], 'contrast': report['selected_contrast_pairs']}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['static_pass'] else 1)
