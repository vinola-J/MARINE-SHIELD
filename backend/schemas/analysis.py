from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisSourceSchema(BaseModel):
    document_name: str
    chunk: str
    similarity_score: float


class TopPredictionSchema(BaseModel):
    class_name: str
    probability: float


class AnalyzeResponse(BaseModel):
    analysis_id: str
    prediction: str
    confidence: float
    severity: str
    severity_score: float
    severity_reason: str
    analysis_status: str
    is_demo_mode: bool = False
    is_low_confidence: bool = False
    low_confidence_warning: Optional[str] = None
    ai_assessment: Optional[str] = None
    recommendation: Optional[str] = None
    sources: List[AnalysisSourceSchema] = []
    top_predictions: List[TopPredictionSchema] = []
    image_url: Optional[str] = None


class AnalysisDetailResponse(AnalyzeResponse):
    timestamp: Optional[str] = None
    created_at: Optional[str] = None
    image_path: Optional[str] = None
