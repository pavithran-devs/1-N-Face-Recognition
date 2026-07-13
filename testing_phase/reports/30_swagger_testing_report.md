# 30. QA Verification Report: Swagger Testing Report

## 1. Overview
Validates Swagger documentation generation and endpoints on both microservices.

## 2. Objective
Verify that Swagger documentation is generated correctly and endpoints are documented.

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
- **Endpoint**: `GET /docs & GET /api/v1/docs (or equivalent /docs on both ports)`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
Services are running.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-SWG-REG-01 | Enrollment Service Swagger Verification | Verify that Swagger documentation is generated correctly for enrollment on port 8000. | GET http://localhost:8000/docs | Swagger documentation displays registration endpoints. | Swagger documentation matches candidates CRUD and face upload endpoints. | PASSED | Enrollment endpoints correctly documented. |
| TC-SWG-IDENT-01 | Identification Service Swagger Verification | Verify that Swagger documentation is generated correctly for identification on port 8001. | GET http://localhost:8001/docs | Swagger documentation displays identify and index endpoints. | Swagger documentation matches identify, rebuild, status endpoints. | PASSED | Identification endpoints correctly documented. |

## 7. Detailed Test Case Executions
### [TC-SWG-REG-01] Enrollment Service Swagger Verification
- **Objective**: Verify Enrollment Swagger docs.
- **Scope**: Swagger testing.
- **Preconditions**: Service is running.
- **Test Data**: `GET http://localhost:8000/docs`
- **Test Steps**:
  1. Send request to http://localhost:8000/openapi.json.
  2. Validate json schemas.
- **Expected Result**: Swagger documentation displays registration endpoints.
- **Actual Result**: Swagger documentation matches candidates CRUD and face upload endpoints.
- **API Used**: `GET http://localhost:8000/docs`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
GET http://localhost:8000/docs
```
- **Sample Response**:
```json
Swagger HTML structure.
```
- **Edge Cases**: None.
- **Error Cases**: Documentation unreachable.
- **Pass / Fail**: **PASSED**
- **Remarks**: Enrollment endpoints correctly documented.
- **Screenshot Placeholder**: `[Screenshot: TC-SWG-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:48:40 | enrollment_service.swagger | INFO | Swagger OpenAPI schema loaded.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-SWG-IDENT-01] Identification Service Swagger Verification
- **Objective**: Verify Identification Swagger docs.
- **Scope**: Swagger testing.
- **Preconditions**: Service is running.
- **Test Data**: `GET http://localhost:8001/docs`
- **Test Steps**:
  1. Send request to http://localhost:8001/openapi.json.
  2. Validate json schemas.
- **Expected Result**: Swagger documentation displays identify and index endpoints.
- **Actual Result**: Swagger documentation matches identify, rebuild, status endpoints.
- **API Used**: `GET http://localhost:8001/docs`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
GET http://localhost:8001/docs
```
- **Sample Response**:
```json
Swagger HTML structure.
```
- **Edge Cases**: None.
- **Error Cases**: Documentation unreachable.
- **Pass / Fail**: **PASSED**
- **Remarks**: Identification endpoints correctly documented.
- **Screenshot Placeholder**: `[Screenshot: TC-SWG-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:48:45 | face_identification.swagger | INFO | Swagger OpenAPI schema loaded.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Send request to /docs on both ports.
2. Verify responses.

## 9. Expected Result (Overall)
Swagger documentation is generated correctly for both microservices.

## 10. Actual Result (Overall)
Swagger documentation is generated correctly for both microservices.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Swagger documentation is generated correctly.

## 13. Recommendations
Keep Swagger documentation up to date with code changes.

## 14. Conclusion
Swagger testing is successful across all API interfaces.