"""Abstract interface for face embedding generation."""
from abc import ABC, abstractmethod

import numpy as np


class FaceEmbedder(ABC):
    """Abstract base class for face embedding models."""

    @abstractmethod
    def load(self) -> None:
        """Load model weights into memory."""
        ...

    @abstractmethod
    def generate(self, aligned_face: np.ndarray) -> np.ndarray:
        """
        Generate a face embedding from an aligned crop.

        Args:
            aligned_face: BGR uint8 aligned face crop (112, 112, 3).

        Returns:
            L2-normalised float32 embedding vector of shape (512,).
        """
        ...

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """True if the model has been loaded."""
        ...

    @property
    def embedding_dim(self) -> int:
        """Embedding dimensionality (default 512 for ArcFace)."""
        return 512
