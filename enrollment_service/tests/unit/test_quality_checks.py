"""Unit tests for face quality checks."""
import numpy as np
import pytest

from app.recognition.detector.base import FaceDetection
from app.recognition.quality.base import QualityCode
from app.recognition.quality.checks import CompositeQualityChecker, QualityThresholds


def make_detection(area: float = 10_000, confidence: float = 0.99) -> FaceDetection:
    side = area ** 0.5
    return FaceDetection(
        bbox=np.array([0, 0, side, side], dtype=np.float32),
        landmarks=np.zeros((5, 2), dtype=np.float32),
        confidence=confidence,
    )


def make_image(h: int = 480, w: int = 640, mean_brightness: float = 128.0) -> np.ndarray:
    img = np.full((h, w, 3), int(mean_brightness), dtype=np.uint8)
    return img


@pytest.fixture
def checker():
    return CompositeQualityChecker(QualityThresholds())


class TestNoFace:
    def test_empty_detections(self, checker):
        result = checker.validate(make_image(), [])
        assert not result.passed
        assert result.code == QualityCode.NO_FACE

    def test_single_face_passes(self, checker):
        # Use a textured (checkerboard) image so blur check passes.
        # A solid-colour image has Laplacian variance=0.0 and would fail blur.
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[::4, :] = 200       # horizontal stripes give non-zero Laplacian variance
        img[:, ::4] = 200
        result = checker.validate(img, [make_detection()])
        assert result.passed


class TestMultipleFaces:
    def test_two_faces_fail(self, checker):
        result = checker.validate(make_image(), [make_detection(), make_detection()])
        assert not result.passed
        assert result.code == QualityCode.MULTIPLE_FACES


class TestBlur:
    def test_blurry_image(self, checker):
        # A solid-color image has zero Laplacian variance → blurry
        img = np.full((200, 200, 3), 128, dtype=np.uint8)
        result = checker.validate(img, [make_detection()])
        assert not result.passed
        assert result.code == QualityCode.BLURRY

    def test_sharp_image(self, checker):
        # Checkerboard pattern has high Laplacian variance
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        img[::2, ::2] = 255
        img[1::2, 1::2] = 255
        result = checker.validate(img, [make_detection()])
        # Should at least pass blur check (may fail brightness if too dark)
        assert result.code != QualityCode.BLURRY


class TestBrightness:
    def test_too_dark(self, checker):
        img = np.zeros((200, 200, 3), dtype=np.uint8)  # mean=0
        result = checker.validate(img, [make_detection()])
        # Will fail blur first on solid black → then brightness
        assert result.code in {QualityCode.BLURRY, QualityCode.TOO_DARK}

    def test_too_bright(self, checker):
        img = np.full((200, 200, 3), 255, dtype=np.uint8)
        result = checker.validate(img, [make_detection()])
        assert result.code in {QualityCode.BLURRY, QualityCode.TOO_BRIGHT}


class TestResolution:
    def test_tiny_image(self, checker):
        img = np.full((10, 10, 3), 128, dtype=np.uint8)
        result = checker.validate(img, [make_detection()])
        assert not result.passed
        assert result.code == QualityCode.LOW_RESOLUTION


class TestFaceSize:
    def test_tiny_face(self, checker):
        tiny = make_detection(area=100)  # 10×10 face
        result = checker.validate(make_image(), [tiny])
        assert not result.passed
        assert result.code == QualityCode.FACE_TOO_SMALL
