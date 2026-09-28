import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import BACKEND_URL, REPORT_DIR
from database.database import get_db
from database.models import Analysis, Report
from backend.schemas.report import ReportGenerateRequest, ReportResponse
from reports.report_generator import generate_pollution_pdf_report

router = APIRouter(tags=["Reports"])


@router.post(
    "/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate structured PDF report for an analysis"
)
def create_report(request: ReportGenerateRequest, db: Session = Depends(get_db)):
    """Generate a downloadable PDF pollution assessment report for an existing analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{request.analysis_id}' not found."
        )

    report_id = str(uuid.uuid4())
    filename = f"marine_shield_report_{analysis.id}.pdf"

    # Generate PDF
    pdf_path = generate_pollution_pdf_report(
        analysis_data=analysis.to_dict(),
        output_filename=filename
    )

    # Persist in DB
    now_utc = datetime.now(timezone.utc)
    db_report = Report(
        id=report_id,
        analysis_id=analysis.id,
        report_path=str(pdf_path),
        created_at=now_utc
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    download_url = f"{BACKEND_URL}/api/reports/{report_id}/download"

    return {
        "report_id": report_id,
        "analysis_id": analysis.id,
        "report_path": str(pdf_path),
        "download_url": download_url,
        "created_at": now_utc.isoformat()
    }


@router.get(
    "/reports",
    response_model=List[ReportResponse],
    summary="List all generated pollution assessment reports"
)
def list_reports(db: Session = Depends(get_db)):
    """List all reports stored in the database."""
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    results = []
    for r in reports:
        results.append({
            "report_id": r.id,
            "analysis_id": r.analysis_id,
            "report_path": r.report_path,
            "download_url": f"{BACKEND_URL}/api/reports/{r.id}/download",
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return results


@router.get(
    "/reports/{report_id}/download",
    summary="Download PDF assessment report"
)
def download_report(report_id: str, db: Session = Depends(get_db)):
    """Serve the generated PDF file for download."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report record not found."
        )

    file_path = Path(report.report_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file is missing on server storage."
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name
    )
