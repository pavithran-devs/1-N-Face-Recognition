"""Face aligner using InsightFace's norm_crop utility."""
import numpy as np

from app.recognition.aligner.base import FaceAligner


class InsightFaceAligner(FaceAligner):
    """
    Uses InsightFace's `norm_crop` to produce 112×112 aligned face crops.
    No model loading required — pure geometry.
    """

    def __init__(self, image_size: int = 112) -> None:
        self._image_size = image_size

    def align(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """
        Align face to a canonical 112×112 frame.

        Args:
            image:     BGR uint8 image.
            landmarks: (5, 2) float32 facial keypoints from SCRFD.

        Returns:
            112×112 BGR uint8 aligned crop.
        """
        from insightface.utils import face_align

        aligned: np.ndarray = face_align.norm_crop(
            image,
            landmark=landmarks,
            image_size=self._image_size,
        )
        return aligned
