"""API Client helper for the Streamlit dashboard."""

import os

import httpx
from loguru import logger

# Retrieve the API URL from environment, fallback to localhost:8001
API_BASE_URL = os.getenv("API_URL", "http://localhost:8001")


class FaceIdentifyAPIClient:
    """Helper client to interact with the FastAPI Backend Service."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or API_BASE_URL
        self.timeout = 30.0

    def get_health(self) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/health")
                return resp.json() if resp.status_code == 200 else {"status": "unhealthy"}
        except Exception as exc:
            logger.error("Failed to connect to health API: {}", exc)
            return {"status": "unreachable", "detail": str(exc)}

    def get_metrics(self) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/metrics")
                return resp.json() if resp.status_code == 200 else {}
        except Exception as exc:
            logger.error("Failed to connect to metrics API: {}", exc)
            return {}

    def get_index_status(self) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/index/status")
                return resp.json() if resp.status_code == 200 else {}
        except Exception as exc:
            logger.error("Failed to connect to index status API: {}", exc)
            return {}

    def rebuild_index(self) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/index/rebuild")
                return resp.json()
        except Exception as exc:
            logger.error("Failed to trigger index rebuild: {}", exc)
            return {"status": "error", "message": str(exc)}

    def import_postgres_sync(self) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/import/postgres")
                return resp.json()
        except Exception as exc:
            logger.error("Failed to trigger postgres sync: {}", exc)
            return {"status": "error", "message": str(exc)}

    def import_json(self, file_name: str, file_bytes: bytes) -> dict:
        try:
            files = {"file": (file_name, file_bytes, "application/json")}
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/import/json", files=files)
                return resp.json()
        except Exception as exc:
            logger.error("JSON import request failed: {}", exc)
            return {"error": {"message": str(exc)}}

    def import_csv(self, file_name: str, file_bytes: bytes) -> dict:
        try:
            files = {"file": (file_name, file_bytes, "text/csv")}
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/import/csv", files=files)
                return resp.json()
        except Exception as exc:
            logger.error("CSV import request failed: {}", exc)
            return {"error": {"message": str(exc)}}

    def identify_face(
        self,
        file_bytes: bytes,
        filename: str = "frame.jpg",
        threshold: float = 0.65,
        top_k: int = 5,
    ) -> dict:
        """Uploads a face image to the identify endpoint."""
        try:
            files = {"file": (filename, file_bytes, "image/jpeg")}
            data = {"threshold": threshold, "top_k": top_k}

            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/identify", files=files, data=data)

                # Check for standard errors
                if resp.status_code == 422:
                    return {"status_code": 422, "detail": resp.json()}
                elif resp.status_code != 200:
                    return {"status_code": resp.status_code, "detail": resp.text}

                return resp.json()
        except Exception as exc:
            logger.error("Face identification request failed: {}", exc)
            return {"status_code": 500, "detail": {"error": {"message": str(exc)}}}
