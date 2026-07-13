# Postman Collection Structure & Documentation

The Postman Collection is designed to verify the API interfaces of the Face Recognition system. The collection is exported in the workspace as `Postman_Collection.json`.

## Collection Outline

### 1. Registration Folder
Contains endpoints for creating candidate metadata and uploading face images.
- **POST `/api/v1/candidates/`**: Create Candidate Metadata
  - *Headers*: `Content-Type: application/json`
  - *Body*:
    ```json
    {
      "candidate_id": "POSTMAN_EMP_01",
      "name": "Jane Miller",
      "email": "jane.miller@corp.com",
      "dob": "1994-08-22"
    }
    ```
- **POST `/api/v1/embedding/generate/{{candidate_uuid}}`**: Upload Face Image
  - *Headers*: `Content-Type: multipart/form-data`
  - *Body*: Form-data field `image` with a JPEG binary.

### 2. Identification Folder
Contains endpoints for query identification.
- **POST `/identify`**: Identify Candidate (Multipart Upload)
  - *Headers*: `Content-Type: multipart/form-data`
  - *Body*:
    - `file`: JPEG binary
    - `threshold`: `0.65` (default)
    - `top_k`: `5` (default)
- **POST `/camera/identify`**: Identify Candidate (Base64 webcam frame)
  - *Headers*: `Content-Type: application/json`
  - *Body*:
    ```json
    {
      "image_b64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
      "threshold": 0.65,
      "top_k": 3
    }
    ```

### 3. Health & Observability Folder
Heartbeats and tracking.
- **GET `/health`**: Liveness probe (Identification port 8001)
- **GET `/api/v1/health`**: Liveness probe (Enrollment port 8000)
- **GET `/metrics`**: Performance stats

### 4. Index Operations Folder
Administrative tasks.
- **POST `/index/rebuild`**: Force rebuild FAISS index from Postgres database.
- **GET `/index/status`**: Return active index metadata.

### 5. Negative Test Folder
Error validation check requests.
- **POST `/api/v1/candidates/`**: Duplicate candidate_id check.
- **POST `/api/v1/candidates/`**: Malformed email validation.
- **POST `/identify`**: No face image upload (expects 422 `no_face`).
- **POST `/identify`**: Group photo upload (expects 422 `multiple_faces`).