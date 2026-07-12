"""API tests for /api/v1/import endpoints."""
import io
import json

import pytest


class TestImportAPI:
    @pytest.mark.asyncio
    async def test_import_json_valid(self, test_client):
        records = [
            {
                "candidate_id": "IMP001",
                "name": "Import Person",
                "email": "import@example.com",
                "embeddings": [{"embedding": [0.1] * 512, "model_name": "buffalo_l", "normalized": True}],
            }
        ]
        payload = json.dumps(records).encode()
        resp = await test_client.post(
            "/api/v1/import/json",
            files={"file": ("data.json", io.BytesIO(payload), "application/json")},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["imported_count"] == 1
        assert body["skipped_count"] == 0

    @pytest.mark.asyncio
    async def test_import_json_invalid_json(self, test_client):
        resp = await test_client.post(
            "/api/v1/import/json",
            files={"file": ("data.json", io.BytesIO(b"not json"), "application/json")},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_import_json_duplicate_skipped(self, test_client):
        records = [{"candidate_id": "IMP002", "name": "Dup", "email": "dup@example.com", "embeddings": []}]
        payload = json.dumps(records).encode()
        # Import once
        await test_client.post(
            "/api/v1/import/json",
            files={"file": ("data.json", io.BytesIO(payload), "application/json")},
        )
        # Import again — should be skipped
        resp = await test_client.post(
            "/api/v1/import/json",
            files={"file": ("data.json", io.BytesIO(payload), "application/json")},
        )
        body = resp.json()
        assert body["skipped_count"] >= 1
