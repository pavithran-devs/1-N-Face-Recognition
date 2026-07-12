# Face Enrollment Service

Production-grade face enrollment API. Registers candidates, generates **512-d ArcFace embeddings** via InsightFace (SCRFD + ArcFace buffalo_l), stores data in PostgreSQL, and exports/imports for a future face identification system.

> **Phase 1 only** — no FAISS, no cosine similarity, no face matching.

---

## Architecture

```
Presentation  │  FastAPI routers + Middleware (logging, rate-limiting, CORS)
──────────────┼──────────────────────────────────────────────────────────────
Application   │  Services: CandidateService, EnrollmentService, EmbeddingService
              │           ExportService, ImportService
──────────────┼──────────────────────────────────────────────────────────────
Domain        │  Pydantic schemas · Custom exceptions
──────────────┼──────────────────────────────────────────────────────────────
Infrastructure│  Repositories (SQLAlchemy async) · Recognition Pipeline
              │  (SCRFD detector → quality checks → aligner → ArcFace)
              │  Exporters (JSON/CSV) · PostgreSQL
```

### Enrollment Flow

```
Client ──POST /face/upload──► EnrollmentService
                                   │
                              ImageValidator
                                   │
                          FaceRecognitionPipeline
                           ├── SCRFD Detector
                           ├── Quality Checks (blur, brightness, size…)
                           ├── InsightFace Aligner (norm_crop 112×112)
                           └── ArcFace Embedder → L2 normalize (512-d)
                                   │
                     CandidateRepository.create()
                     EmbeddingRepository.create()
                                   │
                          Return candidate + embedding
```

### ER Diagram

```
CANDIDATE ──────────────────── FACE_EMBEDDING
  id (UUID PK)                   id (UUID PK)
  candidate_id (UK)              candidate_uuid (FK → candidates.id)
  name                           embedding (float[512])
  email (UK)                     embedding_dimension (512)
  dob                            model_name
  created_at                     normalized (true)
  updated_at                     created_at
```

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.11+ (3.14 recommended) |
| PostgreSQL | 14+ (18 recommended) |
| GCC | Any modern version (for OpenCV/onnxruntime) |

---

## Quick Start

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd enrollment_service
python3.14 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env if your PostgreSQL credentials differ
```

### 4. Create database and run migrations

```bash
createdb -U postgres enrollment_db
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
# Or: bash scripts/run_server.sh
```

The API is live at **http://localhost:8000**
Swagger UI: **http://localhost:8000/docs**

> InsightFace downloads the `buffalo_l` model pack (~300 MB) to `~/.insightface/models/` on first startup.

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Service health + pipeline status |
| `POST` | `/api/v1/candidates/` | Create candidate (no face yet) |
| `GET` | `/api/v1/candidates/` | List/search candidates (paginated) |
| `GET` | `/api/v1/candidates/{id}` | Get candidate by UUID |
| `PUT` | `/api/v1/candidates/{id}` | Update candidate metadata |
| `DELETE` | `/api/v1/candidates/{id}` | Delete candidate + embeddings |
| `POST` | `/api/v1/face/upload` | Enroll via file upload (form-data) |
| `POST` | `/api/v1/face/capture` | Enroll via base64 webcam capture (JSON) |
| `POST` | `/api/v1/embedding/generate/{uuid}` | Generate embedding for existing candidate |
| `PUT` | `/api/v1/embedding/regenerate/{uuid}` | Replace all embeddings |
| `GET` | `/api/v1/embedding/{uuid}` | List embeddings for candidate |
| `GET` | `/api/v1/export/json` | Export all (or one) to JSON |
| `GET` | `/api/v1/export/csv` | Export all (or one) to CSV |
| `POST` | `/api/v1/import/json` | Import from JSON file |
| `POST` | `/api/v1/import/csv` | Import from CSV file |

### Example: Enroll via file upload

```bash
curl -X POST http://localhost:8000/api/v1/face/upload \
  -F "image=@/path/to/face.jpg" \
  -F "candidate_id=EMP001" \
  -F "name=Alice Smith" \
  -F "email=alice@example.com"
```

### Example: Enroll via base64 capture

```bash
curl -X POST http://localhost:8000/api/v1/face/capture \
  -H "Content-Type: application/json" \
  -d '{
    "image_b64": "<base64-string>",
    "candidate_id": "EMP002",
    "name": "Bob",
    "email": "bob@example.com"
  }'
```

---

## Quality Checks

The pipeline rejects images that fail any of these checks:

| Check | Condition |
|-------|-----------|
| No face | 0 faces detected |
| Multiple faces | >1 face detected |
| Low confidence | Detection score < 0.50 |
| Face too small | Bounding-box area < 4,000 px² |
| Blur | Laplacian variance < 50 |
| Too dark | Mean brightness < 40 |
| Too bright | Mean brightness > 220 |
| Low resolution | Image < 64×64 px |

All thresholds are configurable via `QualityThresholds`.

---

## Development

### Running tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
# Or: bash scripts/run_tests.sh
```

Integration tests (require InsightFace models):

```bash
INTEGRATION_TESTS=1 pytest tests/integration/ -v
```

### Lint & format

```bash
bash scripts/lint.sh      # ruff check
bash scripts/format.sh    # black + ruff --fix
bash scripts/typecheck.sh # mypy
```

---

## Export Format

### JSON (`/api/v1/export/json`)

```json
[
  {
    "id": "uuid",
    "candidate_id": "EMP001",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "dob": "1990-01-15",
    "created_at": "2026-07-07T12:00:00",
    "updated_at": "2026-07-07T12:00:00",
    "embeddings": [
      {
        "id": "uuid",
        "embedding": [0.012, -0.034, ...],  // 512 floats
        "embedding_dimension": 512,
        "model_name": "buffalo_l",
        "normalized": true
      }
    ]
  }
]
```

### CSV (`/api/v1/export/csv`)

One row per embedding. The `embedding` column contains 512 semicolon-separated floats.

---

## Configuration

All settings are read from `.env` (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | `postgres` | PostgreSQL password |
| `DB_NAME` | `enrollment_db` | Database name |
| `INSIGHTFACE_MODEL_PACK` | `buffalo_l` | InsightFace model pack |
| `EXPORT_DIR` | `./exports` | Directory for export files |
| `LOG_LEVEL` | `INFO` | Loguru log level |
| `RATE_LIMIT_PER_MINUTE` | `60` | Requests per IP per minute |
| `MAX_IMAGE_SIZE_MB` | `10` | Maximum upload size |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
