"""
Test script for currency detection with image extraction
Usage: python test_extraction.py <image_path>
"""

import sys
import cv2
import os
from pathlib import Path

from config import BINARY_MODEL, BANKNOTE_MODEL, COIN_MODEL, DEVICE
from utils.inference import init_detector
from utils.extraction import (
    extract_currency_images,
    create_display_grid,
    save_extracted_currencies
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_extraction.py <image_path>")
        return

    image_path = sys.argv[1]

    print(f"\n{'=' * 70}")
    print("CURRENCY DETECTION WITH EXTRACTION")
    print(f"{'=' * 70}\n")

    # Initialize detector
    print("Initializing detector...")
    model_paths = {
        'binary': BINARY_MODEL,
        'banknote': BANKNOTE_MODEL,
        'coin': COIN_MODEL
    }
    detector = init_detector(model_paths, device=DEVICE)
    print("✅ Detector initialized\n")

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return

    print(f"📷 Image loaded: {image.shape[1]}x{image.shape[0]}\n")

    # Run detection
    print("🔍 Running detection...")
    result = detector.detect(
        image,
        use_preprocessing=False,
        use_ensemble=True
    )


    if not result['success']:
        print(f"❌ Detection failed: {result['message']}")
        return

    print(f"✅ Detection successful!")
    print(f"   Type: {result['type']}")
    print(f"   Count: {len(result['detections'])}\n")

    # Print detections
    print("Detected items:")
    for i, det in enumerate(result['detections'], 1):
        conf = det.get('ensemble_confidence', det['confidence'])
        print(f"  {i}. {det['class_name']}: {conf:.2%}")

    # Extract currency images
    print(f"\n{'=' * 70}")
    print("EXTRACTING CURRENCY IMAGES")
    print(f"{'=' * 70}\n")

    extracted_images = extract_currency_images(
        image,
        result['detections'],
        result['type']
    )

    print(f"✅ Extracted {len(extracted_images)} images\n")

    # Create output directory
    output_dir = os.path.join(os.path.dirname(image_path), "extracted_currencies")
    os.makedirs(output_dir, exist_ok=True)

    # Save individual extracted images
    print("💾 Saving extracted images...")
    saved_paths = save_extracted_currencies(
        extracted_images,
        result['detections'],
        output_dir,
        prefix=Path(image_path).stem
    )

    for path in saved_paths:
        print(f"   ✓ {os.path.basename(path)}")

    # Create and save grid display
    print("\n📊 Creating display grid...")
    grid = create_display_grid(
        extracted_images,
        result['detections'],
        grid_cols=3,
        cell_size=(400, 400)
    )

    grid_path = os.path.join(output_dir, f"{Path(image_path).stem}_grid.jpg")
    cv2.imwrite(grid_path, grid)
    print(f"   ✓ Grid saved: {os.path.basename(grid_path)}")

    # Save annotated original image
    print("\n🖼️  Creating annotated image...")
    annotated = image.copy()
    for det in result['detections']:
        x1, y1, x2, y2 = map(int, det['bbox'])
        conf = det.get('ensemble_confidence', det['confidence'])
        label = f"{det['class_name']}: {conf:.2%}"

        # Draw box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Draw label background
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(annotated, (x1, y1 - h - 15), (x1 + w + 10, y1), (0, 255, 0), -1)

        # Draw label text
        cv2.putText(annotated, label, (x1 + 5, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    annotated_path = os.path.join(output_dir, f"{Path(image_path).stem}_annotated.jpg")
    cv2.imwrite(annotated_path, annotated)
    print(f"   ✓ Annotated: {os.path.basename(annotated_path)}")

    print(f"\n{'=' * 70}")
    print(f"✅ ALL DONE!")
    print(f"{'=' * 70}")
    print(f"\n📁 Output directory: {output_dir}")
    print(f"   • {len(saved_paths)} individual extracted images")
    print(f"   • 1 grid display")
    print(f"   • 1 annotated original\n")


if __name__ == "__main__":
    main()