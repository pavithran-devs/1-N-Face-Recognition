"""Abstract interface for face detection."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


@dataclass
class FaceDetection:
    """Result from a single detected face."""
    bbox: np.ndarray           # shape (4,): x1, y1, x2, y2
    landmarks: np.ndarray      # shape (5, 2): five facial landmarks
    confidence: float          # detection score [0, 1]
    kps: np.ndarray = field(default_factory=lambda: np.zeros((5, 2)))

    @property
    def area(self) -> float:
        x1, y1, x2, y2 = self.bbox
        return float(max(0.0, x2 - x1) * max(0.0, y2 - y1))

    @property
    def width(self) -> float:
        return float(max(0.0, self.bbox[2] - self.bbox[0]))

    @property
    def height(self) -> float:
        return float(max(0.0, self.bbox[3] - self.bbox[1]))


class FaceDetector(ABC):
    """Abstract base class for face detectors."""

    @abstractmethod
    def load(self) -> None:
        """Load model weights into memory."""
        ...

    @abstractmethod
    def detect(self, image: np.ndarray) -> list[FaceDetection]:
        """
        Detect faces in an image.

        Args:
            image: BGR image as numpy array (H, W, 3) uint8.

        Returns:
            List of FaceDetection; empty if no faces found.
        """
        ...

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """True if the model has been loaded."""
        ...
