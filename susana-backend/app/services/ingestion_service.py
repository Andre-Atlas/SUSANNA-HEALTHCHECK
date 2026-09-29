import hashlib
import re


def clean_text(content: str) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    content = re.sub(r"[ \t]+", " ", content)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def make_chunks(content: str, chunk_size: int, overlap: int) -> list[str]:
    text = clean_text(content)
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_overlap deve ser >= 0 e menor que chunk_size.")
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
