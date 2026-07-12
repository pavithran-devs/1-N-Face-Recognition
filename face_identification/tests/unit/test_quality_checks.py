"""Unit tests for the CompositeQualityChecker face quality validation."""

import numpy as np
import pytest

from app.recognition.detector.base import FaceDetection
from app.recognition.quality.base import QualityCode
from app.recognition.quality.checks import CompositeQualityChecker


@pytest.fixture
def checker() -> CompositeQualityChecker:
    return CompositeQualityChecker()


def test_quality_check_pass(checker) -> None:
    # 3D model landmarks: left eye, right eye, nose, left mouth, right mouth
    # Create matching 2D landmarks for a perfectly frontal face
    landmarks = np.array(
        [
            [100, 100],  # Left Eye
            [200, 100],  # Right Eye
            [150, 150],  # Nose
            [110, 200],  # Left Mouth
            [190, 200],  # Right Mouth
        ],
        dtype=np.float32,
    )

    bbox = np.array([50, 50, 250, 250], dtype=np.float32)
    detection = FaceDetection(bbox=bbox, landmarks=landmarks, confidence=0.9)

    # Form a mock grey/BGR image that is lit correctly (mean 127) and has texture (no blur)
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    image[::2, ::2] = 127
    image[1::2, 1::2] = 130

    res = checker.validate(image, [detection])
    assert res.passed is True
    assert res.code == QualityCode.OK


def test_quality_check_low_resolution(checker) -> None:
    # Small image (100x100 is below min threshold 160)
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    res = checker.validate(image, [])
    assert res.passed is False
    assert res.code == QualityCode.LOW_RESOLUTION


def test_quality_check_no_face(checker) -> None:
    image = np.ones((200, 200, 3), dtype=np.uint8) * 127
    res = checker.validate(image, [])
    assert res.passed is False
    assert res.code == QualityCode.NO_FACE


def test_quality_check_multiple_faces(checker) -> None:
    image = np.ones((200, 200, 3), dtype=np.uint8) * 127
    d1 = FaceDetection(bbox=np.array([10, 10, 50, 50]), landmarks=np.zeros((5, 2)), confidence=0.9)
    d2 = FaceDetection(
        bbox=np.array([60, 60, 100, 100]), landmarks=np.zeros((5, 2)), confidence=0.9
    )

    res = checker.validate(image, [d1, d2])
    assert res.passed is False
    assert res.code == QualityCode.MULTIPLE_FACES


def test_quality_check_too_dark(checker) -> None:
    # Completely black image
    image = np.zeros((200, 200, 3), dtype=np.uint8)
    d = FaceDetection(bbox=np.array([10, 10, 100, 100]), landmarks=np.zeros((5, 2)), confidence=0.9)
    res = checker.validate(image, [d])
    assert res.passed is False
    assert res.code == QualityCode.TOO_DARK


def test_quality_check_too_bright(checker) -> None:
    # Completely white image
    image = np.ones((200, 200, 3), dtype=np.uint8) * 255
    d = FaceDetection(bbox=np.array([10, 10, 100, 100]), landmarks=np.zeros((5, 2)), confidence=0.9)
    res = checker.validate(image, [d])
    assert res.passed is False
    assert res.code == QualityCode.TOO_BRIGHT


def test_quality_check_face_too_small(checker) -> None:
    image = np.ones((200, 200, 3), dtype=np.uint8) * 127
    # 10x10 area = 100px (below min 2500 area)
    d = FaceDetection(bbox=np.array([10, 10, 20, 20]), landmarks=np.zeros((5, 2)), confidence=0.9)
    res = checker.validate(image, [d])
    assert res.passed is False
    assert res.code == QualityCode.FACE_TOO_SMALL


def test_quality_check_occluded_out_of_bounds(checker) -> None:
    image = np.random.randint(100, 150, (300, 300, 3), dtype=np.uint8)
    # Frontal landmarks to pass pose checks
    landmarks = np.array(
        [
            [100, 100],  # Left Eye
            [200, 100],  # Right Eye
            [150, 150],  # Nose
            [110, 200],  # Left Mouth
            [190, 200],  # Right Mouth
        ],
        dtype=np.float32,
    )
    # Small bounding box (100x100, area=10000px² > 2500px²) that excludes the eye/mouth landmarks
    d = FaceDetection(bbox=np.array([120, 120, 220, 220]), landmarks=landmarks, confidence=0.9)
    res = checker.validate(image, [d])
    assert res.passed is False
    assert res.code == QualityCode.HEAVY_OCCLUSION
