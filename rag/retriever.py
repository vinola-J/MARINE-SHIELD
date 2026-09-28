import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import faiss
import numpy as np

from rag.config import INDEX_FILE, METADATA_FILE, TOP_K_DEFAULT
from rag.embeddings import embed_text

_FAISS_INDEX: Optional[faiss.Index] = None
_CHUNKS_METADATA: Optional[List[Dict[str, Any]]] = None


def is_vectorstore_available() -> bool:
    """Check if both the FAISS index and chunks metadata exist on disk."""
    return Path(INDEX_FILE).exists() and Path(METADATA_FILE).exists()


def load_vectorstore():
    """Load and cache FAISS index and chunks metadata in memory."""
    global _FAISS_INDEX, _CHUNKS_METADATA
    if _FAISS_INDEX is not None and _CHUNKS_METADATA is not None:
        return _FAISS_INDEX, _CHUNKS_METADATA

    if not is_vectorstore_available():
        print(f"[RAG Retriever] Warning: Index or metadata not found at {INDEX_FILE}. Auto-ingesting...")
        from rag.ingest import ingest_knowledge_base
        ingest_knowledge_base(force_rebuild=False)

    index = faiss.read_index(str(INDEX_FILE))
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
    
    _FAISS_INDEX = index
    _CHUNKS_METADATA = meta.get("chunks", [])
    print(f"[RAG Retriever] Loaded FAISS index ({_FAISS_INDEX.ntotal} vectors) and {len(_CHUNKS_METADATA)} metadata records.")
    return _FAISS_INDEX, _CHUNKS_METADATA


def reload_vectorstore():
    """Force reload the cached vectorstore."""
    global _FAISS_INDEX, _CHUNKS_METADATA
    _FAISS_INDEX = None
    _CHUNKS_METADATA = None
    return load_vectorstore()


def retrieve_relevant_chunks(
    query: str,
    top_k: int = TOP_K_DEFAULT,
    min_similarity: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Search persistent FAISS vectorstore for chunks semantically matching the query.
    Returns structured records with similarity scores in descending order.
    """
    if not query or not query.strip():
        return []

    index, chunks = load_vectorstore()
    if index.ntotal == 0 or not chunks:
        return []

    query_emb = embed_text(query).reshape(1, -1)  # Shape (1, 384)
    k = min(top_k, index.ntotal)
    
    # Cosine similarities because embeddings were L2-normalized
    similarities, indices = index.search(query_emb, k)
    
    results = []
    for sim, idx in zip(similarities[0], indices[0]):
        if idx < 0 or idx >= len(chunks):
            continue
        sim_val = round(float(sim), 4)
        if sim_val < min_similarity:
            continue
        
        chunk_data = chunks[idx]
        results.append({
            "document_name": f"{chunk_data.get('doc_id', 'KB')} ({chunk_data.get('title', 'Marine Document')})",
            "title": chunk_data.get("title", "Marine Reference Document"),
            "category": chunk_data.get("category", "General Marine Pollution"),
            "source": chunk_data.get("source", "Marine Environmental Knowledge Base"),
            "chunk_id": chunk_data.get("chunk_id", ""),
            "chunk": chunk_data.get("text", ""),
            "similarity_score": sim_val
        })

    return results


def retrieve_for_pollution_analysis(
    prediction: str,
    severity: str,
    additional_question: Optional[str] = None,
    top_k: int = TOP_K_DEFAULT
) -> List[Dict[str, Any]]:
    """
    Formulate targeted environmental query for an image analysis result.
    Retrieves guidance relevant to specific pollution category and severity level.
    """
    query_parts = [
        f"Marine pollution {prediction}",
        f"{severity} severity ecological impact",
        "coastal cleanup response guidelines and safety",
        "monitoring protocol and handling"
    ]
    if additional_question:
        query_parts.append(additional_question)

    composed_query = " ".join(query_parts)
    return retrieve_relevant_chunks(composed_query, top_k=top_k)
