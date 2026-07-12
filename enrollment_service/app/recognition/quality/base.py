"""Abstract interface for face image quality checking."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from app.recognition.detector.base import FaceDetection


class QualityCode(str, Enum):
    OK = "ok"
    NO_FACE = "no_face"
    MULTIPLE_FACES = "multiple_faces"
    BLURRY = "blurry"
    TOO_DARK = "too_dark"
    TOO_BRIGHT = "too_bright"
    FACE_TOO_SMALL = "face_too_small"
    LOW_RESOLUTION = "low_resolution"
    EXTREME_POSE = "extreme_pose"
    HEAVY_OCCLUSION = "heavy_occlusion"


@dataclass
class QualityResult:
    passed: bool
    code: QualityCode
    message: str
    details: dict = field(default_factory=dict)

    @classmethod
    def ok(cls) -> "QualityResult":
        return cls(passed=True, code=QualityCode.OK, message="Quality check passed.")

    @classmethod
    def fail(cls, code: QualityCode, message: str, **details: object) -> "QualityResult":
        return cls(passed=False, code=code, message=message, details=dict(details))


class QualityChecker(ABC):
    """Abstract base class for face quality validators."""

    @abstractmethod
    def validate(
        self,
        image: np.ndarray,
        detections: list[FaceDetection],
    ) -> QualityResult:
        """
        Validate image quality.

        Args:
            image:      BGR uint8 image.
            detections: Face detections produced by the detector.

        Returns:
            QualityResult with passed=True or a failure code + message.
        """
        ...
