import uuid
from datetime import datetime, timezone
from database.database import get_db_context
from database.models import Analysis, AnalysisSource, Report


def test_database_crud():
    aid = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)

    with get_db_context() as db:
        # Create
        record = Analysis(
            id=aid,
            timestamp=now_utc,
            image_path="/tmp/test.jpg",
            prediction="Plastic Waste",
            confidence=0.89,
            severity="MEDIUM",
            severity_score=0.61,
            severity_reason="Scattered plastics",
            ai_assessment="Plastic assessment",
            recommendation="Cleanup protocol",
            status="COMPLETED",
            created_at=now_utc
        )
        db.add(record)
        
        src = AnalysisSource(
            analysis_id=aid,
            document_name="KB-DOC-001",
            chunk="Microplastics excerpt",
            similarity_score=0.85
        )
        db.add(src)

    with get_db_context() as db:
        fetched = db.query(Analysis).filter(Analysis.id == aid).first()
        assert fetched is not None
        assert fetched.prediction == "Plastic Waste"
        assert len(fetched.sources) == 1
        assert fetched.sources[0].document_name == "KB-DOC-001"

        # Cleanup
        db.delete(fetched)
