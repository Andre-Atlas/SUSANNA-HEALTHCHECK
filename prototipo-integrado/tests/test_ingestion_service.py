from app.services.ingestion_service import make_chunks, sha256_text


def test_chunking_and_hash():
    chunks = make_chunks("a" * 100, chunk_size=40, overlap=5)
    assert chunks
    assert len(sha256_text("abc")) == 64
