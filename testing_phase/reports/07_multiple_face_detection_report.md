# 07. QA Verification Report: Multiple Face Detection Report

## 1. Overview
Validates system handling of images containing more than one face.

## 2. Objective
Verify that group images with multiple faces are rejected for security and precision on both microservices.

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
- **Endpoint**: `POST /api/v1/face/upload & POST /identify`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
Pipeline loaded, multiple faces validation check enabled.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-MUL-REG-01 | Enrollment Service Multiple-Face Rejection | Upload picture containing multiple faces to enrollment. | file: three_faces.jpg | HTTP 422, error.code: quality_check_failed, quality_code: multiple_faces. | HTTP 422, error.code: quality_check_failed, details: {quality_code: multiple_faces}. | PASSED | Enrollment correctly blocked the upload. |
| TC-MUL-IDENT-01 | Identification Service Multiple-Face Rejection | Upload picture containing multiple faces to identification. | file: three_faces.jpg | HTTP 422, error.code: quality_check_failed, quality_code: multiple_faces. | HTTP 422, error.code: quality_check_failed, details: {quality_code: multiple_faces}. | PASSED | Identification correctly blocked the query. |

## 7. Detailed Test Case Executions
### [TC-MUL-REG-01] Enrollment Service Multiple-Face Rejection
- **Objective**: Verify multi-face blocking on enrollment.
- **Scope**: Biometric pipeline security.
- **Preconditions**: Candidate metadata exists.
- **Test Data**: `file: three_faces.jpg`
- **Test Steps**:
  1. Send group image file containing multiple faces to /api/v1/embedding/generate/{uuid}.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: multiple_faces.
- **Actual Result**: HTTP 422, error.code: quality_check_failed, details: {quality_code: multiple_faces}.
- **API Used**: `POST /api/v1/embedding/generate/{uuid}`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: image=@three_faces.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "multiple_faces",
      "description": "Multiple faces detected. Please provide an image with exactly one face."
    }
  }
}
```
- **Edge Cases**: Subtle secondary background faces.
- **Error Cases**: None.
- **Pass / Fail**: **PASSED**
- **Remarks**: Enrollment correctly blocked the upload.
- **Screenshot Placeholder**: `[Screenshot: TC-MUL-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:34:50 | enrollment_service.services.enrollment | WARN | Face quality validation failed: multiple_faces
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-MUL-IDENT-01] Identification Service Multiple-Face Rejection
- **Objective**: Verify multi-face blocking on identification.
- **Scope**: Biometric pipeline security.
- **Preconditions**: None.
- **Test Data**: `file: three_faces.jpg`
- **Test Steps**:
  1. Send group image file containing multiple faces to /identify.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: multiple_faces.
- **Actual Result**: HTTP 422, error.code: quality_check_failed, details: {quality_code: multiple_faces}.
- **API Used**: `POST /identify`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: file=@three_faces.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "multiple_faces",
      "description": "Multiple faces detected. Please provide an image with exactly one face."
    }
  }
}
```
- **Edge Cases**: Double faces.
- **Error Cases**: None.
- **Pass / Fail**: **PASSED**
- **Remarks**: Identification correctly blocked the query.
- **Screenshot Placeholder**: `[Screenshot: TC-MUL-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:34:55 | face_identification.api.identify | WARN | Face quality validation failed: multiple_faces
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Send a group image containing multiple distinct subjects to both service endpoints.
2. Confirm API responds with status code 422.

## 9. Expected Result (Overall)
Strict rejection with quality check error 'multiple_faces' on both systems.

## 10. Actual Result (Overall)
Rejection occurred correctly; exact detail message is returned in both payloads.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Essential to avoid ambiguous biometric registrations and search queries.

## 13. Recommendations
Ensure UI prompts users to center their face and crop out other people.

## 14. Conclusion
Multiple faces rejection logic functions correctly.