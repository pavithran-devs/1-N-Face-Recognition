"""Abstract interface for face alignment."""
from abc import ABC, abstractmethod

import numpy as np


class FaceAligner(ABC):
    """Abstract base class for face aligners."""

    @abstractmethod
    def align(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """
        Align a face using 5-point landmarks.

        Args:
            image:     BGR uint8 image (H, W, 3).
            landmarks: (5, 2) float32 array of facial keypoints.

        Returns:
            Aligned face crop as BGR uint8 array (112, 112, 3).
        """
        ...
