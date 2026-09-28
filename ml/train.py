import os
import argparse
import time
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision.datasets import ImageFolder

from ml.config import (
    CLASS_NAMES,
    NUM_CLASSES,
    MODEL_PATH,
    METRICS_PATH,
    BATCH_SIZE,
    LEARNING_RATE,
    EPOCHS,
    MODEL_ARCHITECTURE,
    DATA_DIR
)
from ml.model import MarineShieldClassifier
from ml.preprocessing import get_train_transforms, get_val_transforms
from ml.evaluate import compute_metrics, save_metrics
from ml.predict import reload_classifier


def create_starter_marine_dataset(dataset_dir: Path, samples_per_class: int = 15):
    """
    Generate representative synthetic coastal/marine imagery with characteristic visual textures
    for each pollution category to allow training and validating the real pipeline immediately.
    """
    splits = ["train", "val", "test"]
    split_counts = {
        "train": samples_per_class,
        "val": max(3, samples_per_class // 4),
        "test": max(3, samples_per_class // 4)
    }

    # Distinct color palettes and textures representing coastal background + debris
    debris_profiles = {
        "Plastic Waste": {
            "bg": (200, 220, 240), # Ocean wash / wet sand
            "debris_colors": [(255, 60, 60), (30, 144, 255), (255, 255, 50)], # Bright plastic bottles/wrappers
            "shape": "rectangles"
        },
        "Fishing Net": {
            "bg": (120, 160, 180), # Coastal rocks/water
            "debris_colors": [(20, 180, 120), (50, 80, 60), (220, 160, 30)], # Monofilament ropes / netting
            "shape": "mesh"
        },
        "Glass": {
            "bg": (225, 210, 180), # Sand
            "debris_colors": [(60, 140, 100), (140, 110, 60), (220, 240, 240)], # Green/brown/clear glass bottles
            "shape": "ellipses"
        },
        "Metal": {
            "bg": (180, 175, 160), # Shingle / gravel
            "debris_colors": [(170, 75, 35), (192, 192, 192), (110, 110, 110)], # Rust / aluminum cans
            "shape": "cylinders"
        },
        "Organic Waste": {
            "bg": (195, 205, 175), # Intertidal zone
            "debris_colors": [(85, 107, 47), (139, 69, 19), (47, 79, 79)], # Sargassum seaweed / driftwood
            "shape": "organic"
        },
        "Other Waste": {
            "bg": (170, 180, 190), # Tidal pool / mudflat
            "debris_colors": [(100, 100, 100), (70, 40, 30), (200, 100, 150)], # Composite waste / tires
            "shape": "composite"
        }
    }

    for split in splits:
        count = split_counts[split]
        for class_name in CLASS_NAMES:
            folder = dataset_dir / split / class_name
            folder.mkdir(parents=True, exist_ok=True)
            profile = debris_profiles[class_name]

            for i in range(count):
                # Create 256x256 image
                bg_color = tuple(
                    int(c + np.random.randint(-15, 15)) for c in profile["bg"]
                )
                img = Image.new("RGB", (256, 256), color=bg_color)
                draw = ImageDraw.Draw(img)

                # Add coastal texture lines
                for _ in range(8):
                    y = np.random.randint(0, 256)
                    draw.line([(0, y), (256, y + np.random.randint(-10, 10))], fill=(bg_color[0]-15, bg_color[1]-15, bg_color[2]-15), width=2)

                shape_type = profile["shape"]
                debris_col = profile["debris_colors"][i % len(profile["debris_colors"])]

                if shape_type == "rectangles":
                    # Plastic containers/wrappers
                    x0, y0 = np.random.randint(40, 120), np.random.randint(40, 120)
                    draw.rectangle([x0, y0, x0 + np.random.randint(30, 80), y0 + np.random.randint(40, 100)], fill=debris_col, outline=(0, 0, 0))
                elif shape_type == "mesh":
                    # Netting grid lines
                    for x in range(30, 220, 25):
                        draw.line([(x, 30), (x + 30, 220)], fill=debris_col, width=3)
                    for y in range(30, 220, 25):
                        draw.line([(30, y + 20), (220, y)], fill=debris_col, width=3)
                elif shape_type == "ellipses":
                    # Glass bottle shape
                    x0, y0 = np.random.randint(50, 130), np.random.randint(50, 130)
                    draw.ellipse([x0, y0, x0 + 40, y0 + 90], fill=debris_col, outline=(30, 30, 30))
                elif shape_type == "cylinders":
                    # Can shape
                    x0, y0 = np.random.randint(50, 130), np.random.randint(50, 130)
                    draw.rounded_rectangle([x0, y0, x0 + 50, y0 + 75], radius=10, fill=debris_col, outline=(40, 40, 40))
                elif shape_type == "organic":
                    # Seaweed clusters
                    for _ in range(5):
                        x = np.random.randint(50, 180)
                        y = np.random.randint(50, 180)
                        draw.arc([x, y, x + 60, y + 40], start=0, end=180, fill=debris_col, width=6)
                else:
                    # Other mixed debris
                    x0, y0 = np.random.randint(40, 130), np.random.randint(40, 130)
                    draw.polygon([(x0, y0), (x0+50, y0+20), (x0+30, y0+70), (x0-20, y0+50)], fill=debris_col, outline=(20, 20, 20))

                img_path = folder / f"{class_name.lower().replace(' ', '_')}_{i:03d}.jpg"
                img.save(img_path, quality=90)


def train_model(
    dataset_path: Optional[str] = None,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    output_model_path: Path = MODEL_PATH
) -> Tuple[MarineShieldClassifier, dict]:
    """
    Complete end-to-end training and evaluation pipeline for Marine-Shield.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Training] Using device: {device}")

    # Prepare dataset
    if dataset_path is None or not Path(dataset_path).exists():
        dataset_dir = DATA_DIR / "dataset"
        print(f"[Training] Generating starter marine pollution dataset in: {dataset_dir}")
        create_starter_marine_dataset(dataset_dir, samples_per_class=18)
    else:
        dataset_dir = Path(dataset_path)

    train_dir = dataset_dir / "train"
    val_dir = dataset_dir / "val"
    test_dir = dataset_dir / "test"

    train_dataset = ImageFolder(str(train_dir), transform=get_train_transforms())
    val_dataset = ImageFolder(str(val_dir), transform=get_val_transforms())
    test_dataset = ImageFolder(str(test_dir), transform=get_val_transforms())

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    print(f"[Training] Classes: {train_dataset.classes}")
    print(f"[Training] Dataset sizes -> Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")

    # Model, Loss, Optimizer
    model = MarineShieldClassifier(
        architecture=MODEL_ARCHITECTURE,
        num_classes=NUM_CLASSES,
        pretrained=True
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    best_weights = None

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        scheduler.step()
        train_loss = running_loss / max(total, 1)
        train_acc = correct / max(total, 1)

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_acc = val_correct / max(val_total, 1)
        print(f"Epoch [{epoch:02d}/{epochs:02d}] Train Loss: {train_loss:.4f} Acc: {train_acc*100:.1f}% | Val Loss: {val_loss/max(val_total,1):.4f} Val Acc: {val_acc*100:.1f}%")

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            best_weights = model.state_dict().copy()

    elapsed = time.time() - start_time
    print(f"[Training] Completed in {elapsed:.1f}s. Best Validation Accuracy: {best_val_acc*100:.1f}%")

    # Load best weights before test evaluation
    if best_weights:
        model.load_state_dict(best_weights)

    # Test Evaluation
    model.eval()
    test_preds = []
    test_targets = []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = outputs.max(1)
            test_preds.extend(preds.cpu().numpy().tolist())
            test_targets.extend(labels.numpy().tolist())

    metrics = compute_metrics(test_targets, test_preds, CLASS_NAMES)
    metrics["epochs_trained"] = epochs
    metrics["training_time_seconds"] = round(elapsed, 2)
    metrics["best_val_accuracy"] = round(best_val_acc, 4)

    # Save checkpoint
    model.save_checkpoint(output_model_path, epoch=epochs, metrics=metrics)
    save_metrics(metrics, METRICS_PATH)
    print(f"[Training] Model saved to {output_model_path}")
    print(f"[Training] Evaluation metrics saved to {METRICS_PATH}")

    # Reload cached model
    reload_classifier()

    return model, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MARINE-SHIELD Computer Vision Model")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    parser.add_argument("--dataset", type=str, default=None, help="Path to custom dataset directory")
    args = parser.parse_args()

    train_model(
        dataset_path=args.dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )
