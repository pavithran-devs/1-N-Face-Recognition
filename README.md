# Production-Grade 1:N Face Recognition Platform

An enterprise-ready, two-tier microservices platform for real-time candidate registration, biometric processing, and high-speed 1:N face identification.

Both services are built with Python, FastAPI, and async SQLAlchemy persistence, using state-of-the-art deep learning models for face analytics and FAISS for vector indexing.

---

## 1. System Flow & Pipeline

```
Candidate Image Upload
          │
          ▼
   [ SCRFD Detector ] ──► Detects face bounding boxes
          │
          ▼
 [ Quality Validator ] ──► Filters out blur, poor brightness, no-face, group photos
          │
          ▼
  [ Norm Crop Aligner ] ──► Aligns landmarks and crops face to 112x112 pixels
          │
          ▼
  [ ArcFace Embedder ] ──► Generates 512-dimensional feature vector
          │
          ▼
   [ L2 Normalizer ] ──► Normalizes vector length to unit space (Cosine Similarity)
          │
          ▼
    [ FAISS Search ] ──► Executes nearest-neighbor lookups under 0.2ms
          │
          ▼
   [ Threshold Check ] ──► Enforces security boundary (Default Match threshold: 0.65)
          │
          ▼
 [ PostgreSQL Lookup ] ──► Resolves candidate profile metadata (Name, Email, ID)
          │
          ▼
   [ JSON Response ] ──► Returns match indicators and processing latency profiles
```

---

## 2. Technology Stack

*   **Core Logic**: Python 3.11+, FastAPI (Uvicorn), Pydantic (data verification).
*   **Database Tier**: PostgreSQL 16+, SQLAlchemy 2.0 (asyncpg driver), Alembic migrations.
*   **Computer Vision**: InsightFace (`buffalo_l` pack: SCRFD detector + ArcFace w600k_r50 embedder), OpenCV, NumPy, ONNX Runtime (`CPUExecutionProvider`).
*   **Vector Search**: FAISS-CPU (`IndexFlatIP` inner product).
*   **Testing & Load**: k6 (load testing), Locust (stress testing), pytest, Ruff, Black.
*   **Client App (Planned)**: Flutter.

---

## 3. Directory Layout

```
.
├── enrollment_service/          # Port 8000: Registers candidates & embeds biometric files
│   ├── app/                     # FastAPI presentation, database models, repositories
│   └── streamlit_ui/            # Streamlit dashboard for operator registration
├── face_identification/         # Port 8001: Syncs database and performs 1:N FAISS searches
│   ├── app/                     # FastAPI routers, FAISS managers, metrics
│   └── streamlit_app/           # Streamlit identification terminal interface
├── scripts/                     # Automated testing runners & document generator scripts
├── load_tests/                  # k6 scripts & Locust files for scale evaluations
├── reports/                     # 35 Pre-deployment QA verification reports
├── logs/                        # System log formats and templates
├── postman/                     # API Postman collection structures
├── final-report/                # Compliance checklist and production audit verdict
└── Production_QA_Verification_Master_Report.pdf  # Compiled Master QA document
```

---

## 4. Quick Start

### 4.1 Database Provisioning
Make sure a PostgreSQL database named `enrollment_db` is running on your system, then apply Alembic migrations:
```bash
# From the root workspace directory
createdb -U postgres enrollment_db

cd enrollment_service
alembic upgrade head

cd ../face_identification
alembic upgrade head
```

### 4.2 Start Enrollment Service (Port 8000)
```bash
cd enrollment_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*   **Swagger API Docs**: `http://localhost:8000/docs`

### 4.3 Start Face Identification Service (Port 8001)
```bash
cd face_identification
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
*   **Swagger API Docs**: `http://localhost:8001/docs`

---

## 5. Persistent Data Model

### 5.1 Candidates Table (`candidates`)
Stores metadata profiles.
*   `id`: UUID Primary Key.
*   `candidate_id`: String (Unique business ID, e.g. EMP101).
*   `name`: String.
*   `email`: String (Unique email address).
*   `dob`: Date.

### 5.2 Biometric Embeddings Table (`face_embeddings`)
Stores biometric vector vectors.
*   `id`: UUID Primary Key.
*   `candidate_uuid`: UUID Foreign Key (cascades on candidate delete).
*   `embedding`: Float Array (512 dimensions).
*   `embedding_dimension`: Integer (512).
*   `model_name`: String (`buffalo_l`).
*   `normalized`: Boolean (`True`).

---

## 6. Execution of QA Testing Suite

The codebase comes equipped with an automated verification suite that spins up the services, preloads deep learning weights, and runs accuracy, latency, stress, and functional boundary checks using a subset of the LFW dataset.

### 6.1 Execute Comprehensive Test Suite
```bash
# Run the automated 26-point verification suite
enrollment_service/.venv/bin/python3 scripts/run_comprehensive_tests.py
```
This script compiles actual results, profiles pipeline execution times, and outputs a verification summary report at the root: `System_Comprehensive_Verification_Report.pdf`.

### 6.2 Compile the QA Master Verification Report (PDF)
To compile all 35 pre-deployment reports, k6/Locust plans, checklists, and logging formats into a single, unified enterprise PDF report:
```bash
enrollment_service/.venv/bin/python3 scripts/compile_master_pdf.py
```
This generates `Production_QA_Verification_Master_Report.pdf` at the root directory.

---

## 7. Production Hardening Checklist

Prior to launching these microservices on public staging or production clusters, ensure the following configurations are updated:
1.  **CORS Origins**: Narrow CORS parameters in `.env` from wildcard `*` to specific client frontend URLs to block cross-origin requests.
2.  **GPU Acceleration**: In high-throughput environments, install `onnxruntime-gpu` and configure `CUDAExecutionProvider` to reduce ArcFace inference latency from ~90ms to ~15ms.
3.  **FAISS Scaling**: As the candidate pool grows beyond 100k records, swap the singleton index configuration from `IndexFlatIP` to `IndexIVFFlat` or `HNSW` to maintain sub-millisecond query durations.
