"""API tests for /api/v1/candidates endpoints."""
import pytest


class TestCandidatesAPI:
    @pytest.mark.asyncio
    async def test_create_candidate(self, test_client):
        resp = await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EMP001",
            "name": "Alice Smith",
            "email": "alice@example.com",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["candidate_id"] == "EMP001"
        assert "id" in body

    @pytest.mark.asyncio
    async def test_create_duplicate_raises_409(self, test_client):
        await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EMP002",
            "name": "Bob",
            "email": "bob@example.com",
        })
        resp = await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EMP002",
            "name": "Bob2",
            "email": "bob2@example.com",
        })
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_list_candidates(self, test_client):
        await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EMP003",
            "name": "Carol",
            "email": "carol@example.com",
        })
        resp = await test_client.get("/api/v1/candidates/")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "pagination" in body

    @pytest.mark.asyncio
    async def test_get_candidate_not_found(self, test_client):
        import uuid
        resp = await test_client.get(f"/api/v1/candidates/{uuid.uuid4()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_candidate(self, test_client):
        create_resp = await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EMP004",
            "name": "David",
            "email": "david@example.com",
        })
        cid = create_resp.json()["id"]
        resp = await test_client.put(f"/api/v1/candidates/{cid}", json={"name": "David Updated"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "David Updated"

    @pytest.mark.asyncio
    async def test_delete_candidate(self, test_client):
        create_resp = await test_client.post("/api/v1/candidates/", json={
            "candidate_id": "EMP005",
            "name": "Eve",
            "email": "eve@example.com",
        })
        cid = create_resp.json()["id"]
        resp = await test_client.delete(f"/api/v1/candidates/{cid}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_health(self, test_client):
        resp = await test_client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
