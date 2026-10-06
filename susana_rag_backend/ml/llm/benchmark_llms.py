#!/usr/bin/env python3
"""
Benchmark Automatizado de LLMs para RAG Local.
Alinhado com mle-workflow e ml-adoption-playbook.

Métricas coletadas:
- Observabilidade Operacional: Latência (TTFT/Total), TPS (Throughput).
- Observabilidade de Dados/Modelo: Groundedness (Fidelidade ao contexto).
- Taxa de Erro: Falhas de OOM ou Timeouts.
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path

import mlflow

from app.config import get_settings
from app.llm.ollama_adapter import OllamaAdapter
from app.ports import RetrievedChunk

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("susana.llm.benchmark")

ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = ROOT / "ml" / "llm" / "benchmark_dataset.json"

MODELS_TO_TEST = [
    "qwen2.5:7b",
    "llama3.1",
    "mistral",
    "phi3.5",
    "qwen2.5:3b",
    "gemma2",
]


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_groundedness(response_text: str, expected: list[str], forbidden: list[str]) -> float:
    """Calcula penalidades e bônus baseado em palavras-chave."""
    text_lower = response_text.lower()
    score = 1.0

    # Penaliza se não contiver informações obrigatórias do contexto
    for kw in expected:
        if kw.lower() not in text_lower:
            score -= (1.0 / len(expected)) * 0.5  # Penaliza até 50%

    # Penaliza fortemente alucinações clínicas (concept drift / groundedness failure)
    for kw in forbidden:
        if kw.lower() in text_lower:
            score -= 0.5  # Penalidade grave por alucinação clínica

    return max(0.0, min(1.0, score))


def pull_model(model_name: str) -> bool:
    logger.info("Executando: ollama pull %s", model_name)
    try:
        subprocess.run(["ollama", "pull", model_name], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Falha ao baixar %s: %s", model_name, e.stderr)
        return False
    except FileNotFoundError:
        logger.error("Ollama CLI não encontrado no PATH.")
        return False


def main():
    settings = get_settings()
    os.makedirs(settings.mlflow_artifact_root, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("susana-llm-benchmark")

    dataset = load_dataset()
    logger.info("Dataset carregado com %d cenários.", len(dataset))

    for model_name in MODELS_TO_TEST:
        logger.info("--- Iniciando Benchmark: %s ---", model_name)
        
        # 1. Pipeline Execution / CI-CD Simulation: Pull model
        t_pull_start = time.time()
        success = pull_model(model_name)
        pull_duration = time.time() - t_pull_start
        
        if not success:
            logger.warning("Pulando %s devido a erro de pull.", model_name)
            with mlflow.start_run(run_name=model_name):
                mlflow.log_param("model", model_name)
                mlflow.log_metric("error_rate", 1.0)
            continue

        adapter = OllamaAdapter(
            base_url=settings.ollama_base_url,
            model=model_name,
            timeout_s=45.0, # Timeout maior para modelos grandes
        )

        # Warm-up para evitar penalizar a 1ª requisição na métrica de latência
        adapter.warm_up()

        total_latency = 0
        total_tokens = 0
        total_groundedness = 0.0
        errors = 0

        with mlflow.start_run(run_name=model_name):
            mlflow.log_param("model", model_name)
            mlflow.log_metric("pull_duration_s", pull_duration)

            for idx, item in enumerate(dataset):
                q = item["question"]
                ctx = [RetrievedChunk(id=str(idx), text=item["context"], source="mock", distance=0.1)]
                
                try:
                    # 2. Infra Observability: Medindo latência
                    answer = adapter.generate(q, ctx)
                    
                    # 3. LLMOps: Tokens & TPS
                    # Aproximação simples: 1 token ~= 4 chars para PT-BR
                    estimated_tokens = len(answer.text) / 4.0
                    tps = estimated_tokens / (answer.latency_ms / 1000.0)
                    
                    # 4. Data/Model Observability: Groundedness
                    grounded_score = calculate_groundedness(
                        answer.text, 
                        item["expected_keywords"], 
                        item["forbidden_keywords"]
                    )

                    total_latency += answer.latency_ms
                    total_tokens += estimated_tokens
                    total_groundedness += grounded_score

                    logger.info("[%s] Q%d: TPS=%.1f | Groundedness=%.2f", model_name, idx, tps, grounded_score)

                except Exception as e:
                    logger.error("[%s] Erro na Q%d: %s", model_name, idx, e)
                    errors += 1

            # Compilação de Métricas Agregadas
            valid_runs = len(dataset) - errors
            if valid_runs > 0:
                avg_latency_s = (total_latency / valid_runs) / 1000.0
                avg_tps = total_tokens / (total_latency / 1000.0) if total_latency > 0 else 0
                avg_groundedness = total_groundedness / valid_runs
                error_rate = errors / len(dataset)

                mlflow.log_metric("avg_latency_s", avg_latency_s)
                mlflow.log_metric("avg_tps", avg_tps)
                mlflow.log_metric("groundedness", avg_groundedness)
                mlflow.log_metric("error_rate", error_rate)
                
                logger.info("=> %s FINAL: TPS=%.1f | Groundedness=%.2f | Errors=%.1f%%", 
                            model_name, avg_tps, avg_groundedness, error_rate * 100)
            else:
                mlflow.log_metric("error_rate", 1.0)
                logger.error("=> %s FALHOU EM TODAS AS REQUISIÇÕES.", model_name)

if __name__ == "__main__":
    main()
