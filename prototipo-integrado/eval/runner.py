import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para import de app
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.providers.ollama import OllamaProvider
from app.schemas.chat import ChatContext
from app.services.chat_service import ChatService
from eval.metrics import (
    evaluate_abstention_accuracy,
    evaluate_conversational_context,
    evaluate_llm_metrics,
    evaluate_policy_compliance,
    evaluate_retrieval_hit_at_k,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eval_runner")


def sanitize_model_folder_name(model_name: str) -> str:
    """Converte 'llama3.2:3b' em 'llama3.2-3b'."""
    return model_name.replace(":", "-").replace("/", "_")


async def run_benchmark(dataset_path: str = "eval/dataset.json", results_dir: str = "eval/results") -> Path:
    settings = get_settings()
    model_name = settings.ollama_model
    if not model_name:
        raise ValueError("OLLAMA_MODEL não está configurado no ambiente/.env!")

    dataset_file = BASE_DIR / dataset_path
    if not dataset_file.exists():
        raise FileNotFoundError(f"Dataset não encontrado em: {dataset_file}")

    with open(dataset_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    logger.info("Iniciando Benchmark da Susana")
    logger.info("Modelo LLM: %s", model_name)
    logger.info("Modelo Embedding: %s", settings.embedding_model)
    logger.info("Total de casos no dataset: %d", len(dataset))

    ollama_provider = OllamaProvider()

    results: list[dict] = []
    category_summary: dict[str, dict] = {}

    async with SessionLocal() as db:
        chat_service = ChatService(db=db, llm=ollama_provider, embeddings=ollama_provider)

        for case in dataset:
            question_id = case["id"]
            category = case["category"]
            question = case["question"]
            expected_behavior = case["expected_behavior"]
            expected_source = case.get("expected_source")
            required_facts = case.get("required_facts") or []
            turns = case.get("turns")
            context_data = case.get("context")

            session_id = str(uuid.uuid4())
            chat_service.clear_session(session_id)

            # Para casos com histórico conversacional (Categoria F)
            if turns and len(turns) > 1:
                for turn in turns[:-1]:
                    user_msg = turn["user"]
                    context_obj = ChatContext(**context_data) if context_data else None
                    await chat_service.process(session_id, user_msg, context_obj)

            context_obj = ChatContext(**context_data) if context_data else None

            start_time = time.perf_counter()
            response = await chat_service.process(session_id, question, context_obj)
            end_time = time.perf_counter()

            latency_ms = round((end_time - start_time) * 1000, 2)

            retrieved_sources = [s.source for s in response.sources] if response.sources else []
            retrieved_scores = [e.score for e in response.evidence] if response.evidence else []
            evidence_texts = "\n".join([e.content for e in response.evidence]) if response.evidence else ""

            # Cálculo de Métricas
            hit_at_k = evaluate_retrieval_hit_at_k(retrieved_sources, expected_source, top_k=settings.rag_top_k)
            abstention_acc = evaluate_abstention_accuracy(category, response.status, response.reply)
            policy_comp = evaluate_policy_compliance(response.reply, category, retrieved_sources)
            context_acc = evaluate_conversational_context(category, response.reply, context_data)

            llm_metrics = await evaluate_llm_metrics(
                question=question,
                evidence_text=evidence_texts,
                answer=response.reply,
                expected_behavior=expected_behavior,
                required_facts=required_facts,
                judge_llm=None,  # Pode ser configurado para LLM Judge isolada
            )

            metrics = {
                "hit_at_k": hit_at_k,
                "faithfulness": llm_metrics["faithfulness"],
                "correctness": llm_metrics["correctness"],
                "relevance": llm_metrics["relevance"],
                "abstention_accuracy": abstention_acc,
                "policy_compliance": policy_comp,
                "conversational_context": context_acc,
                "judge_type": llm_metrics["judge_type"],
            }

            result_entry = {
                "question_id": question_id,
                "category": category,
                "question": question,
                "expected_behavior": expected_behavior,
                "expected_source": expected_source,
                "model_name": model_name,
                "model_version": "v1.0",
                "dataset_version": "v1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "embedding_model": settings.embedding_model,
                "retrieval_top_k": settings.rag_top_k,
                "retrieval_threshold": settings.rag_similarity_threshold,
                "system_prompt_version": "1.0",
                "temperature": None,
                "status": response.status,
                "retrieved_sources": retrieved_sources,
                "retrieved_scores": retrieved_scores,
                "answer": response.reply,
                "metrics": metrics,
                "latency_ms": latency_ms,
            }

            results.append(result_entry)
            logger.info("[%s] Cat %s | Latência: %.1f ms | Status: %s", question_id, category, latency_ms, response.status)

    # Organizar e Salvar Resultados
    model_folder_name = sanitize_model_folder_name(model_name)
    output_dir = BASE_DIR / results_dir / model_folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / "results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Calcular Médias
    total_cases = len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_hit_k = sum(r["metrics"]["hit_at_k"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_faithfulness = sum(r["metrics"]["faithfulness"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_correctness = sum(r["metrics"]["correctness"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_relevance = sum(r["metrics"]["relevance"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_abstention = sum(r["metrics"]["abstention_accuracy"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_policy = sum(r["metrics"]["policy_compliance"] for r in results) / total_cases if total_cases > 0 else 0.0
    avg_context = sum(r["metrics"]["conversational_context"] for r in results) / total_cases if total_cases > 0 else 0.0

    summary = {
        "model_name": model_name,
        "dataset_version": "v1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cases": total_cases,
        "metrics_summary": {
            "hit_at_k": round(avg_hit_k, 4),
            "faithfulness": round(avg_faithfulness, 4),
            "correctness": round(avg_correctness, 4),
            "relevance": round(avg_relevance, 4),
            "abstention_accuracy": round(avg_abstention, 4),
            "policy_compliance": round(avg_policy, 4),
            "conversational_context": round(avg_context, 4),
            "avg_latency_ms": round(avg_latency, 2),
        },
    }

    summary_file = output_dir / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    logger.info("Benchmark concluído com sucesso!")
    logger.info("Resultados salvos em: %s", output_dir)

    return output_dir


if __name__ == "__main__":
    asyncio.run(run_benchmark())
