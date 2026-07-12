"""Abstract interface for face alignment."""

from abc import ABC, abstractmethod

import numpy as np


class FaceAligner(ABC):
    """Abstract base class for face aligners."""

    @abstractmethod
    def align(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """
        Align face to a canonical frame.

        Args:
            image:     BGR image as numpy array (H, W, 3) uint8.
            landmarks: (5, 2) facial keypoints.

        Returns:
            Aligned BGR image crop as numpy array (112, 112, 3) uint8.
        """
        ...
