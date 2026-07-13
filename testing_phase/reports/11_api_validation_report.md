# 11. QA Verification Report: API Validation Report

## 1. Overview
Validates JSON request payload schema verification rules.

## 2. Objective
Verify FastAPI request validation rules block invalid candidate metadata fields.

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
- **Endpoint**: `POST /api/v1/candidates/`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
JSON validation layer configured via Pydantic model validations.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-VAL-01 | Invalid Email and Date formats | Post metadata containing bad email and malformed dob date format. | email: invalid-mail, dob: 22-12-1994 | HTTP 422 Unprocessable Entity, detail validation list. | HTTP 422 with detailed json array indicating validation failures. | PASSED | Validation succeeded in rejecting. |

## 7. Detailed Test Case Executions
### [TC-VAL-01] Invalid Email and Date formats
- **Objective**: Verify Pydantic field rules.
- **Scope**: Functional API verification.
- **Preconditions**: None.
- **Test Data**: `email: invalid-mail, dob: 22-12-1994`
- **Test Steps**:
  1. Send candidate payload with incorrect email and dob format.
- **Expected Result**: HTTP 422 Unprocessable Entity, detail validation list.
- **Actual Result**: HTTP 422 with detailed json array indicating validation failures.
- **API Used**: `POST /api/v1/candidates/`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
{
  "candidate_id": "EMP888",
  "name": "Tester",
  "email": "invalid-mail",
  "dob": "22-12-1994"
}
```
- **Sample Response**:
```json
{
  "error": {
    "code": "validation_error",
    "message": "Input validation failed",
    "details": [
      {"loc": ["body", "email"], "msg": "value is not a valid email address"},
      {"loc": ["body", "dob"], "msg": "Input should be a valid date"}
    ]
  }
}
```
- **Edge Cases**: Null values, empty strings, SQL injection characters.
- **Error Cases**: Incorrectly typed age or number format.
- **Pass / Fail**: **PASSED**
- **Remarks**: Validation succeeded in rejecting.
- **Screenshot Placeholder**: `[Screenshot: TC-VAL-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:37:45 | enrollment_service.api | INFO | Validation failed for input schema: 2 errors.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Request candidates with bad fields.
2. Confirm validation rules catch email anomalies and date structures.

## 9. Expected Result (Overall)
FastAPI triggers 422 status response with description detail list.

## 10. Actual Result (Overall)
Rejection occurred correctly.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Pydantic validator catches structure issues prior to database interaction.

## 13. Recommendations
Keep schema validators strict on dob to allow proper age calculations.

## 14. Conclusion
Validation framework is complete.