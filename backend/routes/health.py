from fastapi import APIRouter
from ml.predict import is_production_model_available
from rag.retriever import is_vectorstore_available
from database.database import engine

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Healthcheck endpoint returning system operational status and component readiness."""
    db_healthy = True
    try:
        with engine.connect() as conn:
            pass
    except Exception:
        db_healthy = False

    model_trained = is_production_model_available()
    vectorstore_ready = is_vectorstore_available()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "MARINE-SHIELD API",
        "version": "1.0.0",
        "components": {
            "database": "connected" if db_healthy else "error",
            "computer_vision_model": "trained_production" if model_trained else "demo_mode_active",
            "vector_store": "ready" if vectorstore_ready else "not_indexed"
        }
    }
