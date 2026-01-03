"""
Comprehensive test suite for MKD Currency Detector backend
Run with: pytest test_backend.py -v
"""

import pytest
import sys
import os
from pathlib import Path
from PIL import Image
import io

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient

# ============================================================================
# FIXTURES
# ============================================================================
@pytest.fixture
def client():
    """Create FastAPI test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def sample_image():
    """Create a sample test image (640x640 RGB)"""
    img = Image.new('RGB', (640, 640), color='white')
    return img

@pytest.fixture
def image_bytes(sample_image):
    """Convert sample image to bytes"""
    img_byte_arr = io.BytesIO()
    sample_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

# ============================================================================
# GLOBAL DETECTOR INITIALIZATION
# ============================================================================
from config import BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL
from utils.inference import CurrencyDetector

model_paths = {
    "binary": BINARY_MODEL,
    "banknote": BANKNOTE_MODEL,
    "coin": COIN_MODEL
}

# Initialize once and reuse for all tests
detector = CurrencyDetector(model_paths=model_paths)

# ============================================================================
# UNIT TESTS - Config
# ============================================================================
class TestConfig:
    def test_config_imports(self):
        from config import DEVICE, IMAGE_SIZE, BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL
        assert DEVICE in ["cuda", "cpu"]
        assert IMAGE_SIZE == 640
        assert BINARY_MODEL.endswith("binary_model.pt")

    def test_model_files_exist(self):
        from config import BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL
        assert os.path.exists(BINARY_MODEL)
        assert os.path.exists(BANKNOTE_MODEL)
        assert os.path.exists(COIN_MODEL)

# ============================================================================
# UNIT TESTS - Preprocessing
# ============================================================================
class TestPreprocessing:
    def test_preprocess_image(self, sample_image):
        from utils.preprocess import preprocess_image
        processed = preprocess_image(sample_image, target_size=640)
        assert processed.shape[:2] == (640, 640)
        assert len(processed.shape) == 3

    def test_preprocess_different_sizes(self):
        from utils.preprocess import preprocess_image
        for w, h in [(100,200),(640,480),(1920,1080)]:
            img = Image.new('RGB', (w,h), color='blue')
            processed = preprocess_image(img, target_size=640)
            assert processed.shape[:2] == (640,640)

# ============================================================================
# UNIT TESTS - Inference
# ============================================================================
class TestInference:
    def test_detector_initialization(self):
        global detector
        assert 'binary' in detector.models
        assert 'banknote' in detector.models
        assert 'coin' in detector.models

    def test_detect_returns_dict(self, sample_image):
        global detector
        result = detector.detect(sample_image)
        assert isinstance(result, dict)
        assert "type" in result
        assert "detections" in result

    def test_detect_empty_image(self):
        global detector
        blank_img = Image.new('RGB', (640,640), color='black')
        result = detector.detect(blank_img)
        assert result["type"] in (None, "banknote", "coin")
        assert isinstance(result["detections"], list)

# ============================================================================
# UNIT TESTS - TTS
# ============================================================================
class TestTTS:
    def test_tts_initialization(self):
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        assert tts.language == "mk"

    def test_generate_currency_message_none(self):
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        result = {"success": True, "type": "none", "detections": []}
        message = tts.generate_currency_message(result)
        assert "не е детектирана валута" in message.lower() or "detection error" in message.lower()

    def test_generate_currency_message_banknote(self):
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        result = {
            "success": True,
            "type": "banknote",
            "detections": [{"class_name": "10_note", "confidence": 0.95}]
        }
        message = tts.generate_currency_message(result)
        assert "банкнота" in message.lower()
        assert "10 денари" in message

    def test_generate_currency_message_coin(self):
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        result = {
            "success": True,
            "type": "coin",
            "detections": [{"class_name": "5_coin", "confidence": 0.90}]
        }
        message = tts.generate_currency_message(result)
        assert "монета" in message.lower()
        assert "5 денари" in message

    def test_tts_speak(self):
        """Check that speak() runs without error (Edge TTS, won't test actual audio)"""
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        message = "Тест на говор"
        success = tts.speak(message)  # should return True
        assert success is True

    def test_announce_detection(self):
        """Check announce_detection runs with a detection dict"""
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        result = {
            "success": True,
            "type": "banknote",
            "detections": [{"class_name": "10_note", "confidence": 0.95}]
        }
        success = tts.announce_detection(result)
        assert success is True

# ============================================================================
# API TESTS
# ============================================================================
class TestAPIEndpoints:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_detect_endpoint_success(self, client, image_bytes):
        files = {"file":("test.jpg",image_bytes,"image/jpeg")}
        response = client.post("/detect", files=files)
        assert response.status_code == 200
        result = response.json()
        assert "type" in result
        assert result["type"] in (None, "banknote", "coin")

    def test_detect_endpoint_no_file(self, client):
        response = client.post("/detect")
        assert response.status_code == 422

    def test_detect_endpoint_invalid_file(self, client):
        files = {"file":("test.txt",b"not an image","text/plain")}
        response = client.post("/detect", files=files)
        assert response.status_code in [400,500]

# ============================================================================
# INTEGRATION TESTS
# ============================================================================
class TestIntegration:
    def test_full_pipeline_banknote(self, client):
        img = Image.new('RGB', (1920,1080), color=(100,150,200))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        files = {"file":("banknote.jpg",img_byte_arr,"image/jpeg")}
        response = client.post("/detect", files=files)
        assert response.status_code == 200
        result = response.json()
        assert "type" in result
        assert "detections" in result
        assert isinstance(result["detections"], list)

    def test_tts_integration(self):
        from utils.tts import TextToSpeech
        tts = TextToSpeech(language="mk")
        result = {
            "success": True,
            "type": "banknote",
            "detections": [{"class_name": "50_note", "confidence": 0.95}]
        }
        # Use announce_detection method
        success = tts.announce_detection(result)
        assert success is True

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================
class TestPerformance:
    def test_detector_inference_time(self, sample_image):
        import time
        global detector
        start = time.time()
        result = detector.detect(sample_image)
        duration = time.time() - start
        assert duration < 5.0, f"Inference too slow: {duration}s"

    def test_multiple_requests(self, client, image_bytes):
        for i in range(5):
            image_bytes.seek(0)
            files = {"file":(f"test{i}.jpg",image_bytes,"image/jpeg")}
            response = client.post("/detect", files=files)
            assert response.status_code == 200

# ============================================================================
# MAIN
# ============================================================================
if __name__=="__main__":
    pytest.main([__file__,"-v","--tb=short"])
