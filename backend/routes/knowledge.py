import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from rag.config import KNOWLEDGE_BASE_DIR, INDEX_FILE, METADATA_FILE
from rag.ingest import ingest_knowledge_base
from rag.retriever import is_vectorstore_available, reload_vectorstore

router = APIRouter(tags=["Knowledge Base"])


@router.get(
    "/knowledge",
    summary="Get knowledge base status and indexed document information"
)
def get_knowledge_info():
    """Retrieve indexed document count, categories, and vector store readiness."""
    doc_files = list(KNOWLEDGE_BASE_DIR.glob("*.md")) + list(KNOWLEDGE_BASE_DIR.glob("*.txt"))
    indexed = is_vectorstore_available()

    total_chunks = 0
    chunks_preview = []
    if indexed:
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                total_chunks = data.get("total_chunks", 0)
                chunks_preview = [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "doc_id": c.get("doc_id"),
                        "title": c.get("title"),
                        "category": c.get("category"),
                        "source": c.get("source"),
                        "excerpt": c.get("text", "")[:160] + "..."
                    }
                    for c in data.get("chunks", [])[:10]
                ]
        except Exception as e:
            print(f"[Knowledge Router Error]: {e}")

    return {
        "status": "ready" if indexed else "unindexed",
        "total_documents": len(doc_files),
        "total_chunks": total_chunks,
        "knowledge_base_path": str(KNOWLEDGE_BASE_DIR),
        "documents": [
            {
                "filename": f.name,
                "size_bytes": f.stat().st_size
            }
            for f in sorted(doc_files)
        ],
        "sample_chunks": chunks_preview
    }


@router.post(
    "/knowledge/reindex",
    summary="Reindex knowledge base files into FAISS"
)
def reindex_knowledge():
    """Rebuild the persistent FAISS vector database from knowledge documents."""
    try:
        result = ingest_knowledge_base(force_rebuild=True)
        reload_vectorstore()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindexing failed: {str(e)}"
        )
