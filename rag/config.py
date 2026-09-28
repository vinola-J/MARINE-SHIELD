import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"
VECTOR_DB_DIR = Path(os.getenv("VECTOR_DB_PATH", str(BASE_DIR / "vectorstore")))
INDEX_FILE = VECTOR_DB_DIR / "faiss_index.bin"
METADATA_FILE = VECTOR_DB_DIR / "chunks_metadata.json"

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))
TOP_K_DEFAULT = int(os.getenv("RAG_TOP_K", "3"))

# LLM Configurations
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "offline").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
