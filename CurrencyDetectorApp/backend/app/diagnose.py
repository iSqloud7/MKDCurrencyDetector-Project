"""
Diagnostic script to test currency detection
Usage: python diagnose.py path/to/image.jpg
"""

import sys
import cv2
from pathlib import Path

from config import BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL, DEVICE
from utils.inference import init_detector


def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose.py <image_path>")
        return

    image_path = sys.argv[1]

    # Initialize detector
    model_paths = {
        'binary': BINARY_MODEL,
        'banknote': BANKNOTE_MODEL,
        'coin': COIN_MODEL
    }

    detector = init_detector(model_paths, device=DEVICE)

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return

    print(f"\n{'=' * 70}")
    print(f"DIAGNOSING: {Path(image_path).name}")
    print(f"{'=' * 70}\n")

    # Test with different settings
    print("Test 1: With preprocessing and ensemble")
    result1 = detector.detect(image, use_preprocessing=True, use_ensemble=True)
    print_results(result1)

    print("\nTest 2: Without preprocessing")
    result2 = detector.detect(image, use_preprocessing=False, use_ensemble=True)
    print_results(result2)

    print("\nTest 3: Without ensemble")
    result3 = detector.detect(image, use_preprocessing=True, use_ensemble=False)
    print_results(result3)

    # Visualize
    if result1['success']:
        annotated = image.copy()
        for det in result1['detections']:
            x1, y1, x2, y2 = map(int, det['bbox'])
            conf = det.get('ensemble_confidence', det['confidence'])
            label = f"{det['class_name']}: {conf:.2%}"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        output_path = f"diagnosed_images/diagnosed_{Path(image_path).name}"
        cv2.imwrite(output_path, annotated)
        print(f"\n💾 Saved annotated image: {output_path}")


def print_results(result):
    if result['success']:
        print(f"✅ Type: {result['type']}")
        for i, det in enumerate(result['detections'], 1):
            conf = det.get('ensemble_confidence', det['confidence'])
            print(f"   {i}. {det['class_name']}: {conf:.2%}")
    else:
        print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()