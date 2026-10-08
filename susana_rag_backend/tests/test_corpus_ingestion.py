import json
from pathlib import Path

from app.rag.corpus import discover_corpus_files, load_corpus


def test_discovers_supported_files_recursively(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "notes.txt").write_text("[SERVICO] Teste\nAtendimento administrativo.", encoding="utf-8")
    (nested / "units.csv").write_text("Unidade;Região\nUBS 1;Central\n", encoding="utf-8")
    (nested / "ignored.bin").write_bytes(b"ignored")

    files = discover_corpus_files([tmp_path])

    assert [path.name for path in files] == ["units.csv", "notes.txt"]


def test_deduplicates_repeated_csv_rows_without_losing_multiplicity(tmp_path):
    path = tmp_path / "units.csv"
    path.write_text(
        "Unidade;Região\nUBS 1;Central\nUBS 1;Central\n",
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "registros: 2" in blocks[0].text


def test_groups_csv_measure_values_by_dimensions(tmp_path):
    path = tmp_path / "production.csv"
    path.write_text(
        "ano_mes;estabelecimento;procedimento;quantidade\n"
        "202201;Hospital Regional;Consulta;8\n"
        "202201;Hospital Regional;Consulta;10\n",
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "Hospital Regional" in blocks[0].text
    assert "Consulta" in blocks[0].text
    assert "quantidade total: 18" in blocks[0].text
    assert "registros: 2" in blocks[0].text


def test_loads_csv_rows_as_searchable_records(tmp_path):
    path = tmp_path / "hospitais.csv"
    path.write_text(
        "Estabelecimento;Endereço;Região\nHospital Regional;Área Especial;Central\n",
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "Hospital Regional" in blocks[0].text
    assert "Endereço: Área Especial" in blocks[0].text
    assert "Região: Central" in blocks[0].text
    assert "hospitais.csv" in blocks[0].header


def test_csv_delimiter_comes_from_header_not_commas_in_values(tmp_path):
    path = tmp_path / "services.csv"
    path.write_text(
        "Unidade;Serviços;Região\nUBS 1;Consulta, vacinação e farmácia;Central\n",
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "Consulta, vacinação e farmácia" in blocks[0].text
    assert "Região: Central" in blocks[0].text


def test_small_directory_csv_keeps_each_entity_in_a_separate_chunk():
    path = Path(__file__).resolve().parents[2] / "CORPUS" / "Arquivos" / "Hospitais.csv"

    blocks = load_corpus([path])

    assert len(blocks) > 1
    assert all(block.text.count("Estabelecimento:") == 1 for block in blocks)


def test_consolidates_monthly_sia_csvs_preserving_month_values(tmp_path):
    source_dir = tmp_path / "atendimentos-e-consultas"
    source_dir.mkdir()
    header = "ano_mes;estabelecimento_cnes;procedimento;quantidade\n"
    (source_dir / "SIA012017.csv").write_text(
        header + "201701;Hospital Regional;Consulta;8\n", encoding="utf-8"
    )
    (source_dir / "SIA022017.csv").write_text(
        "ano_mes;cod_estabelecimento_cnes;estabelecimento_cnes;complexidade;procedimento;quantidade\n"
        '201702;123;Hospital Regional;Média;"Consulta, especializada";10\n',
        encoding="utf-8",
    )

    blocks = load_corpus([source_dir / "SIA012017.csv", source_dir / "SIA022017.csv"])

    assert len(blocks) == 1
    assert "Hospital Regional" in blocks[0].text
    assert "Consulta" in blocks[0].text
    assert "especializada" in blocks[0].text
    assert "cod_estabelecimento_cnes: 123" in blocks[0].text
    assert "201701" in blocks[0].text and "8" in blocks[0].text
    assert "201702" in blocks[0].text and "10" in blocks[0].text


def test_loads_structured_json_faq_and_preserves_source(tmp_path):
    path = tmp_path / "faq.json"
    path.write_text(
        json.dumps(
            {
                "documento": {"titulo": "FAQ SUS"},
                "documentos": [
                    {
                        "pergunta": "Onde fica a UBS?",
                        "resposta": "Na região Central.",
                        "texto_indexacao": "UBS região Central",
                        "fontes": ["https://saude.df.gov.br/ubs"],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "Onde fica a UBS?" in blocks[0].text
    assert "Na região Central." in blocks[0].text
    assert "https://saude.df.gov.br/ubs" in (blocks[0].url or "")


def test_loads_chunked_document_json(tmp_path):
    path = tmp_path / "document.json"
    path.write_text(
        json.dumps(
            {
                "document": {
                    "source_title": "Unidades de saúde",
                    "source_url": "https://saude.df.gov.br/unidades",
                },
                "chunks": [
                    {"text": "Hospital Regional de Ceilândia", "metadata": {"section": "Hospitais"}}
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "Hospital Regional de Ceilândia" in blocks[0].text
    assert "Hospitais" in blocks[0].text
    assert blocks[0].url == "https://saude.df.gov.br/unidades"


def test_loads_metadata_and_nested_content_json(tmp_path):
    path = tmp_path / "page.json"
    path.write_text(
        json.dumps(
            {
                "metadata": {"titulo": "Atendimento de urgência", "url": "https://saude.df.gov.br/urgencia"},
                "conteudo": {"titulo_principal": "UPAs", "secoes": [{"titulo": "Horário", "texto": "Atendimento 24 horas."}]},
                "extracao": {"hash_conteudo": "not user-facing"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert "Atendimento 24 horas." in blocks[0].text
    assert "not user-facing" not in blocks[0].text
    assert blocks[0].url == "https://saude.df.gov.br/urgencia"


def test_loads_existing_tagged_text_without_losing_source_url(tmp_path):
    path = tmp_path / "services.txt"
    path.write_text(
        "[SERVICO] Farmácia\nRetirada de medicamentos.\nFonte: https://saude.df.gov.br/farmacia\n",
        encoding="utf-8",
    )

    blocks = load_corpus([path])

    assert len(blocks) == 1
    assert blocks[0].tag == "SERVICO"
    assert blocks[0].url == "https://saude.df.gov.br/farmacia"


def test_fails_closed_when_a_corpus_file_cannot_be_read(tmp_path):
    malformed_json = tmp_path / "broken.json"
    malformed_json.write_text("{invalid json", encoding="utf-8")

    try:
        load_corpus([malformed_json])
    except ValueError as error:
        assert "broken.json" in str(error)
    else:
        raise AssertionError("invalid corpus file must stop indexing")


def test_loads_html_and_pdf_text(tmp_path):
    html_path = tmp_path / "data_dictionary.html"
    html_path.write_bytes(
        "<html><script>ignore me</script><h1>Atendimentos</h1><p>Dados ambulatoriais: Região Central.</p></html>".encode(
            "iso-8859-1"
        )
    )
    pdf_path = (
        Path(__file__).resolve().parents[2]
        / "CORPUS"
        / "atendimentos-e-consultas"
        / "Atendimentos e Consultas - Metadados _Até 2018_.pdf"
    )

    html_blocks = load_corpus([html_path])
    pdf_blocks = load_corpus([pdf_path])

    assert "Atendimentos" in " ".join(block.text for block in html_blocks)
    assert "ignore me" not in " ".join(block.text for block in html_blocks)
    assert "Região Central" in " ".join(block.text for block in html_blocks)
    assert pdf_blocks