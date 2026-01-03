import os
import torch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "app", "models")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Use the copied .pt files (NOT the .torchscript files)
BINARY_MODEL = os.path.join(MODEL_DIR, "binary_model.pt")
BANKNOTE_MODEL = os.path.join(MODEL_DIR, "banknote_model.pt")
COIN_MODEL = os.path.join(MODEL_DIR, "coin_model.pt")

BINARY_CONFIDENCE = 0.35
BANKNOTE_CONFIDENCE = 0.45
COIN_CONFIDENCE = 0.45

IMAGE_SIZE = 640
USE_PREPROCESSING = True
USE_ENSEMBLE = True

MAX_IMAGE_SIZE = 10*1024*1024
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

TTS_LANGUAGE = 'mk'
TTS_ENABLED = True