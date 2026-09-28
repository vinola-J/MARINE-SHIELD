import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import faiss
import numpy as np

from rag.config import (
    KNOWLEDGE_BASE_DIR,
    VECTOR_DB_DIR,
    INDEX_FILE,
    METADATA_FILE,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from rag.embeddings import embed_texts


def parse_markdown_metadata(content: str) -> Tuple[Dict[str, str], str]:
    """Extract metadata header lines from markdown content."""
    metadata = {
        "title": "Marine Environmental Reference",
        "doc_id": "KB-DOC",
        "category": "Marine Environmental Information",
        "source": "Marine Environmental Research Review"
    }

    lines = content.splitlines()
    body_lines = []
    
    # Read title from first # header
    for line in lines:
        if line.startswith("# ") and metadata["title"] == "Marine Environmental Reference":
            metadata["title"] = line.replace("# ", "").strip()
            break

    # Look for metadata tags: **Document ID:**, **Category:**, **Source:**
    for line in lines:
        if "**Document ID:**" in line:
            metadata["doc_id"] = line.split("**Document ID:**")[-1].strip()
        elif "**Category:**" in line:
            metadata["category"] = line.split("**Category:**")[-1].strip()
        elif "**Source:**" in line:
            metadata["source"] = line.split("**Source:**")[-1].strip()
        else:
            body_lines.append(line)

    clean_body = "\n".join(body_lines).strip()
    return metadata, clean_body


def chunk_document(
    text: str,
    metadata: Dict[str, str],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Split document into semantically coherent overlapping text chunks.
    Preserves document structure and contextual metadata with each chunk.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_length = 0

    for paragraph in paragraphs:
        p_len = len(paragraph)
        if current_length + p_len > chunk_size and current_chunk:
            combined = "\n\n".join(current_chunk)
            chunks.append(combined)
            # Retain overlap from end of current chunk
            overlap_text = current_chunk[-1] if len(current_chunk[-1]) <= chunk_overlap else current_chunk[-1][-chunk_overlap:]
            current_chunk = [overlap_text, paragraph]
            current_length = len(overlap_text) + p_len
        else:
            current_chunk.append(paragraph)
            current_length += p_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # Format structured chunk records
    records = []
    for idx, chunk_text in enumerate(chunks):
        records.append({
            "chunk_id": f"{metadata['doc_id']}_c{idx+1}",
            "doc_id": metadata["doc_id"],
            "title": metadata["title"],
            "category": metadata["category"],
            "source": metadata["source"],
            "text": chunk_text
        })
    return records


def ingest_knowledge_base(force_rebuild: bool = False) -> Dict[str, Any]:
    """
    Ingest all knowledge documents into FAISS index and metadata store.
    If the index already exists and force_rebuild is False, skip recomputation.
    """
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    if INDEX_FILE.exists() and METADATA_FILE.exists() and not force_rebuild:
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                meta = json.load(f)
            return {
                "status": "cached",
                "message": "Persistent FAISS vector database already exists.",
                "total_documents": len(set(c["doc_id"] for c in meta.get("chunks", []))),
                "total_chunks": len(meta.get("chunks", [])),
                "index_path": str(INDEX_FILE)
            }
        except Exception:
            pass  # Fall through to rebuild if file is damaged

    print("[RAG Ingestion] Scanning knowledge base directory:", KNOWLEDGE_BASE_DIR)
    doc_files = list(KNOWLEDGE_BASE_DIR.glob("*.md")) + list(KNOWLEDGE_BASE_DIR.glob("*.txt"))
    if not doc_files:
        raise FileNotFoundError(f"No knowledge base documents found in {KNOWLEDGE_BASE_DIR}")

    all_chunks = []
    for filepath in sorted(doc_files):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        metadata, body = parse_markdown_metadata(content)
        chunks = chunk_document(body, metadata)
        all_chunks.extend(chunks)

    print(f"[RAG Ingestion] Extracted {len(all_chunks)} chunks across {len(doc_files)} documents.")

    texts_to_embed = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts_to_embed)  # Shape: (N, 384)

    # Initialize FAISS cosine similarity index (IndexFlatIP on normalized vectors)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Write persistent files
    faiss.write_index(index, str(INDEX_FILE))
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "total_chunks": len(all_chunks),
            "embedding_dimension": dimension,
            "chunks": all_chunks
        }, f, indent=2)

    print(f"[RAG Ingestion] Successfully created FAISS index at {INDEX_FILE}")
    return {
        "status": "created",
        "message": "Successfully ingested knowledge base into persistent FAISS index.",
        "total_documents": len(doc_files),
        "total_chunks": len(all_chunks),
        "index_path": str(INDEX_FILE)
    }


if __name__ == "__main__":
    result = ingest_knowledge_base(force_rebuild=True)
    print("Ingestion result:", json.dumps(result, indent=2))
