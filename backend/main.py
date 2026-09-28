from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import UPLOAD_DIR, REPORT_DIR, CORS_ORIGINS
from database.database import init_db
from ml.predict import load_classifier
from rag.retriever import load_vectorstore
from backend.routes import (
    health_router,
    analyze_router,
    ask_router,
    reports_router,
    analysis_router,
    evaluation_router,
    knowledge_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle:
    - Initialize SQLite database tables
    - Pre-load and cache the machine learning classifier
    - Pre-load and cache the FAISS vector index
    """
    print("[Lifecycle] Initializing MARINE-SHIELD database...")
    init_db()

    print("[Lifecycle] Checking & caching Computer Vision classifier...")
    try:
        load_classifier()
    except Exception as e:
        print(f"[Lifecycle Warning] Classifier caching note: {e}")

    print("[Lifecycle] Checking & caching FAISS vector database...")
    try:
        load_vectorstore()
    except Exception as e:
        print(f"[Lifecycle Warning] Vectorstore caching note: {e}")

    print("[Lifecycle] MARINE-SHIELD backend initialization complete.")
    yield
    print("[Lifecycle] Shutting down MARINE-SHIELD backend.")


app = FastAPI(
    title="MARINE-SHIELD API",
    description="AI-Powered Marine Pollution Detection, Assessment & Response System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts for images and reports
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/generated_reports", StaticFiles(directory=str(REPORT_DIR)), name="generated_reports")

# Register API Routers
app.include_router(health_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(ask_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(evaluation_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")


@app.get("/", tags=["Root"])
def root():
    return {
        "project": "MARINE-SHIELD",
        "description": "AI-Powered Marine Pollution Detection, Assessment & Response System",
        "documentation": "/docs",
        "health_check": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    from backend.config import BACKEND_HOST, BACKEND_PORT
    uvicorn.run("backend.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
