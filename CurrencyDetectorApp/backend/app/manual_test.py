"""
Manual test script - Run without pytest
Usage: python manual_test.py [path_to_image.jpg]
"""

import sys
import os
from pathlib import Path
import requests
from PIL import Image
from utils.inference import init_detector
from config import BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL, DEVICE
import cv2
import numpy as np
import time
import io

# Configuration
BASE_URL = "http://localhost:8000"
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"


def print_success(message):
    print(f"{COLOR_GREEN}✅ {message}{COLOR_RESET}")


def print_error(message):
    print(f"{COLOR_RED}❌ {message}{COLOR_RESET}")


def print_info(message):
    print(f"{COLOR_BLUE}ℹ️  {message}{COLOR_RESET}")


def test_server_running():
    """Test if server is running"""
    print("\n" + "=" * 70)
    print("TEST 1: Server Connection")
    print("=" * 70)

    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success("Server is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        print_info("Start server with: python main.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_health_check():
    """Test health endpoint"""
    print("\n" + "=" * 70)
    print("TEST 2: Health Check")
    print("=" * 70)

    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Status: {data.get('status')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_config():
    """Test configuration files"""
    print("\n" + "=" * 70)
    print("TEST 3: Configuration")
    print("=" * 70)

    try:
        from config import DEVICE, IMAGE_SIZE, BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL

        print_success("Config imported successfully")
        print_info(f"Device: {DEVICE}")
        print_info(f"Image size: {IMAGE_SIZE}")

        # Check model files
        models = {
            "Binary": BINARY_MODEL,
            "Banknote": BANKNOTE_MODEL,
            "Coin": COIN_MODEL
        }

        all_exist = True
        for name, path in models.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print_success(f"{name} model found ({size_mb:.1f} MB)")
            else:
                print_error(f"{name} model NOT found: {path}")
                all_exist = False

        return all_exist
    except Exception as e:
        print_error(f"Config error: {e}")
        return False


def test_inference_local():
    print("\n" + "=" * 70)
    print("TEST 4: Local Inference")
    print("=" * 70)

    try:
        from utils.inference import init_detector

        model_paths = {
            "binary": BINARY_MODEL,
            "banknote": BANKNOTE_MODEL,
            "coin": COIN_MODEL
        }

        detector = init_detector(model_paths, DEVICE)
        print_success("Detector initialized successfully")

        # Create test image (numpy, BGR)
        test_img = np.ones((640, 640, 3), dtype=np.uint8) * 255
        print_info("Created test image (640x640)")

        result = detector.detect(test_img)

        print_success("Detection completed")
        print_info(f"Type: {result.get('type')}")
        print_info(f"Detections: {len(result.get('detections', []))}")

        return True

    except Exception as e:
        print_error(f"Inference error: {e}")
        import traceback
        traceback.print_exc()
        return False



def test_tts():
    """Test text-to-speech"""
    print("\n" + "=" * 70)
    print("TEST 5: Text-to-Speech")
    print("=" * 70)

    try:
        # Import the updated TTS class using Windows voices
        from utils.tts import TextToSpeech

        # Initialize TTS (language mk = Macedonian)
        tts = TextToSpeech(language="mk")
        print_success("TTS initialized")

        # Test message generation
        test_result = {
            "success": True,
            "type": "banknote",
            "detections": [{"class_name": "10 денари", "confidence": 0.95}]
        }

        message = tts.generate_currency_message(test_result)
        print_info(f"Generated message: {message}")

        # Speak the message (Windows TTS, Macedonian Latin)
        print_info("Testing speech (you should hear audio)...")
        tts.speak(message)

        # Optional: give time for audio to finish
        import time
        time.sleep(3)

        print_success("TTS test completed")
        return True
    except Exception as e:
        print_error(f"TTS error: {e}")
        return False



def test_detection_with_image(image_path):
    """Test detection with real image and speak results"""
    print("\n" + "=" * 70)
    print("TEST 6: Detection with Image")
    print("=" * 70)

    if not os.path.exists(image_path):
        print_error(f"Image not found: {image_path}")
        return False

    try:
        print_info(f"Loading image: {image_path}")

        with open(image_path, 'rb') as f:
            files = {"file": (Path(image_path).name, f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/detect", files=files)

        if response.status_code == 200:
            result = response.json()

            print_success("Detection successful")
            print_info(f"Type: {result.get('type')}")
            print_info(f"Detections: {result.get('detections', [])}")

            # Show detection details
            if result.get('detections'):
                print("\n  Detection details:")
                for i, det in enumerate(result['detections'], 1):
                    print(f"    {i}. {det.get('class_name', 'Unknown')}")
                    print(f"       Confidence: {det.get('confidence', 0):.2%}")
                    print(f"       BBox: {det.get('bbox', {})}")

            # Speak the result using TTS
            from utils.tts import get_tts
            tts = get_tts(language="mk")  # Macedonian
            tts.announce_detection(result)  # This will speak the message

            return True
        else:
            print_error(f"Detection failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_preprocessing():
    """Test image preprocessing"""
    print("\n" + "=" * 70)
    print("TEST 7: Image Preprocessing")
    print("=" * 70)

    try:
        from utils.preprocess import preprocess_image
        from PIL import Image

        # Test different sizes
        test_sizes = [(100, 200), (640, 480), (1920, 1080)]

        for w, h in test_sizes:
            img = Image.new('RGB', (w, h), color='blue')
            processed = preprocess_image(img, target_size=640)

            print_info(f"Input: {w}x{h} → Output: {processed.shape[1]}x{processed.shape[0]}")

        print_success("Preprocessing test passed")
        return True
    except Exception as e:
        print_error(f"Preprocessing error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("MKD CURRENCY DETECTOR - MANUAL TEST SUITE")
    print("=" * 70)

    results = []

    # Run tests
    results.append(("Server Connection", test_server_running()))
    results.append(("Health Check", test_health_check()))
    results.append(("Configuration", test_config()))
    results.append(("Preprocessing", test_preprocessing()))
    results.append(("Local Inference", test_inference_local()))
    results.append(("Text-to-Speech", test_tts()))

    # Test with image if provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        results.append(("Image Detection", test_detection_with_image(image_path)))
    else:
        print_info("\nSkipping image detection test (no image provided)")
        print_info("To test with image: python manual_test.py path/to/image.jpg")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_error(f"{test_name}")

    total = len(results)
    print(f"\n  Passed: {passed}/{total}")

    if passed == total:
        print_success("\n🎉 All tests passed!")
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")

    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)