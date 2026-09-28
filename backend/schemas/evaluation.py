from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class MetricSummary(BaseModel):
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float


class ClassMetric(BaseModel):
    precision: float
    recall: float
    f1_score: float
    support: int


class EvaluationResponse(BaseModel):
    is_trained: bool
    status: Optional[str] = "Production Model"
    evaluation_timestamp: Optional[str] = None
    total_test_samples: Optional[int] = None
    overall: Optional[MetricSummary] = None
    per_class: Optional[Dict[str, ClassMetric]] = None
    confusion_matrix: Optional[List[List[int]]] = None
    class_labels: List[str] = []
    notice: Optional[str] = None
    epochs_trained: Optional[int] = None
    training_time_seconds: Optional[float] = None
    best_val_accuracy: Optional[float] = None
