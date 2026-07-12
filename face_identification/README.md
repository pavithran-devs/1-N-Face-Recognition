# Face Identification Service

Production-grade face identification API for **1:N matching**.
It validates incoming face images, generates ArcFace embeddings, performs FAISS similarity search, and resolves candidate details from PostgreSQL.

---

## Overview

The service is designed for real-time or near-real-time identification:

- Accept uploaded face images from files or camera frames
- Run detection + quality checks + alignment + embedding generation
- Search top matches in a FAISS index
- Apply similarity threshold logic
- Return matched candidate metadata from PostgreSQL

---

## Architecture

```
Presentation  │ FastAPI routers + middleware (logging, rate-limiting, CORS)
──────────────┼──────────────────────────────────────────────────────────────
Application   │ Identification, Import, Index services
──────────────┼──────────────────────────────────────────────────────────────
Domain        │ Schemas, exceptions, telemetry contracts
──────────────┼──────────────────────────────────────────────────────────────
Infrastructure│ PostgreSQL repositories + FaceRecognitionPipeline + FAISS
```

### Identification Flow

```
Client ──POST /identify or /camera/identify──► FaceRecognitionPipeline
                                                   │
                                              Quality checks
                                                   │
                                       ArcFace embedding (512-d)
                                                   │
                                          FAISS top-k search
                                                   │
                                     Threshold + DB candidate fetch
                                                   │
                                      Return match / unknown candidate
```

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| PostgreSQL | 14+ |
| FAISS | `faiss-cpu` (installed via pip) |

---

## Quick Start

### 1. Create and activate virtual environment

```bash
cd face_identification
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env values as needed
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the API server

```bash
uvicorn app.main:app --reload --port 8001
# Or: bash scripts/run_server.sh
```

API base URL: `http://localhost:8001`

Swagger UI: `http://localhost:8001/docs`

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health + DB + model + index status |
| `POST` | `/identify` | Identify candidate from uploaded image |
| `POST` | `/camera/identify` | Identify candidate from camera frame upload |
| `POST` | `/import/json` | Import candidate embeddings from JSON |
| `POST` | `/import/csv` | Import candidate embeddings from CSV |
| `POST` | `/import/postgres` | Sync/rebuild index from PostgreSQL data |
| `POST` | `/index/rebuild` | Manually rebuild FAISS index |
| `GET` | `/index/status` | Current FAISS index metadata |
| `GET` | `/metrics` | Runtime telemetry and timing metrics |

### Example: Identify from file

```bash
curl -X POST http://localhost:8001/identify \
  -F "file=@/path/to/face.jpg" \
  -F "threshold=0.65" \
  -F "top_k=5"
```

---

## Configuration

Key `.env` settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | `postgres` | PostgreSQL password |
| `DB_NAME` | `enrollment_db` | Source database containing candidates/embeddings |
| `INSIGHTFACE_MODEL_PACK` | `buffalo_l` | InsightFace model pack |
| `FAISS_INDEX_TYPE` | `IndexFlatIP` | FAISS index implementation |
| `FAISS_INDEX_PATH` | `faiss_index.bin` | On-disk FAISS index file |
| `SIMILARITY_THRESHOLD` | `0.65` | Match threshold |
| `TOP_K_DEFAULT` | `5` | Number of nearest neighbors per search |
| `HOST` | `0.0.0.0` | API bind host |
| `PORT` | `8001` | API bind port |
| `RATE_LIMIT_PER_MINUTE` | `60` | Per-IP request limit |

---

## Development

### Run tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
# Or: bash scripts/run_tests.sh
```

### Lint, format, and type-check

```bash
bash scripts/lint.sh
bash scripts/format.sh
bash scripts/typecheck.sh
```

### Optional UI

```bash
bash scripts/run_ui.sh
```

