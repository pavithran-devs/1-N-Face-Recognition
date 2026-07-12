"""
FaceRecognitionPipeline — chains detection, quality check, alignment,
and ArcFace embedding extraction with micro-second latency telemetry.
"""

from dataclasses import dataclass, field
from time import perf_counter

import numpy as np
from loguru import logger

from app.recognition.aligner.insightface_aligner import InsightFaceAligner
from app.recognition.detector.base import FaceDetection
from app.recognition.detector.scrfd import SCRFDDetector
from app.recognition.embedding.arcface import ArcFaceEmbedder
from app.recognition.quality.base import QualityResult
from app.recognition.quality.checks import CompositeQualityChecker, QualityThresholds


@dataclass
class PipelineResult:
    """Output from a successful pipeline run."""

    embedding: np.ndarray  # (512,) float32, L2-normalised
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
    Modular recognition pipeline running detection, quality checks,
    alignment, and embedding extraction sequentially.
    """

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        self._detector = SCRFDDetector()
        self._aligner = InsightFaceAligner()
        self._embedder = ArcFaceEmbedder()
        self._checker = CompositeQualityChecker(thresholds)
        self._loaded = False

    def load(self) -> None:
        """Load InsightFace weights. Call once during application startup."""
        logger.info("Loading FaceRecognitionPipeline components...")
        t0 = perf_counter()

        self._detector.load()
        self._embedder.load()

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
            raise RuntimeError("Pipeline not loaded. Call load() first.")

        timings: dict[str, float] = {}

        # 1. Detection
        t0 = perf_counter()
        detections = self._detector.detect(image)
        timings["detection"] = perf_counter() - t0

        # 2. Quality check
        t0 = perf_counter()
        quality = self._checker.validate(image, detections)
        timings["quality"] = perf_counter() - t0

        if not quality.passed:
            logger.debug("Quality check failed: {} — {}", quality.code, quality.message)
            return PipelineError(quality=quality, message=quality.message)

        best_detection = detections[0]

        # 3. Alignment
        t0 = perf_counter()
        aligned = self._aligner.align(image, best_detection.landmarks)
        timings["alignment"] = perf_counter() - t0

        # 4. Embedding generation
        t0 = perf_counter()
        embedding = self._embedder.generate(aligned)
        timings["embedding"] = perf_counter() - t0

        logger.debug(
            "Pipeline completed in {:.3f}s total. Latencies (ms): "
            "Detection: {:.1f}, Quality: {:.1f}, Alignment: {:.1f}, Embedding: {:.1f}",
            sum(timings.values()),
            timings["detection"] * 1000,
            timings["quality"] * 1000,
            timings["alignment"] * 1000,
            timings["embedding"] * 1000,
        )

        return PipelineResult(
            embedding=embedding,
            embedding_dim=self._embedder.embedding_dim,
            model_name="buffalo_l/w600k_r50",
            normalized=True,
            detection=best_detection,
            quality=quality,
            timings=timings,
        )
