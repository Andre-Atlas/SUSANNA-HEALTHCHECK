"""Parsing do corpus no formato de blocos `[TAG] Título` (compartilhado entre indexação e avaliação)."""
from __future__ import annotations

import hashlib
import csv
import json
import logging
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Optional, Sequence
from decimal import Decimal, InvalidOperation

_HEADER = re.compile(r"^\[([A-Z_]+)\]\s*(.+)$")
_FONTE = re.compile(r"^Fonte:\s*(\S+)\s*$", re.I)
_SUPPORTED_EXTENSIONS = {".csv", ".htm", ".html", ".json", ".md", ".pdf", ".txt"}
_CSV_CHUNK_CHARS = 900
_TEXT_CHUNK_CHARS = 900

logger = logging.getLogger("susana.corpus")


@dataclass(frozen=True)
class CorpusBlock:
    id: str
    header: str          # "[UNIDADE] UBS 1 Asa Sul"
    tag: str             # "UNIDADE"
    text: str            # bloco completo (inclui cabeçalho)
    url: Optional[str]


def _block_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _make_block(header: str, tag: str, text: str, url: Optional[str] = None) -> CorpusBlock:
    block_text = f"{header}\n{text}".strip()
    return CorpusBlock(
        id=_block_id(f"{block_text}\n{url or ''}"), header=header, tag=tag, text=block_text, url=url
    )


def parse_corpus_text(raw: str, source_id: str = "") -> List[CorpusBlock]:
    blocks: List[CorpusBlock] = []
    header, tag, lines, url = "", "", [], None  # type: str, str, List[str], Optional[str]

    def flush() -> None:
        if header and lines:
            text = "\n".join(lines).strip()
            block_id = _block_id(f"{source_id}\n{text}\n{url or ''}")
            blocks.append(CorpusBlock(id=block_id, header=header, tag=tag, text=text, url=url))

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


def discover_corpus_files(roots: Iterable[Path]) -> List[Path]:
    """Return supported corpus files in stable order, recursively."""
    files = set()
    for root in roots:
        if root.is_file() and root.suffix.lower() in _SUPPORTED_EXTENSIONS:
            files.add(root.resolve())
        elif root.is_dir():
            files.update(
                path.resolve()
                for path in root.rglob("*")
                if path.is_file()
                and not any(part.startswith(".") for part in path.relative_to(root).parts)
                and path.suffix.lower() in _SUPPORTED_EXTENSIONS
                and path.name.lower() != "manifest.json"
            )
    return sorted(files, key=lambda path: str(path).casefold())


def _chunks(text: str, max_chars: int = _TEXT_CHUNK_CHARS) -> Iterator[str]:
    text = re.sub(r"\s+", " ", text).strip()
    while len(text) > max_chars:
        cut = text.rfind(" ", 0, max_chars)
        if cut < max_chars // 2:
            cut = max_chars
        yield text[:cut].strip()
        text = text[cut:].strip()
    if text:
        yield text


def _source_url(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    if isinstance(value, list):
        return next((url for item in value if (url := _source_url(item))), None)
    if isinstance(value, dict):
        for key in ("url", "fonte", "source_url", "fonte_principal"):
            if url := _source_url(value.get(key)):
                return url
    return None


def _json_blocks(path: Path) -> List[CorpusBlock]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, (dict, list)):
        return []

    if isinstance(data, dict) and isinstance(data.get("chunks"), list):
        document = data.get("document") or {}
        title = document.get("source_title") or path.stem if isinstance(document, dict) else path.stem
        title = str(title)[:120]
        url = _source_url(document)
        entries = data["chunks"]
        blocks = []
        for index, entry in enumerate(entries, 1):
            if not isinstance(entry, dict):
                continue
            text = entry.get("text") or entry.get("content_original")
            metadata = entry.get("metadata")
            if isinstance(metadata, dict):
                context = " ".join(str(value) for value in metadata.values() if value not in (None, ""))
                text = f"{context}\n{text}" if context and text else text or context
            if isinstance(text, str):
                for part, chunk in enumerate(_chunks(text), 1):
                    header = f"[JSON] {title} (trecho {index}.{part})"
                    blocks.append(_make_block(header, "JSON", chunk, url))
        return blocks

    if isinstance(data, dict) and isinstance(data.get("documentos"), list):
        document = data.get("documento") or {}
        title = document.get("titulo", path.stem) if isinstance(document, dict) else path.stem
        title = str(title)[:120]
        blocks = []
        for index, entry in enumerate(data["documentos"], 1):
            if not isinstance(entry, dict):
                continue
            text = entry.get("texto_indexacao")
            question = entry.get("pergunta")
            answer = entry.get("resposta")
            body = "\n".join(str(value) for value in (question, answer, text) if value)
            url = _source_url(entry.get("fontes")) or _source_url(document)
            for part, chunk in enumerate(_chunks(body), 1):
                header = f"[FAQ] {title} (item {index}.{part})"
                blocks.append(_make_block(header, "FAQ", chunk, url))
        return blocks

    if isinstance(data, dict) and isinstance(data.get("conteudo"), (dict, list, str)):
        metadata = data.get("metadata") or {}
        title = metadata.get("titulo", path.stem) if isinstance(metadata, dict) else path.stem
        title = str(title)[:120]
        url = _source_url(metadata)
        body = "\n".join(_flatten_json(data["conteudo"]))
        return [
            _make_block(f"[JSON] {title} (trecho {index})", "JSON", chunk, url)
            for index, chunk in enumerate(_chunks(body), 1)
        ]

    title = path.stem
    if isinstance(data, dict) and isinstance(data.get("document"), dict):
        title = data["document"].get("source_title", title)
    title = str(title)[:120]
    body = "\n".join(_flatten_json(data))
    url = _source_url(data)
    return [
        _make_block(f"[JSON] {title} (trecho {index})", "JSON", chunk, url)
        for index, chunk in enumerate(_chunks(body), 1)
    ]


def _flatten_json(value: Any, prefix: str = "") -> List[str]:
    lines: List[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"schema_version", "document_id", "extracao", "metadata"}:
                continue
            lines.extend(_flatten_json(item, str(key)))
    elif isinstance(value, list):
        for item in value:
            lines.extend(_flatten_json(item, prefix))
    elif value not in (None, ""):
        lines.append(f"{prefix}: {value}" if prefix else str(value))
    return lines


def _text_encoding(path: Path) -> str:
    with path.open("rb") as source:
        sample = source.read(8192)
    for encoding in ("utf-8-sig", "utf-8", "iso-8859-1"):
        try:
            sample.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return "utf-8"


def _detect_delimiter(sample: str) -> str:
    header = next((line for line in sample.splitlines() if line.strip()), "")
    counts = {delimiter: header.count(delimiter) for delimiter in (";", ",", "\t", "|")}
    return max(counts, key=counts.get) if max(counts.values(), default=0) else ";"


def _normalized_column(field: str) -> str:
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", field).casefold()
        if not unicodedata.combining(char)
    )
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return {"cod_form_organizacao": "cod_forma_organizacao"}.get(normalized, normalized)


def _csv_blocks(path: Path) -> List[CorpusBlock]:
    encoding = _text_encoding(path)
    with path.open("r", encoding=encoding, newline="") as source:
        sample = source.read(8192)
        source.seek(0)
        delimiter = _detect_delimiter(sample)

        reader = csv.DictReader(source, delimiter=delimiter)
        if not reader.fieldnames:
            return []
        fields = [field for field in reader.fieldnames if field and field.strip().lower() not in {"geometry", "geom", "wkt"}]
        if not fields:
            return []

        measure_fields = [
            field
            for field in fields
            if any(
                token in "".join(
                    char
                    for char in unicodedata.normalize("NFKD", field).casefold()
                    if not unicodedata.combining(char)
                )
                for token in ("quantidade", "qtd", "count")
            )
        ]
        dimension_fields = [field for field in fields if field not in measure_fields]
        measure_groups: dict[tuple[str, ...], dict[str, Any]] = {}
        for row in reader:
            dimensions = tuple((row.get(field) or "").strip() for field in dimension_fields)
            measures = tuple((row.get(field) or "").strip() for field in measure_fields)
            if any(dimensions) or any(measures):
                group = measure_groups.setdefault(
                    dimensions,
                    {
                        "records": 0,
                        "totals": [Decimal(0) for _ in measure_fields],
                        "numeric": [True for _ in measure_fields],
                        "values": [Counter() for _ in measure_fields],
                    },
                )
                group["records"] += 1
                for index, value in enumerate(measures):
                    if not value:
                        continue
                    try:
                        number = Decimal(value.replace(",", "."))
                    except InvalidOperation:
                        group["numeric"][index] = False
                        group["values"][index][value] += 1
                    else:
                        group["totals"][index] += number

    if len(measure_groups) <= 500:
        blocks = []
        record_number = 0
        for dimensions, group in measure_groups.items():
            record_number += group["records"]
            dimension_text = "; ".join(
                f"{field.strip()}: {value}" for field, value in zip(dimension_fields, dimensions) if value
            )
            measure_texts = []
            for index, field in enumerate(measure_fields):
                if group["numeric"][index]:
                    total = group["totals"][index].normalize()
                    measure_texts.append(f"{field.strip()} total: {format(total, 'f')}")
                else:
                    observed = ", ".join(
                        f"{value} ({count} registros)" for value, count in group["values"][index].items()
                    )
                    measure_texts.append(f"{field.strip()}: {observed}")
            body = "; ".join(part for part in (dimension_text, ", ".join(measure_texts)) if part)
            body += f"; registros: {group['records']}"
            header = f"[CSV] {path.name[:100]} (registro {record_number})"
            blocks.extend(
                _make_block(header, "CSV", chunk)
                for chunk in _chunks(body, _CSV_CHUNK_CHARS)
            )
        return blocks

    blocks: List[CorpusBlock] = []
    lines: List[str] = []
    size = 0
    first_record = 1
    record_number = 0
    for dimensions, group in measure_groups.items():
        occurrences = group["records"]
        record_number += occurrences
        dimension_text = "; ".join(
            f"{field.strip()}: {value}" for field, value in zip(dimension_fields, dimensions) if value
        )
        measure_texts = []
        for index, field in enumerate(measure_fields):
            if group["numeric"][index]:
                total = group["totals"][index].normalize()
                measure_texts.append(f"{field.strip()} total: {format(total, 'f')}")
            else:
                observed = ", ".join(
                    f"{value} ({count} registros)" for value, count in group["values"][index].items()
                )
                measure_texts.append(f"{field.strip()}: {observed}")
        body = "; ".join(part for part in (dimension_text, ", ".join(measure_texts)) if part)
        body += f"; registros: {occurrences}"
        for line in _chunks(body, _CSV_CHUNK_CHARS):
            if lines and size + len(line) > _CSV_CHUNK_CHARS:
                header = f"[CSV] {path.name[:100]} (registros {first_record}-{record_number - occurrences})"
                blocks.append(_make_block(header, "CSV", "\n".join(lines)))
                lines, size = [], 0
                first_record = record_number - occurrences + 1
            lines.append(line)
            size += len(line) + 1
    if lines:
        header = f"[CSV] {path.name[:100]} (registros {first_record}-{record_number})"
        blocks.append(_make_block(header, "CSV", "\n".join(lines)))
    return blocks


def _csv_series_blocks(paths: Sequence[Path]) -> List[CorpusBlock]:
    monthly_groups: dict[tuple[str, ...], dict[str, Any]] = {}
    layouts: dict[Path, tuple[str, str, dict[str, str], str]] = {}
    dimension_keys: set[str] = set()
    measure_keys: set[str] = set()

    for path in paths:
        encoding = _text_encoding(path)
        with path.open("r", encoding=encoding, newline="") as source:
            sample = source.read(8192)
            source.seek(0)
            delimiter = _detect_delimiter(sample)
            reader = csv.DictReader(source, delimiter=delimiter)
            if not reader.fieldnames:
                continue

            fields = [field for field in reader.fieldnames if field and field.strip().lower() not in {"geometry", "geom", "wkt"}]
            normalized = {_normalized_column(field): field for field in fields}
            month_fields = [
                key
                for key in normalized
                if key in {"ano_mes", "mes", "competencia", "mes_competencia"} or "competencia" in key
            ]
            if not month_fields:
                logger.warning("CSV mensal sem coluna de competência, ignorado na consolidação: %s", path)
                continue
            month_key = month_fields[0]
            file_measure_keys = [
                key for key in normalized if any(token in key for token in ("quantidade", "qtd", "count"))
            ]
            if not file_measure_keys:
                logger.warning("CSV mensal sem coluna de quantidade, ignorado na consolidação: %s", path)
                continue

            file_dimension_keys = set(normalized) - {month_key, *file_measure_keys}
            layouts[path] = (encoding, delimiter, normalized, month_key)
            dimension_keys.update(file_dimension_keys)
            measure_keys.update(file_measure_keys)

    dimension_fields = sorted(dimension_keys)
    measure_fields = sorted(measure_keys)
    for path in paths:
        if path not in layouts:
            continue
        encoding, delimiter, normalized, month_key = layouts[path]
        fields_by_key = normalized
        with path.open("r", encoding=encoding, newline="") as source:
            reader = csv.DictReader(source, delimiter=delimiter)
            for row in reader:
                month = (row.get(fields_by_key[month_key]) or "").strip()
                dimensions = tuple(
                    (row.get(fields_by_key[key]) or "").strip() if key in fields_by_key else ""
                    for key in dimension_fields
                )
                quantities = tuple(
                    (row.get(fields_by_key[key]) or "").strip() if key in fields_by_key else ""
                    for key in measure_fields
                )
                if not month or not any(dimensions) or not any(quantities):
                    continue
                group = monthly_groups.setdefault(
                    dimensions,
                    {"records": 0, "months": {}},
                )
                group["records"] += 1
                month_totals = group["months"].setdefault(month, [Decimal(0) for _ in measure_fields])
                for index, value in enumerate(quantities):
                    if value:
                        try:
                            month_totals[index] += Decimal(value.replace(",", "."))
                        except InvalidOperation:
                            logger.warning("Quantidade não numérica em %s: %r", path.name, value)

    if not monthly_groups:
        return []

    blocks: List[CorpusBlock] = []
    lines: List[str] = []
    size = 0
    first_group = 1
    group_number = 0
    source_name = "SIA - produção ambulatorial"
    for dimensions, group in monthly_groups.items():
        group_number += 1
        dimension_text = "; ".join(
            f"{field.strip()}: {value}" for field, value in zip(dimension_fields, dimensions) if value
        )
        monthly_values = []
        for month, totals in sorted(group["months"].items()):
            for field, total in zip(measure_fields, totals):
                monthly_values.append(f"{month} {field.strip()}: {format(total.normalize(), 'f')}")
        body = f"{dimension_text}; série mensal: {', '.join(monthly_values)}; registros: {group['records']}"
        for line in _chunks(body, _CSV_CHUNK_CHARS):
            if lines and size + len(line) > _CSV_CHUNK_CHARS:
                header = f"[CSV] {source_name} (grupos {first_group}-{group_number - 1})"
                blocks.append(_make_block(header, "CSV", "\n".join(lines)))
                lines, size = [], 0
                first_group = group_number
            lines.append(line)
            size += len(line) + 1
    if lines:
        header = f"[CSV] {source_name} (grupos {first_group}-{group_number})"
        blocks.append(_make_block(header, "CSV", "\n".join(lines)))
    return blocks


class _HTMLTextParser(HTMLParser):
    _IGNORED = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: Sequence[tuple[str, Optional[str]]]) -> None:
        if tag in self._IGNORED:
            self._ignored_depth += 1
        elif not self._ignored_depth and tag in {"br", "div", "li", "p", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._IGNORED and self._ignored_depth:
            self._ignored_depth -= 1
        elif not self._ignored_depth and tag in {"br", "div", "li", "p", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def _plain_text_blocks(path: Path, raw: str, tag: str) -> List[CorpusBlock]:
    parsed = parse_corpus_text(raw, source_id=str(path))
    if parsed:
        return parsed
    text = "\n".join(line.strip() for line in raw.splitlines() if line.strip())
    return [
        _make_block(f"[{tag}] {path.stem[:100]} (trecho {index})", tag, chunk)
        for index, chunk in enumerate(_chunks(text), 1)
    ]


def _load_file(path: Path) -> List[CorpusBlock]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _csv_blocks(path)
    if suffix == ".json":
        return _json_blocks(path)
    if suffix in {".txt", ".md"}:
        return _plain_text_blocks(path, path.read_text(encoding=_text_encoding(path)), "TEXTO")
    if suffix in {".htm", ".html"}:
        parser = _HTMLTextParser()
        parser.feed(path.read_text(encoding=_text_encoding(path)))
        return _plain_text_blocks(path, "\n".join(parser.parts), "HTML")
    if suffix == ".pdf":
        from pypdf import PdfReader

        text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        return _plain_text_blocks(path, text, "PDF")
    return []


def load_corpus(paths: Iterable[Path]) -> List[CorpusBlock]:
    seen = set()
    out: List[CorpusBlock] = []
    path_list = sorted((path for path in paths if path.exists()), key=lambda path: str(path).casefold())
    grouped_sia: dict[Path, List[Path]] = {}
    regular_paths: List[Path] = []
    for path in path_list:
        if path.suffix.lower() == ".csv" and re.fullmatch(r"SIA\d{6}", path.stem, re.IGNORECASE):
            grouped_sia.setdefault(path.parent, []).append(path)
        else:
            regular_paths.append(path)

    file_groups = [(path,) for path in regular_paths]
    file_groups.extend(tuple(sia_paths) for sia_paths in grouped_sia.values())
    for file_group in file_groups:
        p = file_group[0]
        if not p.exists():
            continue
        try:
            blocks = _csv_series_blocks(file_group) if len(file_group) > 1 else _load_file(p)
        except Exception as error:
            logger.exception("Falha ao ler arquivo(s) de corpus: %s", ", ".join(str(item) for item in file_group))
            raise ValueError(f"Falha ao ler arquivo(s) de corpus: {', '.join(str(item) for item in file_group)}") from error
        for block in blocks:
            if block.id not in seen:
                seen.add(block.id)
                out.append(block)
    return out
