from pathlib import Path
import torch

# === BASE PATHS ===

# backend/app/core/config.py → backend/
BASE_DIR = Path(__file__).resolve().parents[2]

APP_DIR = BASE_DIR / "app"
MODELS_DIR = APP_DIR / "models"

# === DEVICE ===

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# === MODEL PATHS (YOLO .pt) ===

# NOT the .torchscript files.
BINARY_MODEL = MODELS_DIR / "binary_model.pt"
BANKNOTE_MODEL = MODELS_DIR / "banknote_model.pt"
COIN_MODEL = MODELS_DIR / "coin_model.pt"

# Early validation.
for model_path in (BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL):
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

# === CONFIDENCE THRESHOLDS ===

BINARY_CONFIDENCE = 0.35
BANKNOTE_CONFIDENCE = 0.45
COIN_CONFIDENCE = 0.45

# === IMAGE & PIPELINE SETTINGS ===

IMAGE_SIZE = 640
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

USE_PREPROCESSING = True
USE_ENSEMBLE = True

