import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrencyDetector:
    def __init__(self, model_paths: Dict[str, str], device: str = 'cuda'):
        self.device = device
        self.models = {}

        # Confidence thresholds - ADJUST THESE FOR BETTER ACCURACY
        self.binary_threshold = 0.35
        self.banknote_threshold = 0.45
        self.coin_threshold = 0.45
        self.iou_threshold = 0.5

        for name, path in model_paths.items():
            try:
                self.models[name] = YOLO(path)
                logger.info(f"✅ Loaded {name} model")
            except Exception as e:
                logger.error(f"❌ Failed to load {name} model: {e}")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better detection"""
        try:
            # Convert grayscale to BGR if needed
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            # Enhance contrast using CLAHE
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

            # Reduce noise
            denoised = cv2.fastNlMeansDenoisingColored(
                enhanced, None, 10, 10, 7, 21
            )

            return denoised
        except Exception as e:
            logger.warning(f"Preprocessing failed: {e}, using original image")
            return image

    def detect_with_confidence_filter(
            self,
            image: np.ndarray,
            model: YOLO,
            conf_threshold: float
    ) -> List[Dict]:
        """Run detection and filter by confidence"""
        try:
            results = model(
                image,
                conf=conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )

            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        'bbox': box.xyxy[0].cpu().numpy().tolist(),
                        'confidence': float(box.conf[0]),
                        'class_id': int(box.cls[0]),
                        'class_name': model.names[int(box.cls[0])]
                    }
                    detections.append(detection)

            return detections
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []

    def calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """Calculate IoU between two bounding boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2

        inter_xmin = max(x1_min, x2_min)
        inter_ymin = max(y1_min, y2_min)
        inter_xmax = min(x1_max, x2_max)
        inter_ymax = min(y1_max, y2_max)

        inter_area = max(0, inter_xmax - inter_xmin) * max(0, inter_ymax - inter_ymin)

        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area > 0 else 0

    def ensemble_vote(
            self,
            binary_dets: List[Dict],
            specific_dets: List[Dict]
    ) -> List[Dict]:
        """Combine binary and specific model predictions"""
        if not binary_dets or not specific_dets:
            return specific_dets

        matched_dets = []

        for binary_det in binary_dets:
            best_match = None
            best_iou = 0.3  # Minimum IoU threshold

            for specific_det in specific_dets:
                iou = self.calculate_iou(
                    binary_det['bbox'],
                    specific_det['bbox']
                )

                if iou > best_iou:
                    best_iou = iou
                    best_match = specific_det.copy()

            if best_match:
                # Combine confidence scores
                best_match['binary_confidence'] = binary_det['confidence']
                best_match['ensemble_confidence'] = max(
                    binary_det['confidence'],
                    best_match['confidence']
                )

                matched_dets.append(best_match)

        return matched_dets if matched_dets else specific_dets

    def detect(
            self,
            image: np.ndarray,
            use_preprocessing: bool = False,
            use_ensemble: bool = True
    ) -> Dict:
        """
        Main detection pipeline

        Args:
            image: Input image (BGR format)
            use_preprocessing: Apply image enhancement
            use_ensemble: Use ensemble voting for better accuracy

        Returns:
            Detection results dictionary
        """
        # Preprocess image
        if use_preprocessing:
            processed_image = self.preprocess_image(image)
        else:
            processed_image = image

        # Step 1: Binary classification (coin vs note)
        binary_dets = self.detect_with_confidence_filter(
            processed_image,
            self.models['binary'],
            self.binary_threshold
        )

        if not binary_dets:
            return {
                'success': False,
                'message': 'Не е детектирана валута',
                'type': None,
                'detections': []
            }

        # Determine currency type
        currency_type = binary_dets[0]['class_name']

        # Step 2: Specific classification
        if currency_type == 'note':
            specific_model = self.models.get('banknote')
            conf_threshold = self.banknote_threshold
            type_name = 'banknote'
        else:
            specific_model = self.models.get('coin')
            conf_threshold = self.coin_threshold
            type_name = 'coin'

        if specific_model is None:
            return {
                'success': False,
                'message': f'{type_name} модел не е вчитан',
                'type': currency_type,
                'detections': []
            }

        specific_dets = self.detect_with_confidence_filter(
            processed_image,
            specific_model,
            conf_threshold
        )

        if not specific_dets:
            return {
                'success': False,
                'message': f'Не е детектирана специфична класа за {type_name}',
                'type': currency_type,
                'detections': []
            }

        # Step 3: Ensemble voting
        if use_ensemble:
            final_dets = self.ensemble_vote(binary_dets, specific_dets)
        else:
            final_dets = specific_dets

        # Sort by confidence
        final_dets.sort(
            key=lambda x: x.get('ensemble_confidence', x['confidence']),
            reverse=True
        )

        # Filter: Keep only detections above minimum confidence
        MIN_FINAL_CONFIDENCE = 0.4
        final_dets = [
            d for d in final_dets
            if d.get('ensemble_confidence', d['confidence']) >= MIN_FINAL_CONFIDENCE
        ]

        if not final_dets:
            return {
                'success': False,
                'message': 'Детекцијата е со ниска сигурност',
                'type': currency_type,
                'detections': []
            }

        return {
            'success': True,
            'type': currency_type,
            'detections': final_dets,
            'message': f'Детектирани {len(final_dets)} објекти'
        }
detector = None

def init_detector(model_paths: Dict[str, str], device: str = 'cuda'):
    """Initialize the global detector"""
    global detector
    detector = CurrencyDetector(model_paths, device)
    return detector

def detect_currency(image: np.ndarray) -> Dict:
    """
    Wrapper function for backward compatibility

    Args:
        image: Input image (BGR format)

    Returns:
        Detection results
    """
    if detector is None:
        raise RuntimeError("Detector not initialized. Call init_detector() first.")

    return detector.detect(
        image,
        use_preprocessing=True,
        use_ensemble=True
    )