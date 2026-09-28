from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    image_path = Column(String(500), nullable=False)
    prediction = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False)
    severity_score = Column(Float, nullable=False)
    severity_reason = Column(Text, nullable=False)
    ai_assessment = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    status = Column(String(50), default="COMPLETED", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    sources = relationship("AnalysisSource", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "image_path": self.image_path,
            "prediction": self.prediction,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "severity_score": round(self.severity_score, 4),
            "severity_reason": self.severity_reason,
            "ai_assessment": self.ai_assessment,
            "recommendation": self.recommendation,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sources": [s.to_dict() for s in self.sources] if self.sources else []
        }


class AnalysisSource(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    chunk = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=False)

    analysis = relationship("Analysis", back_populates="sources")

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "document_name": self.document_name,
            "chunk": self.chunk,
            "similarity_score": round(self.similarity_score, 4)
        }


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    report_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analysis = relationship("Analysis", back_populates="reports")

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "report_path": self.report_path,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
