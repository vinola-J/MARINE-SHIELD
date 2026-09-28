from pathlib import Path
import shutil
from ml.train import create_starter_marine_dataset
from ml.config import CLASS_NAMES

dataset_dir = Path("data/dataset")
samples_dir = Path("data/images/samples")
samples_dir.mkdir(parents=True, exist_ok=True)

print("Creating starter dataset...")
create_starter_marine_dataset(dataset_dir, samples_per_class=15)

print("Copying representative samples for the UI...")
for cls in CLASS_NAMES:
    folder = dataset_dir / "test" / cls
    img_files = list(folder.glob("*.jpg"))
    if img_files:
        dest = samples_dir / f"{cls.lower().replace(' ', '_')}_sample.jpg"
        shutil.copy(img_files[0], dest)
        print(f"Sample copied for {cls} -> {dest}")

print("All sample images prepared successfully.")
