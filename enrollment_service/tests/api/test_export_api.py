"""API tests for /api/v1/export endpoints."""
import pytest


class TestExportAPI:
    @pytest.mark.asyncio
    async def test_export_all_json(self, test_client):
        # Create a candidate first
        await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EXPORT001",
            "name": "Export Test",
            "email": "export@example.com",
        })
        resp = await test_client.get("/api/v1/export/json")
        assert resp.status_code == 200
        body = resp.json()
        assert body["format"] == "json"
        assert body["exported_count"] >= 1
        assert "file_path" in body

    @pytest.mark.asyncio
    async def test_export_all_csv(self, test_client):
        resp = await test_client.get("/api/v1/export/csv")
        assert resp.status_code == 200
        body = resp.json()
        assert body["format"] == "csv"
