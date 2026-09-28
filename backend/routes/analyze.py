from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from backend.schemas.analysis import AnalyzeResponse
from backend.services.analysis_service import process_pollution_analysis

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze marine/coastal image for pollution"
)
async def analyze_image(
    file: UploadFile = File(..., description="Marine or coastal photo (JPG, JPEG, PNG, WEBP)"),
    db: Session = Depends(get_db)
):
    """
    Execute full computer vision classification, prototype severity assessment,
    RAG environmental retrieval, and grounded response generation.
    """
    try:
        content = await file.read()
        result = process_pollution_analysis(
            file_bytes=content,
            original_filename=file.filename or "uploaded_image.jpg",
            db=db
        )
        return result
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        print(f"[Error in /api/analyze]: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the marine pollution analysis."
        )
