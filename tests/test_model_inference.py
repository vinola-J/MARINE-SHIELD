import pytest
from PIL import Image
from ml.config import CLASS_NAMES, NUM_CLASSES
from ml.model import MarineShieldClassifier
from ml.predict import predict_marine_pollution, is_production_model_available
import torch


def test_classifier_architecture():
    model = MarineShieldClassifier(num_classes=NUM_CLASSES, pretrained=False)
    dummy_input = torch.randn(2, 3, 224, 224)
    output = model(dummy_input)
    assert output.shape == (2, NUM_CLASSES)


def test_predict_marine_pollution():
    img = Image.new("RGB", (256, 256), color=(200, 220, 240))
    res = predict_marine_pollution(img)
    
    assert "prediction" in res
    assert res["prediction"] in CLASS_NAMES
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert "is_demo_mode" in res
    assert "top_predictions" in res
    assert len(res["top_predictions"]) >= 1
    assert "visual_features" in res
