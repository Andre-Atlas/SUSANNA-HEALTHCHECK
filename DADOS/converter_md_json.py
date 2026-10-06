#!/usr/bin/env python3
"""Convert DADOS Markdown sources to provenance-preserving, RAG-ready JSON."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MAX_CHUNK_CHARS = 1400
SCHEMA_VERSION = "1.0.0"
SOURCE_INFO = {
    "01_REME_DF_2025_Medicamentos": {
        "source_id": "sesdf-reme-df-2025",
        "source_url": "https://www.saude.df.gov.br/documents/d/saude/reme-df-2025-com-capa-ascom-versao-final-editada-pdf",
        "review_status": "pending",
        "ingestion_status": "blocked_for_automatic_import",
        "quality_notes": [
            "Transcricao com evidencias de erros de OCR e deslocamento em codigos e descricoes.",
            "Validar campos contra o PDF oficial antes de uso operacional ou clinico.",
            "Itens com colunas irregulares permanecem disponiveis somente como texto original.",
        ],
    },
    "02_HUB_Farmacia_Escola": {
        "source_id": "hub-farmacia-escola",
        "source_url": "https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-centro-oeste/hub-unb/saude/farmacia-escola",
        "review_status": "pending",
        "ingestion_status": "review_required",
        "quality_notes": [
            "Estoque e operacao sao temporarios; verificar a fonte oficial na data da consulta.",
            "Elencos e orientacoes clinicas nao estao aprovados para uso automatico.",
        ],
    },
    "03_Componente_Especializado_Alto_Custo": {
        "source_id": "sesdf-ceaf",
        "source_url": "https://www.saude.df.gov.br/componente-especializado",
        "review_status": "pending",
        "ingestion_status": "partial_review",
        "quality_notes": [
            "Requisitos, elegibilidade e abrangencia necessitam validacao por protocolo vigente.",
            "Avisos com prazo devem deixar de ser apresentados como atuais apos o vencimento.",
        ],
    },
    "04_Farmacias_Vivas_Fitoterapicos": {
        "source_id": "sesdf-farmacias-vivas",
        "source_url": "https://www.saude.df.gov.br/farmacias-vivas-fitoterapicos",
        "review_status": "pending",
        "ingestion_status": "partial_review",
        "quality_notes": [
            "Indicacoes terapeuticas e lista de UBS necessitam validacao em fontes oficiais especificas.",
            "Nao usar alegacoes clinicas como recomendacao individual.",
        ],
    },
    "dados": {
        "source_id": "projeto-guia-dados-assistencia-farmaceutica-df",
        "source_url": None,
        "review_status": "governance_document",
        "ingestion_status": "governance_only",
        "quality_notes": ["Documento de governanca; nao e fonte primaria de informacao clinica."],
    },
}


def stable_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def cells_from_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [cell.strip() for cell in cells]


def is_separator(line: str) -> bool:
    cells = cells_from_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def heading_context(headings: list[str]) -> str:
    return " > ".join(headings) if headings else "Documento"


def extract_reference_date(original: str) -> str | None:
    match = re.search(
        r"(?im)^.*?(?:Data de Última Verificação|Data de Referência|[ÚU]ltima auditoria documental).*?:\*{0,2}\s*\*{0,2}([^*\r\n]+)",
        original,
    )
    return match.group(1).strip() if match else None


def make_chunk(
    source_id: str,
    headings: list[str],
    content: str,
    start_line: int,
    end_line: int,
    kind: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    section = heading_context(headings)
    retrieval_text = f"Fonte: {source_id}\nSecao: {section}\n\n{content.strip()}"
    chunk = {
        "chunk_id": f"{source_id}:L{start_line}-L{end_line}",
        "text": retrieval_text,
        "content_original": content,
        "metadata": {
            "source_id": source_id,
            "section": section,
            "line_start": start_line,
            "line_end": end_line,
            "content_type": kind,
        },
    }
    if extra:
        chunk["metadata"].update(extra)
    return chunk


def parse_document(path: Path) -> dict[str, Any]:
    stem = path.stem
    info = SOURCE_INFO[stem]
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)
    headings: list[str] = []
    chunks: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    paragraph: list[tuple[int, str]] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        group: list[tuple[int, str]] = []
        group_chars = 0
        for line_number, text in paragraph:
            if group and group_chars + len(text) > MAX_CHUNK_CHARS:
                content = "".join(value for _, value in group)
                chunks.append(make_chunk(info["source_id"], headings, content, group[0][0], group[-1][0], "text"))
                group = []
                group_chars = 0
            group.append((line_number, text))
            group_chars += len(text)
        if group:
            content = "".join(value for _, value in group)
            chunks.append(make_chunk(info["source_id"], headings, content, group[0][0], group[-1][0], "text"))
        paragraph = []

    index = 0
    while index < len(lines):
        line = lines[index]
        line_number = index + 1
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line.rstrip("\r\n"))
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            headings = headings[: level - 1]
            headings.append(heading_match.group(2).strip())
            index += 1
            continue

        if line.lstrip().startswith("|"):
            flush_paragraph()
            table_lines: list[tuple[int, str]] = []
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                table_lines.append((index + 1, lines[index]))
                index += 1
            header_line = next((entry for entry in table_lines if not is_separator(entry[1])), None)
            headers = cells_from_row(header_line[1]) if header_line else []
            table_id = f"{info['source_id']}:table:L{table_lines[0][0]}"
            for row_line_number, row_text in table_lines:
                if is_separator(row_text) or (header_line and row_line_number == header_line[0]):
                    continue
                cells = cells_from_row(row_text)
                is_valid = bool(headers) and len(cells) == len(headers)
                row_record = {
                    "record_id": f"{table_id}:L{row_line_number}",
                    "source_id": info["source_id"],
                    "section": heading_context(headings),
                    "table_id": table_id,
                    "line_start": row_line_number,
                    "line_end": row_line_number,
                    "raw_row": row_text.rstrip("\r\n"),
                    "headers_original": headers,
                    "cells_original": cells,
                    "parse_status": "columns_aligned_unverified" if is_valid else "missing_header_or_column_count_mismatch",
                    "review_status": "pending",
                    "validation_status": "not_validated_against_authoritative_source",
                    "fields_original": dict(zip(headers, cells)) if is_valid else None,
                }
                records.append(row_record)
                table_context = "Cabecalhos da tabela: " + " | ".join(headers) + "\nLinha da tabela: " + row_text.rstrip("\r\n")
                chunk = make_chunk(
                    info["source_id"], headings, table_context, row_line_number, row_line_number, "table_row",
                    {"record_id": row_record["record_id"], "table_id": table_id, "parse_status": row_record["parse_status"]},
                )
                chunks.append(chunk)
            continue

        if line.strip():
            paragraph.append((line_number, line))
        else:
            flush_paragraph()
        index += 1
    flush_paragraph()

    title_match = re.search(r"^#\s+(.+)$", original, re.MULTILINE)
    document = {
        "schema_version": SCHEMA_VERSION,
        "document": {
            "source_id": info["source_id"],
            "source_title": title_match.group(1).strip() if title_match else path.stem,
            "source_file": path.name,
            "source_url": info["source_url"],
            "source_version": "REME-DF 2025" if stem.startswith("01_") else None,
            "captured_at": None,
            "reference_date_original": extract_reference_date(original),
            "review_status": info["review_status"],
            "ingestion_status": info["ingestion_status"],
            "quality_notes": info["quality_notes"],
            "language": "pt-BR",
            "original_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
            "original_line_count": len(lines),
        },
        "original_markdown": original,
        "records": records,
        "chunks": chunks,
    }
    return document


def main() -> None:
    source_paths = [ROOT / f"{stem}.md" for stem in SOURCE_INFO]
    converted: list[tuple[Path, dict[str, Any]]] = []
    for source_path in source_paths:
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        converted.append((source_path, parse_document(source_path)))

    for source_path, document in converted:
        output_path = source_path.with_suffix(".json")
        serialized = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
        validated = json.loads(serialized)
        if validated["original_markdown"] != source_path.read_text(encoding="utf-8"):
            raise ValueError(f"Original source was not preserved: {source_path.name}")
        if not validated["chunks"]:
            raise ValueError(f"No RAG chunks were generated: {source_path.name}")
        output_path.write_text(serialized, encoding="utf-8")
        aligned_rows = sum(record["parse_status"] == "columns_aligned_unverified" for record in document["records"])
        irregular_rows = len(document["records"]) - aligned_rows
        print(
            f"{output_path.name}: {len(document['chunks'])} chunks, "
            f"{aligned_rows} structurally aligned (unverified) table rows, "
            f"{irregular_rows} irregular rows; JSON valid"
        )


if __name__ == "__main__":
    main()
