import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List, Optional
from core.config import (
    DEVICE,
    BINARY_CONFIDENCE,
    BANKNOTE_CONFIDENCE,
    COIN_CONFIDENCE,
)
from services.preprocess import preprocess_image
from core.logging import get_logger

logger = get_logger(__name__)


class CurrencyDetector:
    def __init__(self, model_paths: Dict[str, str], device: str = DEVICE):
        self.device = device
        self.models: Dict[str, YOLO] = {}

        self.binary_threshold = BINARY_CONFIDENCE
        self.banknote_threshold = BANKNOTE_CONFIDENCE
        self.coin_threshold = COIN_CONFIDENCE
        self.iou_threshold = 0.5

        for name, path in model_paths.items():
            try:
                self.models[name] = YOLO(str(path))
                logger.info(f"Loaded {name} model from {path}")
            except Exception as e:
                logger.error(f"Failed to load {name} model: {e}")
                raise

    def detect_with_confidence_filter(
            self,
            image: np.ndarray,
            model: YOLO,
            conf_threshold: float
    ) -> List[Dict]:

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

    @staticmethod
    def calculate_iou(box1: List[float], box2: List[float]) -> float:
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

    def ensemble_vote(self, binary_dets: List[Dict], specific_dets: List[Dict]) -> List[Dict]:
        if not binary_dets or not specific_dets:
            return specific_dets

        matched_dets = []

        for binary_det in binary_dets:
            best_match = None
            best_iou = 0.3

            for specific_det in specific_dets:
                iou = self.calculate_iou(
                    binary_det['bbox'],
                    specific_det['bbox']
                )

                if iou > best_iou:
                    best_iou = iou
                    best_match = specific_det.copy()

            if best_match:
                best_match['binary_confidence'] = binary_det['confidence']
                best_match['ensemble_confidence'] = max(
                    binary_det['confidence'],
                    best_match['confidence']
                )
                matched_dets.append(best_match)

        return matched_dets if matched_dets else specific_dets

    # def detect(self, image: np.ndarray, use_preprocessing: bool = True,
    #            use_ensemble: bool = True) -> Dict:
    #
    #     if use_preprocessing:
    #         processed_image, scale = preprocess_image(image)
    #     else:
    #         processed_image = image
    #         scale = 1.0
    #
    #     binary_dets = self.detect_with_confidence_filter(
    #         processed_image,
    #         self.models['binary'],
    #         self.binary_threshold
    #     )
    #
    #     if not binary_dets:
    #         return {
    #             'success': False,
    #             'message': 'Не е детектирана валута!',
    #             'type': None,
    #             'detections': []
    #         }
    #
    #     currency_type = binary_dets[0]['class_name']
    #
    #     if currency_type == 'note':
    #         specific_model = self.models.get('banknote')
    #         conf_threshold = self.banknote_threshold
    #         type_name = 'banknote'
    #     else:
    #         specific_model = self.models.get('coin')
    #         conf_threshold = self.coin_threshold
    #         type_name = 'coin'
    #
    #     if specific_model is None:
    #         return {
    #             'success': False,
    #             'message': f'{type_name} модел не е вчитан!',
    #             'type': currency_type,
    #             'detections': []
    #         }
    #
    #     specific_dets = self.detect_with_confidence_filter(
    #         processed_image,
    #         specific_model,
    #         conf_threshold
    #     )
    #
    #     if not specific_dets:
    #         return {
    #             'success': False,
    #             'message': f'Не е детектирана специфична класа за {type_name}!',
    #             'type': currency_type,
    #             'detections': []
    #         }
    #
    #     final_dets = (
    #         self.ensemble_vote(binary_dets, specific_dets)
    #         if use_ensemble else specific_dets
    #     )
    #
    #     final_dets.sort(
    #         key=lambda x: x.get('ensemble_confidence', x['confidence']),
    #         reverse=True
    #     )
    #
    #     MIN_FINAL_CONFIDENCE = 0.4
    #     final_dets = [
    #         d for d in final_dets
    #         if d.get('ensemble_confidence', d['confidence']) >= MIN_FINAL_CONFIDENCE
    #     ]
    #
    #     if not final_dets:
    #         return {
    #             'success': False,
    #             'message': 'Детекцијата е со ниска сигурност!',
    #             'type': currency_type,
    #             'detections': []
    #         }
    #
    #     for det in final_dets:
    #         x1, y1, x2, y2 = det["bbox"]
    #         det["bbox"] = [
    #             x1 / scale,
    #             y1 / scale,
    #             x2 / scale,
    #             y2 / scale,
    #         ]
    #
    #     return {
    #         'success': True,
    #         'type': currency_type,
    #         'detections': final_dets,
    #         'message': f'Детектирани {len(final_dets)} објекти!'
    #     }

    def detect(self, image: np.ndarray, use_preprocessing: bool = True,
               use_ensemble: bool = True) -> Dict:

        binary_image, binary_scale = preprocess_image(image)

        binary_dets = self.detect_with_confidence_filter(
            binary_image,
            self.models['binary'],
            self.binary_threshold
        )

        if not binary_dets:
            return {
                'success': False,
                'message': 'Не е детектирана валута!',
                'type': None,
                'detections': []
            }

        best_binary = max(binary_dets, key=lambda d: d['confidence'])
        currency_type = best_binary['class_name']

        if currency_type == 'note':
            processed_image, scale = preprocess_image(image)
            specific_model = self.models['banknote']
            conf_threshold = self.banknote_threshold
            type_name = 'banknote'
        else:
            processed_image = image
            scale = 1.0
            specific_model = self.models['coin']
            conf_threshold = self.coin_threshold
            type_name = 'coin'

        specific_dets = self.detect_with_confidence_filter(
            processed_image,
            specific_model,
            conf_threshold
        )

        if not specific_dets:
            return {
                'success': False,
                'message': f'Не е детектирана специфична класа за {type_name}!',
                'type': currency_type,
                'detections': []
            }

        best_specific = max(specific_dets, key=lambda d: d['confidence'])

        final_conf = best_specific['confidence']
        if final_conf < 0.4:
            return {
                'success': False,
                'message': 'Детекцијата е со ниска сигурност!',
                'type': currency_type,
                'detections': []
            }

        x1, y1, x2, y2 = best_specific["bbox"]
        best_specific["bbox"] = [
            x1 / scale,
            y1 / scale,
            x2 / scale,
            y2 / scale,
        ]

        return {
            'success': True,
            'type': currency_type,
            'detections': [best_specific],
            'message': 'Детектиран еден објект!'
        }


detector: Optional[CurrencyDetector] = None


def init_detector(model_paths: Dict[str, str], device: str = DEVICE) -> CurrencyDetector:
    global detector
    detector = CurrencyDetector(model_paths, device)
    logger.info(f"Detector initialized on {device}")
    return detector


def detect_currency(image: np.ndarray) -> Dict:
    if detector is None:
        raise RuntimeError("Detector not initialized. Call init_detector() first.")

    return detector.detect(
        image,
        use_preprocessing=True,
        use_ensemble=True
    )
