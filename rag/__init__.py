from rag.config import (
    KNOWLEDGE_BASE_DIR,
    VECTOR_DB_DIR,
    INDEX_FILE,
    METADATA_FILE,
    EMBEDDING_MODEL_NAME
)
from rag.embeddings import get_embedding_model, embed_text, embed_texts
from rag.ingest import ingest_knowledge_base
from rag.retriever import (
    retrieve_relevant_chunks,
    retrieve_for_pollution_analysis,
    is_vectorstore_available,
    load_vectorstore,
    reload_vectorstore
)
from rag.generator import (
    generate_pollution_assessment,
    answer_environmental_question
)

__all__ = [
    "KNOWLEDGE_BASE_DIR",
    "VECTOR_DB_DIR",
    "INDEX_FILE",
    "METADATA_FILE",
    "EMBEDDING_MODEL_NAME",
    "get_embedding_model",
    "embed_text",
    "embed_texts",
    "ingest_knowledge_base",
    "retrieve_relevant_chunks",
    "retrieve_for_pollution_analysis",
    "is_vectorstore_available",
    "load_vectorstore",
    "reload_vectorstore",
    "generate_pollution_assessment",
    "answer_environmental_question"
]
