import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Configurable Marine Pollution Classes
CLASS_NAMES = [
    "Plastic Waste",
    "Fishing Net",
    "Glass",
    "Metal",
    "Organic Waste",
    "Other Waste"
]

NUM_CLASSES = len(CLASS_NAMES)
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {idx: name for idx, name in enumerate(CLASS_NAMES)}

# Model Architecture Configuration
MODEL_ARCHITECTURE = os.getenv("MODEL_ARCHITECTURE", "mobilenet_v3_small")
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(MODELS_DIR / "marine_shield_model.pth")))
METRICS_PATH = MODELS_DIR / "evaluation_metrics.json"

# Image Preprocessing Parameters
IMAGE_SIZE = (224, 224)
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]

# Training Parameters
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.0003"))
EPOCHS = int(os.getenv("EPOCHS", "12"))
DROPOUT_RATE = 0.3

# Confidence & Validation Parameters
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.60"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "15"))
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
