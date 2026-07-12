"""Concrete quality checks: blur, brightness, size, count, resolution, pose, occlusion."""

from dataclasses import dataclass

import cv2
import numpy as np

from app.recognition.detector.base import FaceDetection
from app.recognition.quality.base import QualityChecker, QualityCode, QualityResult


@dataclass
class QualityThresholds:
    """Configurable thresholds for all quality checks."""

    blur_laplacian_min: float = 50.0  # Laplacian variance; lower → blurrier
    brightness_min: float = 40.0  # Mean pixel value (0-255)
    brightness_max: float = 220.0
    min_face_area: int = 2_500  # support slightly smaller faces (e.g. ~50×50)
    min_image_width: int = 160  # support low-res webcams
    min_image_height: int = 160
    max_pose_angle_deg: float = 35.0  # yaw/pitch/roll limit in degrees
    det_score_min: float = 0.55  # minimum face detection confidence
    max_symmetry_ratio: float = 5.0  # max ratio between left/right sides (occlusion)


class CompositeQualityChecker(QualityChecker):
    """
    Runs all quality checks in order and returns the first failure,
    or QualityResult.ok() if all pass.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        self._t = thresholds or QualityThresholds()

        # Define canonical 3D coordinates of 5 facial landmarks for pose estimation
        # (left eye, right eye, nose, left mouth corner, right mouth corner)
        self._model_points = np.array(
            [
                [-2.25, 1.5, -2.2],  # Left Eye
                [2.25, 1.5, -2.2],  # Right Eye
                [0.0, -0.5, 0.0],  # Nose tip
                [-1.625, -2.5, -1.6],  # Left Mouth corner
                [1.625, -2.5, -1.6],  # Right Mouth corner
            ],
            dtype=np.float32,
        )

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
            self._check_brightness,
            self._check_blur,
            self._check_pose,
            self._check_occlusion,
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
                width=w,
                height=h,
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
                f"Multiple faces detected ({n}). Only single candidates allowed.",
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

    def _check_blur(self, image: np.ndarray, _detections: list[FaceDetection]) -> QualityResult:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if variance < self._t.blur_laplacian_min:
            return QualityResult.fail(
                QualityCode.BLURRY,
                f"Image too blurry (Laplacian variance={variance:.1f}, min={self._t.blur_laplacian_min}).",
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

    def _check_pose(self, image: np.ndarray, detections: list[FaceDetection]) -> QualityResult:
        """Estimate head pose (yaw, pitch, roll) from 5 landmarks using geometrical ratios."""
        if not detections:
            return QualityResult.ok()

        landmarks = detections[0].landmarks

        left_eye = landmarks[0]
        right_eye = landmarks[1]
        nose = landmarks[2]
        left_mouth = landmarks[3]
        right_mouth = landmarks[4]

        # 1. Roll: slope of the eyes line
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        roll = float(np.degrees(np.arctan2(dy, max(1e-5, dx))))

        # 2. Yaw: horizontal asymmetry between eyes and nose
        eye_midpoint_x = (left_eye[0] + right_eye[0]) / 2.0
        eye_distance_x = max(1.0, abs(right_eye[0] - left_eye[0]))
        yaw_offset = (nose[0] - eye_midpoint_x) / eye_distance_x
        # Map yaw_offset (-0.5 to 0.5) to approx degrees by multiplying by 90
        yaw = float(yaw_offset * 90.0)

        # 3. Pitch: vertical ratio of nose position between eyes and mouth
        eye_y = (left_eye[1] + right_eye[1]) / 2.0
        mouth_y = (left_mouth[1] + right_mouth[1]) / 2.0
        face_height = max(1.0, mouth_y - eye_y)

        nose_relative_y = (nose[1] - eye_y) / face_height
        # Deviations from standard frontal ratio (0.45) indicate pitch
        pitch = float((nose_relative_y - 0.45) * 120.0)

        # Threshold check
        if (
            abs(yaw) > self._t.max_pose_angle_deg
            or abs(pitch) > self._t.max_pose_angle_deg
            or abs(roll) > self._t.max_pose_angle_deg
        ):
            return QualityResult.fail(
                QualityCode.EXTREME_POSE,
                f"Pose angle exceeds limits: yaw={yaw:.1f}°, pitch={pitch:.1f}°, roll={roll:.1f}° "
                f"(max allowed {self._t.max_pose_angle_deg}°). Please look directly at the camera.",
                yaw=yaw,
                pitch=pitch,
                roll=roll,
            )

        return QualityResult.ok()

    def _check_occlusion(
        self, _image: np.ndarray, detections: list[FaceDetection]
    ) -> QualityResult:
        """Check for facial occlusion based on landmark boundaries and symmetry."""
        if not detections:
            return QualityResult.ok()

        det = detections[0]
        landmarks = det.landmarks
        x1, y1, x2, y2 = det.bbox

        # 1. Check if all keypoints lie within the bounding box (with slight margin)
        margin_w = det.width * 0.05
        margin_h = det.height * 0.05
        for idx, kp in enumerate(landmarks):
            kx, ky = kp
            if not (x1 - margin_w <= kx <= x2 + margin_w and y1 - margin_h <= ky <= y2 + margin_h):
                return QualityResult.fail(
                    QualityCode.HEAVY_OCCLUSION,
                    f"Face landmarks are outside bounding box boundary. Point {idx} is occluded.",
                    landmark_index=idx,
                    point=[kx, ky],
                    bbox=list(det.bbox),
                )

        # 2. Check facial symmetry (horizontal nose-to-eye symmetry)
        left_eye, right_eye, nose = landmarks[0], landmarks[1], landmarks[2]

        # Horizontal distance from nose to each eye
        dist_nose_left_eye = abs(nose[0] - left_eye[0])
        dist_nose_right_eye = abs(nose[0] - right_eye[0])

        # Avoid division by zero
        if dist_nose_left_eye < 1.0 or dist_nose_right_eye < 1.0:
            return QualityResult.fail(
                QualityCode.HEAVY_OCCLUSION, "Eyes are located too close to the nose center."
            )

        ratio = max(dist_nose_left_eye, dist_nose_right_eye) / min(
            dist_nose_left_eye, dist_nose_right_eye
        )
        if ratio > self._t.max_symmetry_ratio:
            return QualityResult.fail(
                QualityCode.HEAVY_OCCLUSION,
                f"Face landmarks are asymmetric, indicating occlusion: ratio={ratio:.2f} "
                f"(max allowed {self._t.max_symmetry_ratio:.2f}).",
                ratio=ratio,
            )

        return QualityResult.ok()
