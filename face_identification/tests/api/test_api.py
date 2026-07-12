"""Integration tests for the API endpoints."""

import json

import pytest

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


async def test_health_endpoint(test_client) -> None:
    resp = await test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "database" in data
    assert "face_models" in data
    assert "faiss_index" in data


async def test_metrics_endpoint(test_client) -> None:
    resp = await test_client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_searches" in data
    assert "hits" in data
    assert "misses" in data
    assert "average_latencies_ms" in data


async def test_index_status_endpoint(test_client) -> None:
    resp = await test_client.get("/index/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "active" in data
    assert "size" in data


async def test_index_rebuild_endpoint(test_client) -> None:
    # Rebuilding with empty database should return status success but warning size 0
    resp = await test_client.post("/index/rebuild")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"


async def test_json_and_csv_imports(test_client) -> None:
    # 1. Test JSON import
    sample_json = [
        {
            "candidate_id": "TEST_CAND_01",
            "name": "Alex Mercer",
            "email": "alex@mercer.com",
            "dob": "1990-05-15",
            "embeddings": [
                {
                    "embedding": [0.1] * 512,
                    "embedding_dimension": 512,
                    "model_name": "buffalo_l",
                    "normalized": True,
                }
            ],
        }
    ]

    files = {"file": ("test.json", json.dumps(sample_json).encode("utf-8"), "application/json")}
    resp = await test_client.post("/import/json", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported_count"] == 1
    assert data["skipped_count"] == 0

    # 2. Test CSV import
    # Header format: id,candidate_id,name,email,dob,created_at,updated_at,embedding_id,embedding,embedding_dimension,model_name,normalized
    embedding_str = ";".join([str(0.2)] * 512)
    sample_csv = (
        "id,candidate_id,name,email,dob,created_at,updated_at,embedding_id,embedding,embedding_dimension,model_name,normalized\n"
        f",TEST_CAND_02,Dana Mercer,dana@mercer.com,1992-08-20,,,embedding_id_2,{embedding_str},512,buffalo_l,True"
    )

    files_csv = {"file": ("test.csv", sample_csv.encode("utf-8"), "text/csv")}
    resp_csv = await test_client.post("/import/csv", files=files_csv)
    assert resp_csv.status_code == 200
    data_csv = resp_csv.json()
    assert data_csv["imported_count"] == 1
    assert data_csv["skipped_count"] == 0


async def test_face_identification_match_success(test_client) -> None:
    # Seed a candidate in database first using JSON import
    sample_json = [
        {
            "candidate_id": "MATCH_001",
            "name": "Bruce Banner",
            "email": "bruce@banner.com",
            "embeddings": [
                {
                    # Since our mock pipeline returns a random normalized vector,
                    # we mock the FAISSManager search or build the index so Bruce Banner vector matches the mock.
                    "embedding": [0.0] * 512,
                    "embedding_dimension": 512,
                    "model_name": "buffalo_l",
                    "normalized": True,
                }
            ],
        }
    ]
    files = {"file": ("test.json", json.dumps(sample_json).encode("utf-8"), "application/json")}
    await test_client.post("/import/json", files=files)

    # Trigger rebuild to load Bruce Banner into FAISS
    await test_client.post("/index/rebuild")

    # Call identify endpoint with a valid BGR image encoded in JPEG
    import io

    from PIL import Image

    img = Image.new("RGB", (200, 200), color="gray")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    valid_image_bytes = buf.getvalue()

    files_id = {"file": ("face.jpg", valid_image_bytes, "image/jpeg")}
    data_id = {"threshold": 0.0, "top_k": 1}

    resp_id = await test_client.post("/identify", files=files_id, data=data_id)
    assert resp_id.status_code == 200
    data_id_res = resp_id.json()

    # Assert successful match (top result will be matched since threshold is 0.0)
    assert data_id_res["matched"] is True
    assert "name" in data_id_res
    assert "candidate_id" in data_id_res


async def test_camera_identify_endpoint(test_client) -> None:
    # Seed candidate first
    sample_json = [
        {
            "candidate_id": "MATCH_CAM_01",
            "name": "Bruce Banner",
            "email": "bruce@banner.com",
            "embeddings": [
                {
                    "embedding": [0.0] * 512,
                    "embedding_dimension": 512,
                    "model_name": "buffalo_l",
                    "normalized": True,
                }
            ],
        }
    ]
    files_import = {
        "file": ("test.json", json.dumps(sample_json).encode("utf-8"), "application/json")
    }
    await test_client.post("/import/json", files=files_import)
    await test_client.post("/index/rebuild")

    # 1. Create a dummy image
    import io

    from PIL import Image

    img = Image.new("RGB", (200, 200), color="gray")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    valid_image_bytes = buf.getvalue()

    files_id = {"file": ("camera.jpg", valid_image_bytes, "image/jpeg")}
    data_id = {"threshold": 0.0, "top_k": 1}

    resp = await test_client.post("/camera/identify", files=files_id, data=data_id)
    assert resp.status_code == 200
    assert resp.json()["matched"] is True


async def test_import_postgres_sync_endpoint(test_client) -> None:
    resp = await test_client.post("/import/postgres")
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
