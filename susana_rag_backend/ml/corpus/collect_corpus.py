#!/usr/bin/env python3
"""Coleta corpus público ADMINISTRATIVO (não clínico) da SES-DF / MS.
Uso: python ml/corpus/collect_corpus.py
Saídas: data/corpus/sesdf_public.txt (formato sus_docs.txt + 'Fonte:') e data/corpus/manifest.json
"""
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).resolve().parent / "sources.yaml"
OUT_DIR = ROOT / "data" / "corpus"
OUT_TXT = OUT_DIR / "sesdf_public.txt"
OUT_MANIFEST = OUT_DIR / "manifest.json"

USER_AGENT = "SusanaCorpusBot/1.0 (projeto academico; coleta de paginas publicas administrativas)"
TIMEOUT = 15.0
DELAY_S = 1.0
MIN_CHARS = 200
MAX_BLOCK = 900
MIN_PARAGRAPH = 40
VALID_TAGS = {"UNIDADE", "VACINACAO", "SERVICO", "EMERGENCIA", "INSTITUCIONAL"}
NOISE_TAGS = ["script", "style", "noscript", "nav", "footer", "header", "aside", "form", "iframe", "svg", "button"]
NOISE_SELECTORS = [".navbar", ".breadcrumb", ".portlet-navigation", "#navigation", ".menu", ".footer",
                   ".social", ".share", "[role=navigation]", ".lfr-nav", ".skip-link"]
MAIN_SELECTORS = [".journal-content-article", "#main-content", "#content", "main", "article", "[role=main]"]

log = logging.getLogger("collect_corpus")


def load_sources() -> List[Dict[str, str]]:
    data = yaml.safe_load(SOURCES.read_text(encoding="utf-8")) or {}
    out = []
    for s in data.get("sources", []):
        if s.get("tag") not in VALID_TAGS or not str(s.get("url", "")).startswith("http"):
            log.warning("fonte inválida ignorada: %s", s)
            continue
        out.append(s)
    return out


def extract_paragraphs(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(NOISE_TAGS):
        t.decompose()
    for sel in NOISE_SELECTORS:
        for t in soup.select(sel):
            t.decompose()
    root = None
    for sel in MAIN_SELECTORS:
        cands = soup.select(sel)
        if cands:
            root = max(cands, key=lambda c: len(c.get_text(" ", strip=True)))
            break
    root = root or soup.body or soup
    paras: List[str] = []
    seen = set()
    for el in root.find_all(["p", "li", "h2", "h3", "h4", "td"]):
        txt = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if len(txt) < MIN_PARAGRAPH or txt in seen:
            continue
        link_chars = sum(len(a.get_text(strip=True)) for a in el.find_all("a"))
        if link_chars > 0.6 * len(txt):
            continue
        seen.add(txt)
        paras.append(txt)
    return paras


def chunk(paras: List[str], max_len: int = MAX_BLOCK) -> List[str]:
    blocks: List[str] = []
    cur: List[str] = []
    size = 0
    for p in paras:
        while len(p) > max_len:
            cut = p.rfind(". ", 0, max_len)
            cut = cut + 1 if cut > max_len // 2 else max_len
            pieces, p = p[:cut].strip(), p[cut:].strip()
            if cur:
                blocks.append("\n".join(cur)); cur, size = [], 0
            blocks.append(pieces)
        if size + len(p) + 1 > max_len and cur:
            blocks.append("\n".join(cur)); cur, size = [], 0
        if p:
            cur.append(p); size += len(p) + 1
    if cur:
        blocks.append("\n".join(cur))
    return blocks


def fetch(client: httpx.Client, url: str) -> Optional[str]:
    try:
        r = client.get(url)
        if r.status_code != 200:
            log.error("HTTP %s em %s", r.status_code, url)
            return None
        return r.text
    except httpx.HTTPError as exc:
        log.error("falha em %s: %s", url, exc)
        return None


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()
    out_blocks: List[str] = []
    manifest: List[Dict[str, object]] = []
    ok = fail = 0
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, follow_redirects=True) as client:
        for i, src in enumerate(sources):
            if i:
                time.sleep(DELAY_S)
            html = fetch(client, src["url"])
            if html is None:
                fail += 1
                continue
            paras = extract_paragraphs(html)
            text = "\n".join(paras)
            if len(text) < MIN_CHARS:
                log.warning("descartada (<%d chars úteis): %s", MIN_CHARS, src["url"])
                fail += 1
                continue
            blocks = chunk(paras)
            for n, b in enumerate(blocks, 1):
                out_blocks.append("[{}] {} (parte {})\n{}\nFonte: {}".format(src["tag"], src["title"], n, b, src["url"]))
            manifest.append({
                "url": src["url"], "title": src["title"], "tag": src["tag"],
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "n_chars": len(text), "n_blocos": len(blocks),
            })
            ok += 1
            log.info("ok %s -> %d blocos", src["url"], len(blocks))
    OUT_TXT.write_text("\n\n".join(out_blocks) + "\n", encoding="utf-8")
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("URLs ok=%d falha=%d blocos=%d arquivo=%s (%d bytes)", ok, fail, len(out_blocks), OUT_TXT, OUT_TXT.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
