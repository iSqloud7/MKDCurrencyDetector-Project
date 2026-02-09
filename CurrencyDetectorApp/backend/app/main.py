from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import cv2
import numpy as np
from PIL import Image
import io
import base64
import uvicorn

from core.config import (
    BINARY_MODEL,
    BANKNOTE_MODEL,
    COIN_MODEL,
    DEVICE,
    USE_PREPROCESSING,
    USE_ENSEMBLE,
    MAX_IMAGE_SIZE,
)

from services.inference import init_detector, detect_currency
from services.extraction import extract_single_currency
from services.tts import text_to_speech   # 👈 ELEVENLABS HERE
from core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="MKD Currency Detector API",
    version="2.0.0",
    description="API for detecting Macedonian currency (coins and banknotes)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# STARTUP
# =========================
@app.on_event("startup")
async def startup_event():
    try:
        model_paths = {
            "binary": BINARY_MODEL,
            "banknote": BANKNOTE_MODEL,
            "coin": COIN_MODEL,
        }

        init_detector(model_paths, device=DEVICE)

        logger.info("=" * 50)
        logger.info("MKD Currency Detector API Started")
        logger.info(f"Device: {DEVICE}")
        logger.info(f"Preprocessing: {USE_PREPROCESSING}")
        logger.info(f"Ensemble voting: {USE_ENSEMBLE}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        raise


# =========================
# HELPERS
# =========================
def mk_detection_message(detections: list) -> str:
    if not detections:
        return "Не е детектирана валута."

    names = {
        "2000_note": "две илјади денари",
        "1000_note": "илјада денари",
        "500_note": "петстотини денари",
        "200_note": "двесте денари",
        "100_note": "сто денари",
        "50_note": "педесет денари",
        "10_note": "десет денари",
        "50_coin": "педесет денари",
        "10_coin": "десет денари",
        "5_coin": "пет денари",
        "2_coin": "два денари",
        "1_coin": "еден денар",
    }

    first = detections[0]["class_name"]
    value = names.get(first, first.replace("_", " "))

    if first.endswith("note"):
        return f"Детектирана банкнота од {value}"
    elif first.endswith("coin"):
        return f"Детектирана монета од {value}"
    else:
        return f"Детектирана валута {value}"


# =========================
# ROUTES
# =========================
@app.get("/")
async def root():
    return {
        "name": "MKD Currency Detector API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "detect": "/detect (POST)",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "device": DEVICE,
        "preprocessing": USE_PREPROCESSING,
        "ensemble": USE_ENSEMBLE,
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...), extract_images: bool = True):
    try:
        contents = await file.read()

        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Max size {MAX_IMAGE_SIZE / (1024 * 1024):.1f}MB",
            )

        try:
            pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")

        result = detect_currency(image)

        if not result.get("success", False):
            return JSONResponse(
                {
                    "success": False,
                    "message": result.get("message", "No currency detected"),
                    "type": None,
                    "detections": [],
                    "count": 0,
                    "tts_audio": None,
                }
            )

        detected_type = result.get("type")
        detections_formatted = []

        for i, det in enumerate(result.get("detections", [])):
            data = {
                "id": i,
                "class_name": det["class_name"],
                "confidence": det.get("ensemble_confidence", det["confidence"]),
                "bbox": det["bbox"],
            }

            if extract_images:
                try:
                    extracted = extract_single_currency(
                        image, det["bbox"], detected_type
                    )
                    _, buffer = cv2.imencode(".png", extracted)
                    data["image"] = (
                        "data:image/png;base64,"
                        + base64.b64encode(buffer).decode()
                    )
                except Exception:
                    data["image"] = None

            detections_formatted.append(data)

        # 🔊 ELEVENLABS TTS
        try:
            message = mk_detection_message(detections_formatted)
            audio_bytes = text_to_speech(message)
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.warning(f"TTS failed: {e}")
            audio_b64 = None

        return JSONResponse(
            {
                "success": True,
                "type": detected_type,
                "detections": detections_formatted,
                "count": len(detections_formatted),
                "tts_audio": audio_b64,  # 👈 FRONTEND CAN PLAY THIS
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "detections": [],
                "count": 0,
                "tts_audio": None,
            },
        )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
