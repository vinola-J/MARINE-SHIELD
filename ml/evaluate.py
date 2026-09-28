import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)
import torch

from ml.config import METRICS_PATH, CLASS_NAMES


def compute_metrics(
    y_true: List[int],
    y_pred: List[int],
    class_names: List[str] = CLASS_NAMES
) -> Dict[str, Any]:
    """
    Compute rigorous evaluation metrics using scikit-learn.
    Never fabricated — only computed from actual ground truth and predictions.
    """
    accuracy = float(accuracy_score(y_true, y_pred))
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    
    report_dict = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))

    return {
        "is_trained": True,
        "status": "Production Model Verified",
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_test_samples": len(y_true),
        "overall": {
            "accuracy": round(accuracy, 4),
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "precision_weighted": round(float(p_weighted), 4),
            "recall_weighted": round(float(r_weighted), 4),
            "f1_weighted": round(float(f1_weighted), 4)
        },
        "per_class": {
            name: {
                "precision": round(report_dict[name]["precision"], 4),
                "recall": round(report_dict[name]["recall"], 4),
                "f1_score": round(report_dict[name]["f1-score"], 4),
                "support": int(report_dict[name]["support"])
            }
            for name in class_names if name in report_dict
        },
        "confusion_matrix": cm.tolist(),
        "class_labels": class_names
    }


def save_metrics(metrics: Dict[str, Any], path: Path = METRICS_PATH):
    """Save computed evaluation metrics to JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def load_evaluation_metrics() -> Dict[str, Any]:
    """
    Load real evaluation metrics from disk.
    If no trained model metrics exist, return clear status that production model is not trained yet.
    """
    if not METRICS_PATH.exists():
        return {
            "is_trained": False,
            "status": "Production model not trained yet.",
            "overall": None,
            "per_class": None,
            "confusion_matrix": None,
            "class_labels": CLASS_NAMES,
            "notice": "No verified model evaluation metrics found. Please execute the training pipeline to generate actual test metrics."
        }

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {
            "is_trained": False,
            "status": f"Failed to load evaluation metrics: {str(e)}",
            "overall": None,
            "per_class": None,
            "confusion_matrix": None,
            "class_labels": CLASS_NAMES
        }


def evaluate_model(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    device: torch.device
) -> Dict[str, Any]:
    """Run evaluation on a PyTorch dataloader and compute metrics."""
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    return compute_metrics(all_labels, all_preds, CLASS_NAMES)
