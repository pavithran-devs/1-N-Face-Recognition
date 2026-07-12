"""ArcFace embedding extractor backed by InsightFace."""
import numpy as np
from loguru import logger

from app.config.settings import get_settings
from app.recognition.embedding.base import FaceEmbedder


class ArcFaceEmbedder(FaceEmbedder):
    """
    Extracts 512-d embeddings using InsightFace's ArcFace model.
    Embeddings are L2-normalised before return.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model: object | None = None
        self._app: object | None = None

    def load(self) -> None:
        """Load the ArcFace model from the buffalo_l pack."""
        try:
            from insightface.app import FaceAnalysis

            logger.info("Loading ArcFace embedding model…")
            self._app = FaceAnalysis(
                name=self._settings.insightface_model_pack,
                allowed_modules=["recognition"],
                providers=["CPUExecutionProvider"],
            )
            self._app.prepare(ctx_id=-1)  # type: ignore[union-attr]
            # Grab the recogniser directly for per-crop inference
            self._model = self._app.models.get("recognition")
            logger.info("ArcFace embedder loaded successfully.")
        except Exception as exc:
            logger.error("Failed to load ArcFace embedder: {}", exc)
            raise

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def generate(self, aligned_face: np.ndarray) -> np.ndarray:
        """
        Generate a 512-d L2-normalised embedding.

        Args:
            aligned_face: BGR uint8 crop (112, 112, 3).

        Returns:
            float32 ndarray of shape (512,), L2-normalised.
        """
        if not self.is_loaded:
            raise RuntimeError("ArcFaceEmbedder.load() must be called first.")

        # InsightFace recognition model expects BGR (112, 112, 3)
        embedding: np.ndarray = self._model.get_feat(aligned_face)  # type: ignore[union-attr]
        embedding = embedding.flatten().astype(np.float32)
        return self._l2_normalize(embedding)

    @staticmethod
    def _l2_normalize(vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        if norm < 1e-10:
            return vec
        return vec / norm
