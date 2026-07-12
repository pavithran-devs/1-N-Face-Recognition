"""Face recognition modules packaging."""

from app.recognition.aligner.base import FaceAligner
from app.recognition.aligner.insightface_aligner import InsightFaceAligner
from app.recognition.detector.base import FaceDetection, FaceDetector
from app.recognition.detector.scrfd import SCRFDDetector
from app.recognition.embedding.arcface import ArcFaceEmbedder
from app.recognition.embedding.base import FaceEmbedder
from app.recognition.quality.base import QualityChecker, QualityCode, QualityResult
from app.recognition.quality.checks import CompositeQualityChecker, QualityThresholds

__all__ = [
    "FaceDetection",
    "FaceDetector",
    "SCRFDDetector",
    "FaceAligner",
    "InsightFaceAligner",
    "FaceEmbedder",
    "ArcFaceEmbedder",
    "QualityChecker",
    "QualityCode",
    "QualityResult",
    "CompositeQualityChecker",
    "QualityThresholds",
]
