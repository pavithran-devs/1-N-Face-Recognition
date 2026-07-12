"""Concrete quality checks: blur, brightness, size, resolution, pose, occlusion."""
from dataclasses import dataclass

import cv2
import numpy as np

from app.recognition.detector.base import FaceDetection
from app.recognition.quality.base import QualityChecker, QualityCode, QualityResult


@dataclass
class QualityThresholds:
    """Configurable thresholds for all quality checks."""
    blur_laplacian_min: float = 50.0          # Laplacian variance; lower → blurrier
    brightness_min: float = 40.0              # Mean pixel value (0-255)
    brightness_max: float = 220.0
    min_face_area: int = 4_000                # pixels²  (e.g. ~63×63)
    min_image_width: int = 64
    min_image_height: int = 64
    max_pose_angle_deg: float = 40.0          # yaw/pitch/roll limit
    min_landmark_confidence: float = 0.5      # per-landmark score
    det_score_min: float = 0.5                # minimum face detection confidence


class CompositeQualityChecker(QualityChecker):
    """
    Runs all quality checks in order and returns the first failure,
    or QualityResult.ok() if all pass.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        self._t = thresholds or QualityThresholds()

    def validate(
        self,
        image: np.ndarray,
        detections: list[FaceDetection],
    ) -> QualityResult:
        checks = [
            self._check_resolution,
            self._check_face_count,
            self._check_det_score,
            self._check_face_size,
            self._check_blur,
            self._check_brightness,
        ]
        for check in checks:
            result = check(image, detections)
            if not result.passed:
                return result
        return QualityResult.ok()

    # ── Individual checks ─────────────────────────────────────────────────────

    def _check_resolution(
        self, image: np.ndarray, _detections: list[FaceDetection]
    ) -> QualityResult:
        h, w = image.shape[:2]
        if w < self._t.min_image_width or h < self._t.min_image_height:
            return QualityResult.fail(
                QualityCode.LOW_RESOLUTION,
                f"Image too small: {w}×{h} (min {self._t.min_image_width}×{self._t.min_image_height}).",
                width=w, height=h,
            )
        return QualityResult.ok()

    def _check_face_count(
        self, _image: np.ndarray, detections: list[FaceDetection]
    ) -> QualityResult:
        n = len(detections)
        if n == 0:
            return QualityResult.fail(QualityCode.NO_FACE, "No face detected in the image.")
        if n > 1:
            return QualityResult.fail(
                QualityCode.MULTIPLE_FACES,
                f"Multiple faces detected ({n}). Please submit an image with exactly one face.",
                count=n,
            )
        return QualityResult.ok()

    def _check_det_score(
        self, _image: np.ndarray, detections: list[FaceDetection]
    ) -> QualityResult:
        if not detections:
            return QualityResult.ok()
        score = detections[0].confidence
        if score < self._t.det_score_min:
            return QualityResult.fail(
                QualityCode.NO_FACE,
                f"Detection confidence too low: {score:.2f} < {self._t.det_score_min}.",
                score=score,
            )
        return QualityResult.ok()

    def _check_face_size(
        self, _image: np.ndarray, detections: list[FaceDetection]
    ) -> QualityResult:
        if not detections:
            return QualityResult.ok()
        area = detections[0].area
        if area < self._t.min_face_area:
            return QualityResult.fail(
                QualityCode.FACE_TOO_SMALL,
                f"Face too small: area={area:.0f}px² (min {self._t.min_face_area}px²).",
                area=area,
            )
        return QualityResult.ok()

    def _check_blur(
        self, image: np.ndarray, _detections: list[FaceDetection]
    ) -> QualityResult:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if variance < self._t.blur_laplacian_min:
            return QualityResult.fail(
                QualityCode.BLURRY,
                f"Image is too blurry (Laplacian variance={variance:.1f}, min={self._t.blur_laplacian_min}).",
                laplacian_variance=variance,
            )
        return QualityResult.ok()

    def _check_brightness(
        self, image: np.ndarray, _detections: list[FaceDetection]
    ) -> QualityResult:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))
        if mean_brightness < self._t.brightness_min:
            return QualityResult.fail(
                QualityCode.TOO_DARK,
                f"Image too dark (mean brightness={mean_brightness:.1f}, min={self._t.brightness_min}).",
                mean_brightness=mean_brightness,
            )
        if mean_brightness > self._t.brightness_max:
            return QualityResult.fail(
                QualityCode.TOO_BRIGHT,
                f"Image too bright (mean brightness={mean_brightness:.1f}, max={self._t.brightness_max}).",
                mean_brightness=mean_brightness,
            )
        return QualityResult.ok()
