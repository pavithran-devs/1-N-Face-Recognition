"""
Integration tests for the full enrollment pipeline.

These tests require the InsightFace buffalo_l model pack (~300MB).
They are skipped automatically unless the environment variable
INTEGRATION_TESTS=1 is set.

Run with:
    INTEGRATION_TESTS=1 pytest tests/integration/ -v
"""
import os

import numpy as np
import pytest


SKIP_REASON = "Integration tests disabled. Set INTEGRATION_TESTS=1 to run."
skip_unless_integration = pytest.mark.skipif(
    os.getenv("INTEGRATION_TESTS") != "1",
    reason=SKIP_REASON,
)


@skip_unless_integration
class TestFaceRecognitionPipeline:
    @pytest.fixture(scope="class")
    def pipeline(self):
        from app.recognition.pipeline import FaceRecognitionPipeline
        p = FaceRecognitionPipeline()
        p.load()
        return p

    def test_pipeline_loads(self, pipeline):
        assert pipeline.is_loaded

    def test_blank_image_fails_quality(self, pipeline):
        """A solid-color image should fail the blur quality check."""
        image = np.full((200, 200, 3), 128, dtype=np.uint8)
        from app.recognition.pipeline import PipelineError
        result = pipeline.process(image)
        assert isinstance(result, PipelineError)
