"""
Currency extraction utilities
Handles extraction and background removal for detected currency
"""

import cv2
import numpy as np
from typing import List, Tuple


def extract_currency_images(image: np.ndarray, detections: List[dict],
                            currency_type: str) -> List[np.ndarray]:
    """
    Extract individual currency images from detections

    Args:
        image: Original image
        detections: List of detection dictionaries with 'bbox' key
        currency_type: 'coin' or 'note'

    Returns:
        List of extracted currency images
    """
    extracted = []

    for det in detections:
        bbox = det['bbox']
        extracted_img = extract_single_currency(image, bbox, currency_type)
        extracted.append(extracted_img)

    return extracted


def extract_single_currency(image: np.ndarray, bbox: List[float],
                            currency_type: str, padding: int = 10) -> np.ndarray:
    """
    Extract a single currency from bounding box

    Args:
        image: Original image
        bbox: Bounding box [x1, y1, x2, y2]
        currency_type: 'coin' or 'note'
        padding: Extra padding around bbox

    Returns:
        Extracted currency image
    """
    x1, y1, x2, y2 = map(int, bbox)

    # Add padding
    h, w = image.shape[:2]
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)

    # Crop image
    cropped = image[y1:y2, x1:x2].copy()

    if cropped.size == 0 or cropped.shape[0] == 0 or cropped.shape[1] == 0:
        return np.zeros((100, 100, 3), dtype=np.uint8)

    # For coins, remove background
    if currency_type == 'coin':
        return remove_background_circular(cropped)
    else:
        # For banknotes, apply slight enhancement
        return enhance_banknote(cropped)


def remove_background_circular(image: np.ndarray) -> np.ndarray:
    """
    Remove background from coin using circular mask
    Returns BGRA image with transparent background

    Args:
        image: Cropped coin image (BGR)

    Returns:
        Image with transparent background (BGRA)
    """
    # Ensure BGR format
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Detect circles
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=50,
        param2=30,
        minRadius=int(min(image.shape[:2]) * 0.25),
        maxRadius=int(max(image.shape[:2]) * 0.55)
    )

    # Create mask
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    if circles is not None:
        # Use detected circle
        circles = np.uint16(np.around(circles))
        circle = circles[0, 0]
        center = (circle[0], circle[1])
        radius = int(circle[2] * 1.05)  # Slightly larger to include edges
        cv2.circle(mask, center, radius, 255, -1)
    else:
        # Fallback: use ellipse
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        axes = (int(w * 0.48), int(h * 0.48))
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)

    # Smooth mask edges for better appearance
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Apply mask to create transparent background
    bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = mask

    return bgra


def enhance_banknote(image: np.ndarray) -> np.ndarray:
    """
    Enhance banknote image (contrast, sharpness)

    Args:
        image: Cropped banknote image

    Returns:
        Enhanced image
    """
    # Increase contrast slightly
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    l = clahe.apply(l)

    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # Slight sharpening
    kernel = np.array([[-1, -1, -1],
                       [-1, 9, -1],
                       [-1, -1, -1]]) / 9
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    # Blend original and sharpened
    result = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)

    return result


def create_display_grid(images: List[np.ndarray], detections: List[dict],
                        grid_cols: int = 3, cell_size: Tuple[int, int] = (300, 300)) -> np.ndarray:
    """
    Create a grid display of extracted currency images with labels

    Args:
        images: List of extracted currency images
        detections: List of detection dictionaries
        grid_cols: Number of columns in grid
        cell_size: Size of each cell (width, height)

    Returns:
        Grid image
    """
    if not images:
        return np.zeros((cell_size[1], cell_size[0], 3), dtype=np.uint8)

    n = len(images)
    grid_rows = (n + grid_cols - 1) // grid_cols

    # Create white background
    grid_h = grid_rows * cell_size[1]
    grid_w = grid_cols * cell_size[0]
    grid = np.ones((grid_h, grid_w, 3), dtype=np.uint8) * 255

    for idx, (img, det) in enumerate(zip(images, detections)):
        row = idx // grid_cols
        col = idx % grid_cols

        # Resize image to fit cell (maintaining aspect ratio)
        h, w = img.shape[:2]
        scale = min((cell_size[0] - 40) / w, (cell_size[1] - 60) / h)
        new_w, new_h = int(w * scale), int(h * scale)

        if img.shape[2] == 4:  # BGRA (coins with transparency)
            # Composite on white background
            resized = cv2.resize(img, (new_w, new_h))
            alpha = resized[:, :, 3] / 255.0
            for c in range(3):
                resized[:, :, c] = (resized[:, :, c] * alpha +
                                    255 * (1 - alpha)).astype(np.uint8)
            resized = resized[:, :, :3]
        else:
            resized = cv2.resize(img, (new_w, new_h))

        # Calculate position (centered in cell)
        y_offset = row * cell_size[1] + (cell_size[1] - new_h) // 2
        x_offset = col * cell_size[0] + (cell_size[0] - new_w) // 2

        # Place image
        grid[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

        # Add label
        label = f"{det['class_name']}"
        conf = det.get('ensemble_confidence', det['confidence'])
        conf_text = f"({conf:.2%})"

        label_y = row * cell_size[1] + cell_size[1] - 15
        label_x = col * cell_size[0] + 20

        cv2.putText(grid, label, (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(grid, conf_text, (label_x, label_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    return grid


def save_extracted_currencies(images: List[np.ndarray], detections: List[dict],
                              output_dir: str, prefix: str = "currency") -> List[str]:
    """
    Save extracted currency images to disk

    Args:
        images: List of extracted images
        detections: List of detection dictionaries
        output_dir: Output directory
        prefix: Filename prefix

    Returns:
        List of saved file paths
    """
    import os

    os.makedirs(output_dir, exist_ok=True)
    saved_paths = []

    for idx, (img, det) in enumerate(zip(images, detections)):
        class_name = det['class_name'].replace(' ', '_')
        conf = det.get('ensemble_confidence', det['confidence'])

        filename = f"{prefix}_{idx + 1}_{class_name}_{conf:.2f}.png"
        filepath = os.path.join(output_dir, filename)

        cv2.imwrite(filepath, img)
        saved_paths.append(filepath)

    return saved_paths