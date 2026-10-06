"""Parsing do corpus no formato de blocos `[TAG] Título` (compartilhado entre indexação e avaliação)."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

_HEADER = re.compile(r"^\[([A-Z_]+)\]\s*(.+)$")
_FONTE = re.compile(r"^Fonte:\s*(\S+)\s*$", re.I)


@dataclass(frozen=True)
class CorpusBlock:
    id: str
    header: str          # "[UNIDADE] UBS 1 Asa Sul"
    tag: str             # "UNIDADE"
    text: str            # bloco completo (inclui cabeçalho)
    url: Optional[str]


def _block_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_corpus_text(raw: str) -> List[CorpusBlock]:
    blocks: List[CorpusBlock] = []
    header, tag, lines, url = "", "", [], None  # type: str, str, List[str], Optional[str]

    def flush() -> None:
        if header and lines:
            text = "\n".join(lines).strip()
            blocks.append(CorpusBlock(id=_block_id(text), header=header, tag=tag, text=text, url=url))

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = _HEADER.match(line)
        if m:
            flush()
            header, tag, lines, url = line, m.group(1), [line], None
            continue
        f = _FONTE.match(line)
        if f:
            url = f.group(1)
            continue
        if header:
            lines.append(line)
    flush()
    return blocks


def load_corpus(paths: Iterable[Path]) -> List[CorpusBlock]:
    seen = set()
    out: List[CorpusBlock] = []
    for p in paths:
        if not p.exists():
            continue
        for b in parse_corpus_text(p.read_text(encoding="utf-8")):
            if b.id not in seen:
                seen.add(b.id)
                out.append(b)
    return out
