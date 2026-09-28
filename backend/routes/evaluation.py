from fastapi import APIRouter, BackgroundTasks
from ml.evaluate import load_evaluation_metrics
from ml.train import train_model
from backend.schemas.evaluation import EvaluationResponse

router = APIRouter(tags=["Model Evaluation"])


@router.get(
    "/evaluation",
    response_model=EvaluationResponse,
    summary="Get computer vision model evaluation metrics"
)
def get_model_evaluation():
    """
    Retrieve real test evaluation metrics for the production model.
    Never fabricates metrics: if model is not trained, returns clear status.
    """
    metrics = load_evaluation_metrics()
    return metrics


@router.post(
    "/evaluation/train",
    summary="Trigger model training pipeline"
)
def trigger_training(background_tasks: BackgroundTasks, epochs: int = 5):
    """Trigger retraining of the MobileNetV3 marine pollution classifier in background."""
    background_tasks.add_task(train_model, epochs=epochs)
    return {
        "status": "initiated",
        "message": f"Model training initiated for {epochs} epochs in background."
    }
