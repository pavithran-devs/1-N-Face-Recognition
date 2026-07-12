"""SCRFD face detector backed by InsightFace's FaceAnalysis."""

import numpy as np
from loguru import logger

from app.config.settings import get_settings
from app.recognition.detector.base import FaceDetection, FaceDetector


class SCRFDDetector(FaceDetector):
    """
    Wraps InsightFace FaceAnalysis to provide SCRFD detection.
    The model pack (buffalo_l) is auto-downloaded on first use if not present,
    or loaded from configured cache.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._app: object | None = None

    def load(self) -> None:
        """Initialise InsightFace FaceAnalysis and prepare models."""
        try:
            from insightface.app import FaceAnalysis

            logger.info(
                "Loading InsightFace model pack for detection: {}",
                self._settings.insightface_model_pack,
            )
            # Create FaceAnalysis with only detection enabled
            self._app = FaceAnalysis(
                root="/home/pavithranraj/.insightface",
                name=self._settings.insightface_model_pack,
                allowed_modules=["detection"],
                providers=["CPUExecutionProvider"],
            )
            self._app.prepare(ctx_id=-1, det_size=(640, 640))
            logger.info("SCRFD detector loaded successfully.")
        except Exception as exc:
            logger.error("Failed to load SCRFD detector: {}", exc)
            raise

    @property
    def is_loaded(self) -> bool:
        return self._app is not None

    def detect(self, image: np.ndarray) -> list[FaceDetection]:
        """
        Run SCRFD detection on a BGR uint8 image.

        Raises:
            RuntimeError: if the model has not been loaded.
        """
        if not self.is_loaded:
            raise RuntimeError("SCRFDDetector.load() must be called before detect().")

        faces = self._app.get(image)  # type: ignore[union-attr]
        detections: list[FaceDetection] = []

        for face in faces:
            bbox = face.bbox.astype(np.float32)
            kps = (
                face.kps.astype(np.float32)
                if face.kps is not None
                else np.zeros((5, 2), dtype=np.float32)
            )
            score = float(face.det_score)
            detections.append(
                FaceDetection(
                    bbox=bbox,
                    landmarks=kps,
                    confidence=score,
                    kps=kps,
                )
            )

        # Sort by bounding box area descending (largest face first)
        detections.sort(key=lambda d: d.area, reverse=True)
        return detections
