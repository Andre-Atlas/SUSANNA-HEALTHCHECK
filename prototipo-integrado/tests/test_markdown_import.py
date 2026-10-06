from pathlib import Path

from scripts.ingest_markdown_directory import load_approved_documents


def test_markdown_manifest_only_selects_approved_documents():
    manifest_path = Path(__file__).resolve().parents[2] / "DADOS" / "manifest.json"

    approved, skipped = load_approved_documents(manifest_path)

    assert [item.filename for item in approved] == ["02_HUB_Farmacia_Escola.md"]
    assert {filename for filename, _reason in skipped} == {
        "01_REME_DF_2025_Medicamentos.md",
        "03_Componente_Especializado_Alto_Custo.md",
        "04_Farmacias_Vivas_Fitoterapicos.md",
    }
    assert approved[0].source_url.startswith("https://www.gov.br/")