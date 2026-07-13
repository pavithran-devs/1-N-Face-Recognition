# 16. QA Verification Report: Health Endpoint Report

## 1. Overview
Validates system diagnostic health endpoints for liveness and readiness monitoring on both microservices.

## 2. Objective
Verify health checks report DB connections, model loaded, and FAISS index states.

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
- **Endpoint**: `GET /api/v1/health & GET /health`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
All services running.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-HLT-REG-01 | Verify Enrollment Service Health Status | Send GET to health check on Enrollment Service. | GET /api/v1/health | HTTP 200 with status: healthy, database: connected. | HTTP 200, matching expected indicators. | PASSED | Enrollment Service healthy. |
| TC-HLT-IDENT-01 | Verify Identification Service Health Status | Send GET to health check on Face Identification Service. | GET /health | HTTP 200 with status: healthy, database: connected, model: loaded, index: active. | HTTP 200, matching expected indicators. | PASSED | Identification Service healthy. |

## 7. Detailed Test Case Executions
### [TC-HLT-REG-01] Verify Enrollment Service Health Status
- **Objective**: Verify Enrollment health.
- **Scope**: Monitoring endpoints.
- **Preconditions**: None.
- **Test Data**: `GET /api/v1/health`
- **Test Steps**:
  1. Run curl against /api/v1/health on port 8000.
- **Expected Result**: HTTP 200 with status: healthy, database: connected.
- **Actual Result**: HTTP 200, matching expected indicators.
- **API Used**: `GET /api/v1/health`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
GET /api/v1/health
```
- **Sample Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "pipeline": "loaded"
}
```
- **Edge Cases**: Database disconnect.
- **Error Cases**: Startup model load error.
- **Pass / Fail**: **PASSED**
- **Remarks**: Enrollment Service healthy.
- **Screenshot Placeholder**: `[Screenshot: TC-HLT-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:41:05 | enrollment_service.api.health | INFO | Health diagnostics check clean.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-HLT-IDENT-01] Verify Identification Service Health Status
- **Objective**: Verify Identification health.
- **Scope**: Monitoring endpoints.
- **Preconditions**: None.
- **Test Data**: `GET /health`
- **Test Steps**:
  1. Run curl against /health on port 8001.
- **Expected Result**: HTTP 200 with status: healthy, database: connected, model: loaded, index: active.
- **Actual Result**: HTTP 200, matching expected indicators.
- **API Used**: `GET /health`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
GET /health
```
- **Sample Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "pipeline": "loaded",
  "faiss_index": {
    "loaded": true,
    "size": 12,
    "path": "faiss_index.bin"
  }
}
```
- **Edge Cases**: Index file missing.
- **Error Cases**: Model pipeline crash.
- **Pass / Fail**: **PASSED**
- **Remarks**: Identification Service healthy.
- **Screenshot Placeholder**: `[Screenshot: TC-HLT-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:41:12 | face_identification.api.health | INFO | Health diagnostic clean.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Call health endpoints of both services and inspect JSON response fields.

## 9. Expected Result (Overall)
Clean status report containing DB connection details on both services.

## 10. Actual Result (Overall)
Both service instances return correct and descriptive health payloads.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Integrates with Docker health check pipelines.

## 13. Recommendations
Add connection pool sizing information to health statistics.

## 14. Conclusion
Health API verification is successful across both services.