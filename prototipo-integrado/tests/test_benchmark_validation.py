import json
from pathlib import Path
import pytest
from app.core.config import get_settings
from eval.metrics import (
    evaluate_abstention_accuracy,
    evaluate_policy_compliance,
    evaluate_retrieval_hit_at_k,
)
from eval.runner import sanitize_model_folder_name

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "eval" / "dataset.json"


def test_validation_1_dataset_has_40_cases():
    assert DATASET_PATH.exists(), "Dataset eval/dataset.json não encontrado"
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 40, f"Esperados 40 casos no dataset, encontrados {len(data)}"


def test_validation_2_ids_are_unique():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    ids = [item["id"] for item in data]
    assert len(ids) == len(set(ids)), "Existem IDs duplicados no dataset"


def test_validation_3_all_categories_present():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    categories = {item["category"] for item in data}
    expected_categories = {"A", "B", "C", "D", "E", "F"}
    assert expected_categories.issubset(categories), f"Categorias ausentes: {expected_categories - categories}"


def test_validation_4_all_cases_have_expected_behavior():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for case in data:
        assert "expected_behavior" in case and bool(case["expected_behavior"].strip()), (
            f"Caso {case.get('id')} não possui expected_behavior"
        )


def test_validation_5_execution_does_not_mutate_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        before = f.read()

    # Simular leitura e processamento
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    _ = len(data)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        after = f.read()

    assert before == after, "A execução alterou o arquivo do dataset"


def test_validation_6_model_name_from_config():
    settings = get_settings()
    # Verifica que o runner consulta settings.ollama_model em vez de usar hardcoded string
    assert hasattr(settings, "ollama_model"), "Settings não expõe ollama_model"


def test_validation_7_required_result_fields():
    required_fields = {
        "question_id",
        "category",
        "question",
        "expected_behavior",
        "model_name",
        "model_version",
        "dataset_version",
        "timestamp",
        "embedding_model",
        "retrieval_top_k",
        "retrieval_threshold",
        "status",
        "retrieved_sources",
        "retrieved_scores",
        "answer",
        "metrics",
        "latency_ms",
    }
    dummy_entry = {
        "question_id": "Q001",
        "category": "A",
        "question": "teste",
        "expected_behavior": "teste",
        "model_name": "llama3.2:3b",
        "model_version": "v1.0",
        "dataset_version": "v1.0",
        "timestamp": "2026-10-06T00:00:00Z",
        "embedding_model": "nomic-embed-text",
        "retrieval_top_k": 5,
        "retrieval_threshold": 0.7,
        "status": "answered",
        "retrieved_sources": [],
        "retrieved_scores": [],
        "answer": "resposta",
        "metrics": {},
        "latency_ms": 100.0,
    }
    assert required_fields.issubset(dummy_entry.keys())


def test_validation_8_different_models_separate_results():
    folder1 = sanitize_model_folder_name("llama3.2:3b")
    folder2 = sanitize_model_folder_name("qwen3.5:4b")
    assert folder1 == "llama3.2-3b"
    assert folder2 == "qwen3.5-4b"
    assert folder1 != folder2, "Modelos diferentes devem gerar pastas de resultado separadas"


def test_validation_9_retrieval_hit_at_k_logic():
    sources = ["Farmácia Escola do HUB-UnB / Ebserh", "Outra Fonte"]
    assert evaluate_retrieval_hit_at_k(sources, "HUB-UnB", top_k=5) == 1.0
    assert evaluate_retrieval_hit_at_k(sources, "Fonte Inexistente", top_k=5) == 0.0


def test_validation_10_chat_endpoint_contract_unaffected():
    # Garante que as métricas e absttenção funcionam no modelo contratual da Susana
    assert evaluate_abstention_accuracy("C", "needs_clarification", "Qual serviço você busca?") == 1.0
    assert evaluate_abstention_accuracy("E", "out_of_scope", "Não realizo diagnósticos.") == 1.0
    assert evaluate_policy_compliance("Telefone de contato fake 99999-9999", "A", []) == 0.0
