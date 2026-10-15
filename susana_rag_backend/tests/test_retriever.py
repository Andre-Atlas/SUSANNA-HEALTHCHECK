import numpy as np

from app.rag.corpus import CorpusBlock
from app.rag.retriever import ChromaRetriever, is_relevant
from app.ports import RetrievedChunk


class FixedEmbedder:
    slug = "test"

    def encode_passages(self, texts):
        return np.tile(np.array([[1.0, 0.0]], dtype=np.float32), (len(texts), 1))


def test_index_removes_documents_missing_from_current_corpus(tmp_path):
    retriever = ChromaRetriever(FixedEmbedder(), tmp_path / "chroma")
    old_block = CorpusBlock("old", "[CSV] old", "CSV", "old document", None)
    new_block = CorpusBlock("new", "[CSV] new", "CSV", "new document", None)

    assert retriever.index([old_block]) == 1
    assert retriever.index([new_block]) == 1

    assert retriever.count() == 1
    assert retriever.search(np.array([1.0, 0.0], dtype=np.float32), k=1)[0].text == "new document"


def test_search_reranks_exact_entity_terms_ahead_of_similar_names(tmp_path):
    retriever = ChromaRetriever(FixedEmbedder(), tmp_path / "chroma")
    retriever.index(
        [
            CorpusBlock("taguatinga", "[CSV] hospitals", "CSV", "Hospital Regional de Taguatinga", None),
            CorpusBlock("ceilandia", "[CSV] hospitals", "CSV", "Hospital Regional de Ceilandia", None),
            CorpusBlock("gama", "[CSV] hospitals", "CSV", "Hospital Regional do Gama", None),
        ]
    )

    results = retriever.search(np.array([1.0, 0.0], dtype=np.float32), k=1, query_text="Hospital Regional de Ceilândia")

    assert results[0].id == "ceilandia"


def test_search_keeps_single_digit_unit_identifier(tmp_path):
    retriever = ChromaRetriever(FixedEmbedder(), tmp_path / "chroma")
    retriever.index(
        [
            CorpusBlock("ubs-4", "[CSV] units", "CSV", "Horário UBS 4 Paranoá", None),
            CorpusBlock("ubs-1", "[CSV] units", "CSV", "Horário UBS 1 Paranoá", None),
        ]
    )

    results = retriever.search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=1,
        query_text="Qual o horário da UBS 1 do Paranoá?",
    )

    assert results[0].id == "ubs-1"


def test_search_ignores_record_count_when_matching_unit_number(tmp_path):
    retriever = ChromaRetriever(FixedEmbedder(), tmp_path / "chroma")
    retriever.index(
        [
            CorpusBlock("ubs-4", "[CSV] units", "CSV", "UBS 4 Paranoá; Horário: 07:00; registros: 1", None),
            CorpusBlock("ubs-1", "[CSV] units", "CSV", "UBS 1 Paranoá; Horário: 22:00; registros: 1", None),
        ]
    )

    results = retriever.search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=1,
        query_text="Qual horário da UBS 1 do Paranoá?",
    )

    assert results[0].id == "ubs-1"


def test_search_prefers_unit_number_in_name_over_same_number_in_address(tmp_path):
    retriever = ChromaRetriever(FixedEmbedder(), tmp_path / "chroma")
    retriever.index(
        [
            CorpusBlock(
                "ubs-4",
                "[CSV] units",
                "CSV",
                "Estabelecimento: UBS 04 RIACHO FUNDO II; Endereço: AREA ESPECIAL 01; registros: 1",
                None,
            ),
            CorpusBlock(
                "ubs-1",
                "[CSV] units",
                "CSV",
                "Estabelecimento: UBS 01 RIACHO FUNDO II; Endereço: AREA ESPECIAL 01; registros: 1",
                None,
            ),
        ]
    )

    results = retriever.search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=1,
        query_text="Onde fica UBS 01 Riacho Fundo II?",
    )

    assert results[0].id == "ubs-1"


def test_search_reranks_exact_entity_outside_initial_vector_candidates(tmp_path):
    retriever = ChromaRetriever(FixedEmbedder(), tmp_path / "chroma")
    blocks = [
        CorpusBlock(f"other-{index}", "[CSV] units", "CSV", f"UBS {index + 2} Planaltina", None)
        for index in range(39)
    ]
    blocks.append(CorpusBlock("paranoa-ubs-1", "[CSV] units", "CSV", "UBS 1 Paranoá", None))
    retriever.index(blocks)

    results = retriever.search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=1,
        query_text="Horário UBS 1 Paranoá",
    )

    assert results[0].id == "paranoa-ubs-1"


def test_search_finds_numbered_entity_beyond_vector_candidate_limit(tmp_path):
    class DistractorEmbedder(FixedEmbedder):
        def encode_passages(self, texts):
            return np.array(
                [[0.0, 1.0] if "UBS 1 Paranoá" in text else [1.0, 0.0] for text in texts],
                dtype=np.float32,
            )

    retriever = ChromaRetriever(DistractorEmbedder(), tmp_path / "chroma")
    blocks = [
        CorpusBlock(f"other-{index}", "[CSV] units", "CSV", f"UBS {index + 2} Planaltina", None)
        for index in range(400)
    ]
    blocks.append(CorpusBlock("paranoa-ubs-1", "[CSV] units", "CSV", "UBS 1 Paranoá", None))
    retriever.index(blocks)

    results = retriever.search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=1,
        query_text="Horário da UBS 1 do Paranoá",
    )

    assert results[0].id == "paranoa-ubs-1"


def test_search_finds_named_entity_beyond_vector_candidate_limit(tmp_path):
    class DistractorEmbedder(FixedEmbedder):
        def encode_passages(self, texts):
            return np.array(
                [[0.0, 1.0] if "CEPAV - PRIMAVERA" in text else [1.0, 0.0] for text in texts],
                dtype=np.float32,
            )

    retriever = ChromaRetriever(DistractorEmbedder(), tmp_path / "chroma")
    blocks = [
        CorpusBlock(f"other-{index}", "[CSV] centers", "CSV", f"CEPAV - NÚCLEO {index}", None)
        for index in range(400)
    ]
    blocks.append(CorpusBlock("cepav-primavera", "[CSV] centers", "CSV", "CEPAV - PRIMAVERA", None))
    retriever.index(blocks)

    results = retriever.search(
        np.array([1.0, 0.0], dtype=np.float32),
        k=1,
        query_text="Onde fica o CEPAV - PRIMAVERA?",
    )

    assert results[0].id == "cepav-primavera"


def test_exact_entity_match_can_pass_distance_threshold():
    result = RetrievedChunk(
        id="ubs-1",
        text="Estabelecimento: UBS 1 - PARANOA; Horário: De Segunda a Sexta das 07:00 às 22:00",
        source="UBS CSV",
        distance=0.63,
    )

    assert is_relevant([result], "Qual é o horário de funcionamento da UBS 1 do Paranoá?", 0.55)


def test_unit_match_ignores_interrogative_words():
    result = RetrievedChunk(
        id="candangolandia",
        text="Estabelecimento: UBS 01 CANDANGOLANDIA; Horário: De Segunda a Sexta das 07:00 às 19:00 e Sábado das 07:00 às 12:00",
        source="UBS CSV",
        distance=0.575,
    )

    assert is_relevant(
        [result],
        "A UBS 01 de Candangolândia abre aos sábados e até que horas?",
        0.55,
    )


def test_unrelated_context_still_fails_relevance_threshold():
    result = RetrievedChunk(
        id="ceaf",
        text="Farmácia CEAF: Estação 102 Sul do Metrô, Brasília; horário administrativo do serviço.",
        source="CEAF JSON",
        distance=0.701,
    )

    assert not is_relevant([result], "Qual o horário do metrô de Brasília?", 0.55)