from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.config import BACKEND_URL
from database.database import get_db
from database.models import Analysis
from backend.schemas.analysis import AnalysisDetailResponse

router = APIRouter(tags=["Analysis Records"])


@router.get(
    "/analysis/{analysis_id}",
    response_model=AnalysisDetailResponse,
    summary="Get single analysis details"
)
def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve an existing pollution analysis by ID."""
    record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found."
        )

    res_dict = record.to_dict()
    img_name = Path(record.image_path).name if record.image_path else ""
    image_url = f"{BACKEND_URL}/uploads/{img_name}" if img_name else None

    return {
        "analysis_id": record.id,
        "prediction": record.prediction,
        "confidence": record.confidence,
        "severity": record.severity,
        "severity_score": record.severity_score,
        "severity_reason": record.severity_reason,
        "analysis_status": record.status,
        "is_demo_mode": record.status == "DEMO_MODE",
        "is_low_confidence": record.status == "LOW_CONFIDENCE",
        "low_confidence_warning": "Low-confidence prediction. Please verify the result manually." if record.status == "LOW_CONFIDENCE" else None,
        "ai_assessment": record.ai_assessment,
        "recommendation": record.recommendation,
        "sources": [s.to_dict() for s in record.sources],
        "top_predictions": [],
        "image_url": image_url,
        "image_path": record.image_path,
        "timestamp": record.timestamp.isoformat() if record.timestamp else None,
        "created_at": record.created_at.isoformat() if record.created_at else None
    }


@router.get(
    "/analyses",
    summary="List recent pollution analyses for dashboard"
)
def list_analyses(
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List recent pollution analyses ordered by latest created."""
    records = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(limit).all()
    results = []
    for r in records:
        img_name = Path(r.image_path).name if r.image_path else ""
        results.append({
            "analysis_id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "prediction": r.prediction,
            "confidence": round(r.confidence, 4),
            "severity": r.severity,
            "severity_score": round(r.severity_score, 4),
            "severity_reason": r.severity_reason,
            "analysis_status": r.status,
            "image_url": f"{BACKEND_URL}/uploads/{img_name}" if img_name else None,
            "has_reports": len(r.reports) > 0
        })
    return results
