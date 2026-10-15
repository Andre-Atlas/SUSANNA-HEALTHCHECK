import numpy as np

from app.ports import LLMAnswer, RetrievedChunk
from app.rag.pipeline import RAGPipeline


class FixedEmbedder:
    def encode_queries(self, texts):
        return np.array([[1.0, 0.0]], dtype=np.float32)


class FixedRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def search(self, query_vec, k, query_text):
        return self.chunks[:k]


class CitingLLM:
    def generate(self, question, contexts):
        return LLMAnswer("Fato apoiado pela segunda fonte [2]; referência inválida [99].", "test", 5)


def test_pipeline_returns_only_real_structured_citations():
    chunks = [
        RetrievedChunk("a", "context A", "Fonte A", 0.1, "https://example.test/a"),
        RetrievedChunk("b", "context B", "Fonte B", 0.2, "https://example.test/b"),
    ]
    pipeline = RAGPipeline(
        llm=CitingLLM(),
        embedder=FixedEmbedder(),
        retriever=FixedRetriever(chunks),
        mlflow_enabled=False,
    )

    result = pipeline.query("pergunta")

    assert result["citations"] == [
        {
            "ref": 2,
            "id": "b",
            "title": "Fonte B",
            "url": "https://example.test/b",
        }
    ]