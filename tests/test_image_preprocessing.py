import io
import pytest
from PIL import Image
from ml.preprocessing import validate_image, preprocess_for_inference, extract_visual_features


def test_valid_image_validation():
    # Create simple valid test image
    img = Image.new("RGB", (300, 300), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    data = buf.getvalue()

    is_valid, err, pil_img = validate_image(data, "coastal.jpg")
    assert is_valid is True
    assert err is None
    assert pil_img is not None
    assert pil_img.size == (300, 300)


def test_invalid_extension():
    img = Image.new("RGB", (100, 100), color=(50, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    data = buf.getvalue()

    is_valid, err, pil_img = validate_image(data, "document.pdf")
    assert is_valid is False
    assert "Unsupported file extension" in err


def test_corrupted_image():
    corrupted_data = b"NOT_AN_IMAGE_FILE_RANDOM_CORRUPTED_BYTES"
    is_valid, err, pil_img = validate_image(corrupted_data, "bad.jpg")
    assert is_valid is False
    assert "Corrupted or invalid" in err


def test_preprocess_for_inference():
    img = Image.new("RGB", (400, 300), color=(80, 120, 160))
    tensor = preprocess_for_inference(img)
    assert tensor.shape == (1, 3, 224, 224)


def test_extract_visual_features():
    img = Image.new("RGB", (256, 256), color=(120, 140, 160))
    feats = extract_visual_features(img)
    assert "brightness" in feats
    assert "contrast" in feats
    assert "edge_density" in feats
    assert "clutter_score" in feats
    assert 0.0 <= feats["brightness"] <= 1.0
