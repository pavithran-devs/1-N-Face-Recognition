# 06. QA Verification Report: No Face Detection Report

## 1. Overview
Validates system handling of images containing no human faces.

## 2. Objective
Verify that uploading non-face images results in a quality check validation failure (422 Unprocessable Entity) on both Enrollment and Identification microservices.

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
System is online with default quality checkers loaded.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-NOF-REG-01 | Enrollment Service No-Face Rejection | Upload solid gray image to enrollment face upload endpoint. | file: gray_dummy.jpg | HTTP 422, error.code: quality_check_failed, quality_code: no_face. | HTTP 422 with structured quality rejection details. | PASSED | Enrollment validation blocked gray image successfully. |
| TC-NOF-IDENT-01 | Identification Service No-Face Rejection | Upload solid gray image to identification endpoint. | file: gray_dummy.jpg | HTTP 422, error.code: quality_check_failed, quality_code: no_face. | HTTP 422 with structured quality rejection details. | PASSED | Identification validation blocked query image. |

## 7. Detailed Test Case Executions
### [TC-NOF-REG-01] Enrollment Service No-Face Rejection
- **Objective**: Verify no-face validation on enrollment.
- **Scope**: Biometric pipeline validation.
- **Preconditions**: Candidate metadata created first.
- **Test Data**: `file: gray_dummy.jpg`
- **Test Steps**:
  1. Post solid gray JPEG image to /api/v1/embedding/generate/{uuid}.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: no_face.
- **Actual Result**: HTTP 422 with structured quality rejection details.
- **API Used**: `POST /api/v1/embedding/generate/{uuid}`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: image=@gray_dummy.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "no_face",
      "description": "No face was detected in the image"
    }
  }
}
```
- **Edge Cases**: Landscape images, cartoon faces.
- **Error Cases**: Service timeout.
- **Pass / Fail**: **PASSED**
- **Remarks**: Enrollment validation blocked gray image successfully.
- **Screenshot Placeholder**: `[Screenshot: TC-NOF-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:33:55 | enrollment_service.services.enrollment | WARN | Face quality validation failed: no_face
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-NOF-IDENT-01] Identification Service No-Face Rejection
- **Objective**: Verify no-face validation on identification.
- **Scope**: Biometric pipeline validation.
- **Preconditions**: None.
- **Test Data**: `file: gray_dummy.jpg`
- **Test Steps**:
  1. Post solid gray JPEG image to /identify.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: no_face.
- **Actual Result**: HTTP 422 with structured quality rejection details.
- **API Used**: `POST /identify`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: file=@gray_dummy.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "no_face",
      "description": "No face was detected in the image"
    }
  }
}
```
- **Edge Cases**: Paintings, landscape photographs.
- **Error Cases**: ONNX execution fail.
- **Pass / Fail**: **PASSED**
- **Remarks**: Identification validation blocked query image.
- **Screenshot Placeholder**: `[Screenshot: TC-NOF-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:34:02 | face_identification.api.identify | WARN | Face quality validation failed: no_face
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Send a gray square image payload to both service endpoints.
2. Ensure response matches standard quality check error formats.

## 9. Expected Result (Overall)
Rejection with HTTP status 422 and error key 'no_face' on both services.

## 10. Actual Result (Overall)
HTTP 422 code and quality_code: no_face correctly returned by both services.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Prevents downstream database search and registration on non-face entities.

## 13. Recommendations
Keep logs of such failures for analytics and debugging.

## 14. Conclusion
No face rejection logic functions as expected across both services.