from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from rag.config import EMBEDDING_MODEL_NAME

_EMBEDDING_MODEL: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Load and cache the SentenceTransformer embedding model."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        print(f"[RAG] Loading SentenceTransformer model: {EMBEDDING_MODEL_NAME}...")
        _EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _EMBEDDING_MODEL


def embed_text(text: str) -> np.ndarray:
    """Generate normalized embedding for a single string."""
    model = get_embedding_model()
    emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return emb.astype("float32")


def embed_texts(texts: List[str]) -> np.ndarray:
    """Generate batch normalized embeddings."""
    if not texts:
        return np.empty((0, 384), dtype="float32")
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.astype("float32")
