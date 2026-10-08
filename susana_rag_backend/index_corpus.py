"""Script standalone para indexar o corpus no Chroma."""
import logging
from app.config import get_settings
from app.rag.corpus import discover_corpus_files, load_corpus
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("indexer")

def main():
    settings = get_settings()
    logger.info("Carregando Embedder: %s", settings.embedding_model)
    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    
    logger.info("Conectando ao Chroma em %s", settings.chroma_dir)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    
    corpus_files = discover_corpus_files(
        [settings.docs_dir, settings.project_corpus_dir, settings.legacy_docs_file]
    )
    logger.info("Lendo %d arquivos de corpus...", len(corpus_files))
    blocks = load_corpus(corpus_files)
    
    logger.info("Indexando %d blocos. Isso pode demorar...", len(blocks))
    indexed = retriever.index(blocks)
    
    logger.info("Indexação concluída: %d blocos adicionados.", indexed)
    logger.info("Total no índice agora: %d blocos.", retriever.count())

if __name__ == "__main__":
    main()
