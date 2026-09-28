import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import torch
import torch.nn.functional as F

from ml.config import (
    MODEL_PATH,
    CLASS_NAMES,
    LOW_CONFIDENCE_THRESHOLD,
    NUM_CLASSES
)
from ml.model import MarineShieldClassifier
from ml.preprocessing import preprocess_for_inference, extract_visual_features

# Global in-memory cache for the loaded model
_CACHED_MODEL: Optional[MarineShieldClassifier] = None
_CACHED_DEVICE: Optional[torch.device] = None


def get_inference_device() -> torch.device:
    """Select appropriate device (CPU default for predictable deployment)."""
    global _CACHED_DEVICE
    if _CACHED_DEVICE is None:
        _CACHED_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _CACHED_DEVICE


def load_classifier() -> Optional[MarineShieldClassifier]:
    """Load and cache the trained production model if available."""
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    model_file = Path(MODEL_PATH)
    if model_file.exists():
        try:
            device = get_inference_device()
            _CACHED_MODEL = MarineShieldClassifier.load_from_checkpoint(model_file, device=device)
            return _CACHED_MODEL
        except Exception as e:
            print(f"[Warning] Failed to load production model from {model_file}: {e}")
            _CACHED_MODEL = None
            return None
    return None


def reload_classifier():
    """Clear and reload cached model (e.g. after training)."""
    global _CACHED_MODEL
    _CACHED_MODEL = None
    return load_classifier()


def is_production_model_available() -> bool:
    """Check if the trained production model checkpoint exists on disk."""
    return Path(MODEL_PATH).exists()


def run_demo_prediction(image: Image.Image, visual_feats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic fallback prediction when the model checkpoint has not been trained yet.
    Clearly marks is_demo_mode = True and returns demo disclosure.
    """
    # Use image dimensions and visual features to select a deterministic class
    feat_val = int(visual_feats.get("clutter_score", 0.5) * 100) + int(visual_feats.get("brightness", 0.5) * 100)
    class_idx = feat_val % NUM_CLASSES
    predicted_class = CLASS_NAMES[class_idx]
    
    # Deterministic confidence between 0.65 and 0.88 for demo
    conf = round(0.68 + ((feat_val % 20) / 100.0), 3)

    return {
        "prediction": predicted_class,
        "confidence": conf,
        "is_demo_mode": True,
        "model_status": "Production model not trained yet. (DEMO MODE)",
        "model_notice": "DEMO MODE active — this prediction is a placeholder because the production model has not been trained yet.",
        "is_low_confidence": conf < LOW_CONFIDENCE_THRESHOLD,
        "low_confidence_warning": "Low-confidence prediction. Please verify the result manually." if conf < LOW_CONFIDENCE_THRESHOLD else None,
        "top_predictions": [
            {"class_name": predicted_class, "probability": conf},
            {"class_name": CLASS_NAMES[(class_idx + 1) % NUM_CLASSES], "probability": round((1.0 - conf) * 0.7, 3)},
            {"class_name": CLASS_NAMES[(class_idx + 2) % NUM_CLASSES], "probability": round((1.0 - conf) * 0.3, 3)}
        ],
        "visual_features": visual_feats
    }


def predict_marine_pollution(image: Image.Image) -> Dict[str, Any]:
    """
    Execute pollution classification on an image.
    Uses real trained model if available, otherwise falls back to clearly marked DEMO MODE.
    """
    visual_feats = extract_visual_features(image)
    model = load_classifier()

    if model is None:
        # Fallback to clearly identified DEMO MODE
        return run_demo_prediction(image, visual_feats)

    # Real Production Inference
    device = get_inference_device()
    tensor = preprocess_for_inference(image).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = F.softmax(logits, dim=1).squeeze(0)

    top_prob, top_idx = torch.topk(probabilities, k=min(3, NUM_CLASSES))
    
    predicted_idx = int(top_idx[0].item())
    confidence = float(top_prob[0].item())
    predicted_class = CLASS_NAMES[predicted_idx]

    top_predictions = []
    for p, idx in zip(top_prob, top_idx):
        top_predictions.append({
            "class_name": CLASS_NAMES[int(idx.item())],
            "probability": round(float(p.item()), 4)
        })

    is_low_conf = confidence < LOW_CONFIDENCE_THRESHOLD

    return {
        "prediction": predicted_class,
        "confidence": round(confidence, 4),
        "is_demo_mode": False,
        "model_status": "Production Model",
        "model_notice": None,
        "is_low_confidence": is_low_conf,
        "low_confidence_warning": "Low-confidence prediction. Please verify the result manually." if is_low_conf else None,
        "top_predictions": top_predictions,
        "visual_features": visual_feats
    }
