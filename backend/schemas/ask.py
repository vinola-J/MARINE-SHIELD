from typing import List, Optional
from pydantic import BaseModel, Field
from backend.schemas.analysis import AnalysisSourceSchema


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Environmental question regarding marine pollution")
    analysis_id: Optional[str] = Field(None, description="Optional ID of an analyzed incident for specific context")


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[AnalysisSourceSchema] = []
