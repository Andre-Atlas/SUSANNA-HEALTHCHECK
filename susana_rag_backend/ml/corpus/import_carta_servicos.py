#!/usr/bin/env python3
"""Converte a Carta de Serviços ao Cidadão 2026 (SES-DF), extraída do PDF oficial na branch `docs`
(EDA`s/EDAcartilha), num arquivo indexável em CORPUS/Arquivos/.

Entrada:  CORPUS/nao_indexado/carta_servicos_2026_secoes.jsonl  (uma seção por linha; mantida como origem)
Saída:    CORPUS/Arquivos/carta_servicos_sesdf_2026.json         (esquema "chunks", lido por app/rag/corpus.py)

Uso: python ml/corpus/import_carta_servicos.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "CORPUS" / "nao_indexado" / "carta_servicos_2026_secoes.jsonl"
OUT = ROOT / "CORPUS" / "Arquivos" / "carta_servicos_sesdf_2026.json"
# Página onde a SES-DF publica a Carta de Serviços (o PDF original não tem URL estável no extrato)
SOURCE_URL = "https://www.saude.df.gov.br/carta-de-servicos"
# Correções de rótulo da extração da EDA (conferidas lendo o texto de cada seção e a ordem do sumário):
# - p. 7: rotulada "Atendimento em UPAs", mas descreve o e-Protocolo e a Ouvidoria;
# - p. 14: rotulada "Centros Especializados", mas vai até a p. 23 e cobre também Saúde Mental (CAPS),
#   SAMU-DF 192, UPAs e Hospitais (ordem do sumário da Carta).
SERVICE_FIXES = {
    7: "e-Protocolo e Ouvidoria",
    14: "Centros Especializados, Saúde Mental (CAPS), SAMU-DF 192, UPAs e Hospitais",
}


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)          # marcadores da extração do PDF
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?u>", "", text, flags=re.I)                 # sublinhado
    text = re.sub(r"\*\*|__", "", text)                           # negrito markdown
    text = re.sub(r"^\s*[-•]\s*", "- ", text, flags=re.M)         # marcadores de lista uniformes
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def main() -> int:
    sections = [json.loads(line) for line in SRC.read_text(encoding="utf-8").splitlines() if line.strip()]
    chunks = []
    starts = [x.get("pagina") for x in sections]
    for pos, s in enumerate(sections):
        if s.get("tipo") == "capa_sumario":                      # capa/sumário: só títulos
            continue
        body = clean(s.get("texto") or "")
        if len(body) < 80:
            continue
        service = SERVICE_FIXES.get(s.get("pagina")) or s.get("servico") or s.get("titulo")
        start = s.get("pagina")
        end = (starts[pos + 1] - 1) if pos + 1 < len(starts) else start
        pages = f"p. {start}" if end == start else f"p. {start}–{end}"
        chunks.append({"text": body, "metadata": {"servico": service, "pagina": pages}})
    doc = {"document": {"source_title": "Carta de Serviços ao Cidadão 2026 — SES-DF", "url": SOURCE_URL,
                        "origem": "PDF oficial extraído na branch docs (EDA`s/EDAcartilha)"},
           "chunks": chunks}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(chunks)} seções gravadas em {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
