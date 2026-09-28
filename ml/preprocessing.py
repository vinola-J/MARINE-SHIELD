import io
import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageStat, ImageFilter
import torch
from torchvision import transforms

from ml.config import (
    IMAGE_SIZE,
    NORM_MEAN,
    NORM_STD,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_EXTENSIONS
)


def get_train_transforms():
    """Data augmentation transforms for training."""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD)
    ])


def get_val_transforms():
    """Standard evaluation/inference transforms."""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD)
    ])


def validate_image(file_bytes: bytes, filename: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[Image.Image]]:
    """
    Validate uploaded image bytes against size, extension, and corruption checks.
    
    Returns:
        (is_valid, error_msg, pil_image)
    """
    if not file_bytes or len(file_bytes) == 0:
        return False, "Empty file provided.", None

    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return False, f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE_MB}MB.", None

    if filename:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}", None

    try:
        # First verification check
        stream = io.BytesIO(file_bytes)
        img_check = Image.open(stream)
        img_check.verify()

        # Re-open stream since verify closes or alters internal state
        stream.seek(0)
        img = Image.open(stream)
        
        # Ensure conversion to RGB (handles RGBA, grayscale, etc.)
        img_rgb = img.convert("RGB")
        return True, None, img_rgb
    except Exception as e:
        return False, f"Corrupted or invalid image file: {str(e)}", None


def preprocess_for_inference(image: Image.Image) -> torch.Tensor:
    """Preprocess a PIL Image into a normalized 4D tensor for model inference."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    val_transforms = get_val_transforms()
    tensor = val_transforms(image)
    return tensor.unsqueeze(0)  # Shape: (1, 3, 224, 224)


def extract_visual_features(image: Image.Image) -> Dict[str, Any]:
    """
    Extract explainable visual cues (edge density, brightness, contrast, clutter score)
    used to inform the prototype severity module.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size
    aspect_ratio = round(width / max(height, 1), 2)

    # Convert to grayscale for statistical edge and intensity analysis
    gray = image.convert("L")
    stat = ImageStat.Stat(gray)
    brightness = stat.mean[0] / 255.0  # 0.0 to 1.0
    contrast = stat.stddev[0] / 128.0  # approx normalized std dev

    # Edge filter to estimate debris clutter and boundary density
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_stat = ImageStat.Stat(edges)
    edge_density = min(1.0, edge_stat.mean[0] / 40.0)

    # Clutter / coverage proxy
    clutter_score = round(0.6 * edge_density + 0.4 * min(1.0, contrast), 4)

    return {
        "dimensions": f"{width}x{height}",
        "aspect_ratio": aspect_ratio,
        "brightness": round(brightness, 3),
        "contrast": round(contrast, 3),
        "edge_density": round(edge_density, 3),
        "clutter_score": clutter_score
    }
