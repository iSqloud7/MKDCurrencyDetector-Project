# ============================================================================
# tests/advanced_diagnose.py
# Advanced diagnostic with threshold testing
# Usage: python tests/advanced_diagnose.py path/to/image.jpg
# ============================================================================

import sys
import cv2
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL, DEVICE
from services.inference import CurrencyDetector

def test_with_threshold(detector, image, binary_thresh, specific_thresh, name):
    """Test detection with specific thresholds."""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"Binary: {binary_thresh:.2f}, Specific: {specific_thresh:.2f}")
    print(f"{'='*70}")

    # Save original thresholds
    orig_binary = detector.binary_threshold
    orig_banknote = detector.banknote_threshold
    orig_coin = detector.coin_threshold

    # Set new thresholds
    detector.binary_threshold = binary_thresh
    detector.banknote_threshold = specific_thresh
    detector.coin_threshold = specific_thresh

    # Run detection
    result = detector.detect(image, use_preprocessing=True, use_ensemble=True)

    # Restore thresholds
    detector.binary_threshold = orig_binary
    detector.banknote_threshold = orig_banknote
    detector.coin_threshold = orig_coin

    # Print results
    if result['success']:
        print(f"✅ Type: {result['type']}, Count: {len(result['detections'])}")
        for i, det in enumerate(result['detections'], 1):
            conf = det.get('ensemble_confidence', det['confidence'])
            print(f"   {i}. {det['class_name']}: {conf:.2%}")
    else:
        print(f"❌ {result['message']}")

    return result


def test_individual_models(detector, image):
    """Test each model individually."""
    print(f"\n{'='*70}")
    print("INDIVIDUAL MODEL TESTING")
    print(f"{'='*70}")

    # Binary model
    print("\n1. Binary Model (coin vs note):")
    binary_dets = detector.detect_with_confidence_filter(
        image, detector.models['binary'], 0.15
    )
    if binary_dets:
        for det in binary_dets:
            print(f"   {det['class_name']}: {det['confidence']:.2%}")
    else:
        print("   No detections")

    # Banknote model
    print("\n2. Banknote Model:")
    note_dets = detector.detect_with_confidence_filter(
        image, detector.models['banknote'], 0.15
    )
    if note_dets:
        for det in note_dets:
            print(f"   {det['class_name']}: {det['confidence']:.2%}")
    else:
        print("   No detections")

    # Coin model
    print("\n3. Coin Model:")
    coin_dets = detector.detect_with_confidence_filter(
        image, detector.models['coin'], 0.15
    )
    if coin_dets:
        for det in coin_dets:
            print(f"   {det['class_name']}: {det['confidence']:.2%}")
    else:
        print("   No detections")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tests/advanced_diagnose.py <image_path>")
        return

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    print(f"\n{'='*70}")
    print("ADVANCED CURRENCY DETECTION DIAGNOSTICS")
    print(f"{'='*70}")
    print(f"Image: {Path(image_path).name}")

    # Initialize
    model_paths = {
        'binary': BINARY_MODEL,
        'banknote': BANKNOTE_MODEL,
        'coin': COIN_MODEL
    }
    detector = CurrencyDetector(model_paths, device=DEVICE)

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image")
        return

    print(f"Image size: {image.shape[1]}x{image.shape[0]}")

    # Test individual models
    test_individual_models(detector, image)

    # Test with different thresholds
    print(f"\n{'='*70}")
    print("THRESHOLD TESTING")
    print(f"{'='*70}")

    threshold_configs = [
        (0.35, 0.45, "Current (Conservative)"),
        (0.25, 0.30, "Moderate"),
        (0.20, 0.25, "Aggressive"),
        (0.15, 0.20, "Very Aggressive"),
    ]

    best_result = None
    best_count = 0
    best_name = ""

    for binary_t, specific_t, name in threshold_configs:
        result = test_with_threshold(detector, image, binary_t, specific_t, name)
        count = len(result.get('detections', []))
        if count > best_count:
            best_count = count
            best_result = result
            best_name = name

    # Summary
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print(f"{'='*70}")
    print(f"\nBest result: {best_name} ({best_count} detections)")
    
    if best_count > 0:
        print("\nUpdate core/config.py with:")
        if "Very Aggressive" in best_name:
            print("   BINARY_CONFIDENCE = 0.15")
            print("   BANKNOTE_CONFIDENCE = 0.20")
            print("   COIN_CONFIDENCE = 0.20")
        elif "Aggressive" in best_name:
            print("   BINARY_CONFIDENCE = 0.20")
            print("   BANKNOTE_CONFIDENCE = 0.25")
            print("   COIN_CONFIDENCE = 0.25")
        else:
            print("   BINARY_CONFIDENCE = 0.25")
            print("   BANKNOTE_CONFIDENCE = 0.30")
            print("   COIN_CONFIDENCE = 0.30")


if __name__ == "__main__":
    main()
