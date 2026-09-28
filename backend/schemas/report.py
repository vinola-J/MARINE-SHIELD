from typing import Optional
from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    analysis_id: str = Field(..., description="The ID of the analysis to generate a PDF report for")


class ReportResponse(BaseModel):
    report_id: str
    analysis_id: str
    report_path: str
    download_url: str
    created_at: Optional[str] = None
