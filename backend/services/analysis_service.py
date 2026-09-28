import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image
from sqlalchemy.orm import Session

from backend.config import UPLOAD_DIR, BACKEND_URL
from ml.preprocessing import validate_image
from ml.predict import predict_marine_pollution
from severity.severity import assess_pollution_severity
from rag.retriever import retrieve_for_pollution_analysis
from rag.generator import generate_pollution_assessment
from database.models import Analysis, AnalysisSource


def process_pollution_analysis(
    file_bytes: bytes,
    original_filename: str,
    db: Session
) -> Dict[str, Any]:
    """
    Complete end-to-end processing pipeline for marine pollution image:
    1. Validation
    2. Secure file persistence
    3. Computer vision classification
    4. Prototype severity assessment
    5. Knowledge base retrieval (RAG)
    6. Grounded AI generation
    7. Database persistence
    """
    # 1. Validation
    is_valid, error_msg, pil_image = validate_image(file_bytes, filename=original_filename)
    if not is_valid or pil_image is None:
        raise ValueError(error_msg or "Invalid image file.")

    # 2. Secure file persistence (do not trust user filename)
    analysis_id = str(uuid.uuid4())
    safe_filename = f"{analysis_id}.jpg"
    saved_path = UPLOAD_DIR / safe_filename
    pil_image.save(saved_path, format="JPEG", quality=92)
    relative_image_url = f"{BACKEND_URL}/uploads/{safe_filename}"

    # 3. Computer Vision Inference
    cv_result = predict_marine_pollution(pil_image)
    prediction = cv_result["prediction"]
    confidence = float(cv_result["confidence"])
    is_demo = cv_result.get("is_demo_mode", False)
    is_low_conf = cv_result.get("is_low_confidence", False)

    # 4. Severity Assessment (Explainable rule-based prototype)
    sev_result = assess_pollution_severity(
        prediction=prediction,
        confidence=confidence,
        visual_features=cv_result.get("visual_features"),
        is_low_confidence=is_low_conf
    )
    severity_level = sev_result["severity_level"]
    severity_score = float(sev_result["severity_score"])
    severity_reason = sev_result["severity_reason"]

    # 5. RAG Retrieval
    sources = retrieve_for_pollution_analysis(
        prediction=prediction,
        severity=severity_level,
        top_k=3
    )

    # 6. Grounded AI Assessment & Recommendation
    ai_assessment, recommendation = generate_pollution_assessment(
        prediction=prediction,
        confidence=confidence,
        severity=severity_level,
        severity_score=severity_score,
        severity_reason=severity_reason,
        sources=sources
    )

    # Determine status string
    if is_demo:
        status = "DEMO_MODE"
    elif is_low_conf:
        status = "LOW_CONFIDENCE"
    else:
        status = "COMPLETED"

    # 7. Database Persistence
    now_utc = datetime.now(timezone.utc)
    db_analysis = Analysis(
        id=analysis_id,
        timestamp=now_utc,
        image_path=str(saved_path),
        prediction=prediction,
        confidence=confidence,
        severity=severity_level,
        severity_score=severity_score,
        severity_reason=severity_reason,
        ai_assessment=ai_assessment,
        recommendation=recommendation,
        status=status,
        created_at=now_utc
    )
    db.add(db_analysis)

    for s in sources:
        db_source = AnalysisSource(
            analysis_id=analysis_id,
            document_name=s.get("document_name", "Marine Reference"),
            chunk=s.get("chunk", ""),
            similarity_score=float(s.get("similarity_score", 0.0))
        )
        db.add(db_source)

    db.commit()
    db.refresh(db_analysis)

    return {
        "analysis_id": analysis_id,
        "prediction": prediction,
        "confidence": confidence,
        "severity": severity_level,
        "severity_score": severity_score,
        "severity_reason": severity_reason,
        "analysis_status": status,
        "is_demo_mode": is_demo,
        "is_low_confidence": is_low_conf,
        "low_confidence_warning": cv_result.get("low_confidence_warning"),
        "ai_assessment": ai_assessment,
        "recommendation": recommendation,
        "sources": sources,
        "top_predictions": cv_result.get("top_predictions", []),
        "image_url": relative_image_url
    }
