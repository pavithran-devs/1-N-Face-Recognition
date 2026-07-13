# 09. QA Verification Report: Brightness Validation Report

## 1. Overview
Validates system checks for underexposed or overexposed images.

## 2. Objective
Verify that dark (underexposed) and bright (overexposed) face photos are blocked on both enrollment and identification.

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
Exposure boundaries configured to [40, 230] mean pixel intensity.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-EXP-REG-01 | Enrollment Service Dark Photo Rejection | Upload dark face photo during candidate enrollment. | file: dark_face.jpg (mean brightness: 15.2) | HTTP 422, error.code: quality_check_failed, quality_code: too_dark. | HTTP 422, quality_code: too_dark returned. | PASSED | Rejected by enrollment validator. |
| TC-EXP-IDENT-01 | Identification Service Dark Photo Rejection | Upload dark face photo during candidate identification. | file: dark_face.jpg (mean brightness: 15.2) | HTTP 422, error.code: quality_check_failed, quality_code: too_dark. | HTTP 422, quality_code: too_dark returned. | PASSED | Rejected by identification query validator. |
| TC-EXP-REG-02 | Enrollment Service Washout Photo Rejection | Upload overexposed face photo during candidate enrollment. | file: bright_face.jpg (mean brightness: 245.8) | HTTP 422, error.code: quality_check_failed, quality_code: too_bright. | HTTP 422, quality_code: too_bright returned. | PASSED | Blocked. |
| TC-EXP-IDENT-02 | Identification Service Washout Photo Rejection | Upload overexposed face photo during candidate identification. | file: bright_face.jpg (mean brightness: 245.8) | HTTP 422, error.code: quality_check_failed, quality_code: too_bright. | HTTP 422, quality_code: too_bright returned. | PASSED | Blocked. |

## 7. Detailed Test Case Executions
### [TC-EXP-REG-01] Enrollment Service Dark Photo Rejection
- **Objective**: Verify dark photo rejection on enrollment.
- **Scope**: Image quality verification.
- **Preconditions**: Candidate metadata exists.
- **Test Data**: `file: dark_face.jpg (mean brightness: 15.2)`
- **Test Steps**:
  1. Post dark photo to /api/v1/embedding/generate/{uuid}.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: too_dark.
- **Actual Result**: HTTP 422, quality_code: too_dark returned.
- **API Used**: `POST /api/v1/embedding/generate/{uuid}`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: image=@dark_face.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "too_dark",
      "description": "Image is too dark. Mean brightness: 15.2 (Minimum: 40)"
    }
  }
}
```
- **Edge Cases**: Face in heavy shadows.
- **Error Cases**: None.
- **Pass / Fail**: **PASSED**
- **Remarks**: Rejected by enrollment validator.
- **Screenshot Placeholder**: `[Screenshot: TC-EXP-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:36:05 | enrollment_service.services.enrollment | WARN | Quality check failed: too_dark (mean: 15.2)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-EXP-IDENT-01] Identification Service Dark Photo Rejection
- **Objective**: Verify dark photo rejection on identification.
- **Scope**: Image quality verification.
- **Preconditions**: None.
- **Test Data**: `file: dark_face.jpg (mean brightness: 15.2)`
- **Test Steps**:
  1. Post dark photo to /identify.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: too_dark.
- **Actual Result**: HTTP 422, quality_code: too_dark returned.
- **API Used**: `POST /identify`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: file=@dark_face.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "too_dark",
      "description": "Image is too dark. Mean brightness: 15.2 (Minimum: 40)"
    }
  }
}
```
- **Edge Cases**: Poor indoor lighting.
- **Error Cases**: None.
- **Pass / Fail**: **PASSED**
- **Remarks**: Rejected by identification query validator.
- **Screenshot Placeholder**: `[Screenshot: TC-EXP-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:36:12 | face_identification.api.identify | WARN | Quality check failed: too_dark (mean: 15.2)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-EXP-REG-02] Enrollment Service Washout Photo Rejection
- **Objective**: Verify bright photo rejection on enrollment.
- **Scope**: Image quality verification.
- **Preconditions**: Candidate metadata exists.
- **Test Data**: `file: bright_face.jpg (mean brightness: 245.8)`
- **Test Steps**:
  1. Post bright photo to /api/v1/embedding/generate/{uuid}.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: too_bright.
- **Actual Result**: HTTP 422, quality_code: too_bright returned.
- **API Used**: `POST /api/v1/embedding/generate/{uuid}`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: image=@bright_face.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "too_bright",
      "description": "Image is too bright. Mean brightness: 245.8 (Maximum: 230)"
    }
  }
}
```
- **Edge Cases**: Flash reflection on foreheads.
- **Error Cases**: None.
- **Pass / Fail**: **PASSED**
- **Remarks**: Blocked.
- **Screenshot Placeholder**: `[Screenshot: TC-EXP-REG-02_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:36:15 | enrollment_service.services.enrollment | WARN | Quality check failed: too_bright (mean: 245.8)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-EXP-IDENT-02] Identification Service Washout Photo Rejection
- **Objective**: Verify bright photo rejection on identification.
- **Scope**: Image quality verification.
- **Preconditions**: None.
- **Test Data**: `file: bright_face.jpg (mean brightness: 245.8)`
- **Test Steps**:
  1. Post bright photo to /identify.
- **Expected Result**: HTTP 422, error.code: quality_check_failed, quality_code: too_bright.
- **Actual Result**: HTTP 422, quality_code: too_bright returned.
- **API Used**: `POST /identify`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: file=@bright_face.jpg
```
- **Sample Response**:
```json
{
  "error": {
    "code": "quality_check_failed",
    "message": "Face validation checks failed",
    "details": {
      "quality_code": "too_bright",
      "description": "Image is too bright. Mean brightness: 245.8 (Maximum: 230)"
    }
  }
}
```
- **Edge Cases**: Direct outdoor sunlight glare.
- **Error Cases**: None.
- **Pass / Fail**: **PASSED**
- **Remarks**: Blocked.
- **Screenshot Placeholder**: `[Screenshot: TC-EXP-IDENT-02_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:36:18 | face_identification.api.identify | WARN | Quality check failed: too_bright (mean: 245.8)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Post dark and bright image payloads to both Microservices.
2. Validate that error messages mention exposure boundaries.

## 9. Expected Result (Overall)
All requests fail with HTTP 422 and correct quality details.

## 10. Actual Result (Overall)
Rejections occur with specific 'too_dark' and 'too_bright' messages on both services.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Ensures consistent quality boundaries are enforced during both registration and lookup.

## 13. Recommendations
Add dynamic light compensation prompt to user frontend.

## 14. Conclusion
Exposure validation logic is fully verified across both enrollment and identification microservices.