# 27. QA Verification Report: Server Restart Report

## 1. Overview
Validates system recovery after server restart operations on both Enrollment and Identification microservices.

## 2. Objective
Verify the server recovers cleanly and initializes models on startup.

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
Service configuration files must be complete.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-RST-REG-01 | Enrollment Service Warm Start Recovery | Restart Enrollment Service process. | Process restart. | HTTP 200, status: healthy. | Process recovers, model pre-warming completed, ready for metadata/embedding writes. | PASSED | Process restarted successfully. |
| TC-RST-IDENT-01 | Identification Service Warm Start Recovery | Restart Identification Service process. | Process restart. | HTTP 200, status: healthy. | Process recovers, model pre-warming completed, FAISS index reloaded. | PASSED | Process restarted successfully. |

## 7. Detailed Test Case Executions
### [TC-RST-REG-01] Enrollment Service Warm Start Recovery
- **Objective**: Verify enrollment restart recovery.
- **Scope**: Resilience testing.
- **Preconditions**: Database running.
- **Test Data**: `Process restart.`
- **Test Steps**:
  1. Kill Enrollment server.
  2. Restart Enrollment server.
  3. Verify /api/v1/health.
- **Expected Result**: HTTP 200, status: healthy.
- **Actual Result**: Process recovers, model pre-warming completed, ready for metadata/embedding writes.
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
- **Edge Cases**: Incomplete configuration parameters.
- **Error Cases**: Database unreachable.
- **Pass / Fail**: **PASSED**
- **Remarks**: Process restarted successfully.
- **Screenshot Placeholder**: `[Screenshot: TC-RST-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:46:55 | enrollment_service.core.events | INFO | Preloaded models successfully.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-RST-IDENT-01] Identification Service Warm Start Recovery
- **Objective**: Verify identification restart recovery.
- **Scope**: Resilience testing.
- **Preconditions**: Database running.
- **Test Data**: `Process restart.`
- **Test Steps**:
  1. Kill Identification server.
  2. Restart Identification server.
  3. Verify /health.
- **Expected Result**: HTTP 200, status: healthy.
- **Actual Result**: Process recovers, model pre-warming completed, FAISS index reloaded.
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
  "pipeline": "loaded"
}
```
- **Edge Cases**: FAISS index file corrupt on startup.
- **Error Cases**: InsightFace fails to initialize.
- **Pass / Fail**: **PASSED**
- **Remarks**: Process restarted successfully.
- **Screenshot Placeholder**: `[Screenshot: TC-RST-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:47:02 | face_identification.core.events | INFO | Loaded model pack buffalo_l successfully.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Restart both microservice processes.
2. Confirm automatic model reload timings.

## 9. Expected Result (Overall)
Both servers boot and initialize models cleanly.

## 10. Actual Result (Overall)
Models and FAISS index are loaded correctly on startup for both microservices.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
First query timing warmups are handled correctly.

## 13. Recommendations
Use pre-warming calls on startup before routing user traffic.

## 14. Conclusion
Server restart recovery behaves correctly for both services.