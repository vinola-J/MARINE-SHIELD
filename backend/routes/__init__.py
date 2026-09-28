from backend.routes.health import router as health_router
from backend.routes.analyze import router as analyze_router
from backend.routes.ask import router as ask_router
from backend.routes.reports import router as reports_router
from backend.routes.analysis import router as analysis_router
from backend.routes.evaluation import router as evaluation_router
from backend.routes.knowledge import router as knowledge_router

__all__ = [
    "health_router",
    "analyze_router",
    "ask_router",
    "reports_router",
    "analysis_router",
    "evaluation_router",
    "knowledge_router"
]
