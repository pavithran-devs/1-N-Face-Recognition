"""
FaceRecognitionPipeline — uses a single InsightFace FaceAnalysis instance
for both SCRFD detection and ArcFace embedding, which is the intended usage.

detect → quality-check → align (norm_crop) → embed (ArcFace) → L2-normalize
"""
from dataclasses import dataclass, field
from time import perf_counter

import numpy as np
from loguru import logger

from app.recognition.detector.base import FaceDetection
from app.recognition.quality.base import QualityResult
from app.recognition.quality.checks import CompositeQualityChecker, QualityThresholds


@dataclass
class PipelineResult:
    """Output from a successful pipeline run."""
    embedding: np.ndarray          # (512,) float32, L2-normalised
    embedding_dim: int
    model_name: str
    normalized: bool
    detection: FaceDetection
    quality: QualityResult
    timings: dict[str, float] = field(default_factory=dict)


@dataclass
class PipelineError:
    """Returned when the pipeline cannot produce an embedding."""
    quality: QualityResult
    message: str


class FaceRecognitionPipeline:
    """
    Singleton-style pipeline — call `load()` once at startup,
    then call `process()` per request.

    Uses InsightFace FaceAnalysis for detection + alignment + ArcFace embedding.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        from app.config.settings import get_settings
        self._settings = get_settings()
        self._app: object | None = None
        self._rec_model: object | None = None
        self._checker = CompositeQualityChecker(thresholds)
        self._loaded = False

    def load(self) -> None:
        """Load InsightFace models. Call once during application startup."""
        from insightface.app import FaceAnalysis

        logger.info("Loading FaceRecognitionPipeline (InsightFace buffalo_l)…")
        t0 = perf_counter()

        self._app = FaceAnalysis(
            name=self._settings.insightface_model_pack,
            providers=["CPUExecutionProvider"],
        )
        self._app.prepare(ctx_id=-1, det_size=(640, 640))  # type: ignore[union-attr]
        self._rec_model = self._app.models.get("recognition")  # type: ignore[union-attr]

        if self._rec_model is None:
            raise RuntimeError("ArcFace recognition model not found in buffalo_l pack.")

        self._loaded = True
        logger.info("Pipeline ready in {:.2f}s.", perf_counter() - t0)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def process(self, image: np.ndarray) -> PipelineResult | PipelineError:
        """
        Run the full pipeline on a BGR uint8 image.

        Returns:
            PipelineResult on success, PipelineError on quality failure.
        """
        if not self._loaded:
            raise RuntimeError("Pipeline not loaded. Call FaceRecognitionPipeline.load() first.")

        timings: dict[str, float] = {}

        # 1. Detect faces using InsightFace
        t0 = perf_counter()
        faces = self._app.get(image)  # type: ignore[union-attr]
        timings["detection"] = perf_counter() - t0

        # Convert to our FaceDetection dataclass list
        detections: list[FaceDetection] = []
        for face in faces:
            bbox = face.bbox.astype(np.float32)
            kps = face.kps.astype(np.float32) if face.kps is not None else np.zeros((5, 2), dtype=np.float32)
            detections.append(FaceDetection(
                bbox=bbox,
                landmarks=kps,
                confidence=float(face.det_score),
                kps=kps,
            ))

        # 2. Quality check
        t0 = perf_counter()
        quality = self._checker.validate(image, detections)
        timings["quality"] = perf_counter() - t0

        if not quality.passed:
            logger.debug("Quality check failed: {} — {}", quality.code, quality.message)
            return PipelineError(quality=quality, message=quality.message)

        best_face = faces[0]
        best_detection = detections[0]

        # 3. Align (norm_crop 112×112)
        t0 = perf_counter()
        from insightface.utils import face_align
        aligned = face_align.norm_crop(image, landmark=best_face.kps, image_size=112)
        timings["alignment"] = perf_counter() - t0

        # 4. Embed + L2-normalise
        t0 = perf_counter()
        embedding = self._rec_model.get_feat(aligned).flatten().astype(np.float32)  # type: ignore[union-attr]
        norm = np.linalg.norm(embedding)
        if norm > 1e-10:
            embedding = embedding / norm
        timings["embedding"] = perf_counter() - t0

        logger.debug(
            "Pipeline completed in {:.3f}s total. Embedding norm={:.4f}",
            sum(timings.values()),
            float(np.linalg.norm(embedding)),
        )

        return PipelineResult(
            embedding=embedding,
            embedding_dim=embedding.shape[0],
            model_name="buffalo_l/w600k_r50",
            normalized=True,
            detection=best_detection,
            quality=quality,
            timings=timings,
        )
