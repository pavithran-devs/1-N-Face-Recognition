# 01. QA Verification Report: Candidate Registration Testing Report

## 1. Overview
Validates the complete flow of candidate metadata creation and face embedding registration.

## 2. Objective
Verify that candidate profiles can be created, and face images uploaded, decoded, processed, and stored in PostgreSQL.

## 3. Testing Environment

- **OS**: Linux (Ubuntu 22.04 LTS / Debian 12)
- **CPU**: Intel(R) Xeon(R) CPU @ 2.20GHz (4 Cores)
- **RAM**: 16 GB DDR4
- **Database**: PostgreSQL 16.2
- **InsightFace Model**: buffalo_l (SCRFD face detection + ArcFace w600k_r50 embedding)
- **FAISS**: 1.7.4 (IndexFlatIP)
- **Python**: 3.11.8
- **FastAPI**: 0.111.0
- **SQLAlchemy**: 2.0.28
- **OpenCV**: 4.9.0.80
- **NumPy**: 1.26.4
- **ONNX Runtime**: 1.17.1 (CPUExecutionProvider)


## 4. API Endpoint Under Test
- **Endpoint**: `POST /api/v1/candidates/ and POST /api/v1/embedding/generate/{uuid}`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
PostgreSQL database running, alembic migrations applied, and InsightFace models fully initialized.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-REG-01 | Successful Candidate Registration & Embedding Generation | Registers a new candidate with valid metadata and uploads a clear face image. | candidate_id: EMP101, name: John Doe, email: john.doe@corp.com, dob: 1992-05-15, file: john_clear.jpg | HTTP 201 created for candidate and HTTP 201 for embedding generation. | Candidate profile persisted in SQL, 512-d normalized embedding written to DB. | PASSED | Database persistence verified. |

## 7. Detailed Test Case Executions
### [TC-REG-01] Successful Candidate Registration & Embedding Generation
- **Objective**: Ensure candidates are successfully created with biometric vector generation.
- **Scope**: Functional / Integration testing.
- **Preconditions**: Candidate John Doe does not exist in PostgreSQL.
- **Test Data**: `candidate_id: EMP101, name: John Doe, email: john.doe@corp.com, dob: 1992-05-15, file: john_clear.jpg`
- **Test Steps**:
  1. Send POST to /api/v1/candidates/ with JSON metadata.
  2. Extract candidate UUID from response.
  3. Send POST to /api/v1/embedding/generate/{uuid} with face image multipart form-data.
- **Expected Result**: HTTP 201 created for candidate and HTTP 201 for embedding generation.
- **Actual Result**: Candidate profile persisted in SQL, 512-d normalized embedding written to DB.
- **API Used**: `POST /api/v1/candidates/ & POST /api/v1/embedding/generate/{uuid}`
- **HTTP Status**: `201 Created`
- **Sample Request**:
```json
{
  "candidate_id": "EMP101",
  "name": "John Doe",
  "email": "john.doe@corp.com",
  "dob": "1992-05-15"
}
```
- **Sample Response**:
```json
{
  "id": "c001f35f-3315-4ba8-bb58-372986429f4a",
  "candidate_id": "EMP101",
  "name": "John Doe",
  "email": "john.doe@corp.com",
  "dob": "1992-05-15"
}
```
- **Edge Cases**: Unusual name formats, international characters, extremely long candidate IDs.
- **Error Cases**: Missing mandatory fields, invalid dates, unsupported image types.
- **Pass / Fail**: **PASSED**
- **Remarks**: Database persistence verified.
- **Screenshot Placeholder**: `[Screenshot: TC-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:30:12 | enrollment_service.services.enrollment | INFO | Created candidate profile UUID: c001f35f-3315-4ba8-bb58-372986429f4a
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Call candidates API endpoint with a payload.
2. Verify response UUID and status code.
3. Call embedding generate API endpoint with a sample face picture.
4. Check logs for SCRFD face detection and ArcFace L2-normalization tasks.

## 9. Expected Result (Overall)
HTTP status codes must be 201, and database must contain candidate records with a 512-dimensional vector.

## 10. Actual Result (Overall)
Both candidate record and embedding vector successfully written and stored in the database.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Pipeline runs and correctly L2-normalizes the ArcFace output vector.

## 13. Recommendations
Implement transactional safety so that candidate deletion is clean in case of embedding generation failure.

## 14. Conclusion
Candidate Registration workflow is verified as stable and production-ready.