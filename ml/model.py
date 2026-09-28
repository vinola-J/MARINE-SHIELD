import os
from pathlib import Path
from typing import Dict, Any, Optional
import torch
import torch.nn as nn
from torchvision.models import (
    mobilenet_v3_small,
    MobileNet_V3_Small_Weights,
    mobilenet_v3_large,
    MobileNet_V3_Large_Weights,
    resnet18,
    ResNet18_Weights
)

from ml.config import (
    NUM_CLASSES,
    CLASS_NAMES,
    MODEL_ARCHITECTURE,
    DROPOUT_RATE
)


class MarineShieldClassifier(nn.Module):
    """
    Computer Vision model for Marine Pollution Classification.
    Utilizes transfer learning with MobileNetV3 (default) or ResNet18.
    """
    def __init__(
        self,
        architecture: str = MODEL_ARCHITECTURE,
        num_classes: int = NUM_CLASSES,
        pretrained: bool = True,
        dropout_rate: float = DROPOUT_RATE
    ):
        super().__init__()
        self.architecture = architecture.lower()
        self.num_classes = num_classes

        if "mobilenet_v3_small" in self.architecture:
            weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
            backbone = mobilenet_v3_small(weights=weights)
            in_features = backbone.classifier[0].in_features
            
            # Replace classifier head
            backbone.classifier = nn.Sequential(
                nn.Linear(in_features, 256),
                nn.Hardswish(),
                nn.Dropout(p=dropout_rate),
                nn.Linear(256, num_classes)
            )
            self.model = backbone

        elif "mobilenet_v3_large" in self.architecture:
            weights = MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
            backbone = mobilenet_v3_large(weights=weights)
            in_features = backbone.classifier[0].in_features
            
            backbone.classifier = nn.Sequential(
                nn.Linear(in_features, 256),
                nn.Hardswish(),
                nn.Dropout(p=dropout_rate),
                nn.Linear(256, num_classes)
            )
            self.model = backbone

        elif "resnet18" in self.architecture:
            weights = ResNet18_Weights.DEFAULT if pretrained else None
            backbone = resnet18(weights=weights)
            in_features = backbone.fc.in_features
            
            backbone.fc = nn.Sequential(
                nn.Linear(in_features, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(p=dropout_rate),
                nn.Linear(256, num_classes)
            )
            self.model = backbone
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

    def save_checkpoint(self, path: Path | str, epoch: int = 0, metrics: Optional[Dict[str, Any]] = None):
        """Save model state dict, architecture metadata, and training metrics."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "state_dict": self.state_dict(),
            "architecture": self.architecture,
            "num_classes": self.num_classes,
            "class_names": CLASS_NAMES,
            "epoch": epoch,
            "metrics": metrics or {}
        }
        torch.save(checkpoint, path)

    @classmethod
    def load_from_checkpoint(cls, path: Path | str, device: Optional[torch.device] = None) -> "MarineShieldClassifier":
        """Load trained model from checkpoint file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at: {path}")

        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        checkpoint = torch.load(path, map_location=device)
        arch = checkpoint.get("architecture", MODEL_ARCHITECTURE)
        num_classes = checkpoint.get("num_classes", NUM_CLASSES)

        model = cls(architecture=arch, num_classes=num_classes, pretrained=False)
        model.load_state_dict(checkpoint["state_dict"])
        model.to(device)
        model.eval()
        return model
