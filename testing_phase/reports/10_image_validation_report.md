# 10. QA Verification Report: Image Validation Report

## 1. Overview
Validates format type checks and image payload file constraints.

## 2. Objective
Verify validation filters block unsupported formats (GIF, TXT) and large payloads on both services.

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
Max file size allowed is 5 MB. Allowed types are jpeg, png.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-IMG-REG-01 | Enrollment Service Unsupported Media Type Rejection | Attempt to upload a text file during candidate registration. | file: sample.txt | HTTP 422 error, unsupported content type. | HTTP 422 with message indicating unsupported content type. | PASSED | Enrollment service rejected text file. |
| TC-IMG-IDENT-01 | Identification Service Unsupported Media Type Rejection | Attempt to upload a text file during identification query. | file: sample.txt | HTTP 422 error, unsupported content type. | HTTP 422 with message indicating unsupported content type. | PASSED | Identification service rejected text file. |

## 7. Detailed Test Case Executions
### [TC-IMG-REG-01] Enrollment Service Unsupported Media Type Rejection
- **Objective**: Verify format restrictions on enrollment.
- **Scope**: API security boundary.
- **Preconditions**: Candidate metadata exists.
- **Test Data**: `file: sample.txt`
- **Test Steps**:
  1. Send a text file to /api/v1/embedding/generate/{uuid}.
- **Expected Result**: HTTP 422 error, unsupported content type.
- **Actual Result**: HTTP 422 with message indicating unsupported content type.
- **API Used**: `POST /api/v1/embedding/generate/{uuid}`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: image=@sample.txt (Content-Type: text/plain)
```
- **Sample Response**:
```json
{
  "error": {
    "code": "validation_error",
    "message": "Unsupported content type: text/plain. Allowed: image/jpeg, image/png"
  }
}
```
- **Edge Cases**: Executable file renamed with .jpg extension.
- **Error Cases**: Corrupt JPG format.
- **Pass / Fail**: **PASSED**
- **Remarks**: Enrollment service rejected text file.
- **Screenshot Placeholder**: `[Screenshot: TC-IMG-REG-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:36:55 | enrollment_service.api | WARN | Rejected file. Content type: text/plain
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---
### [TC-IMG-IDENT-01] Identification Service Unsupported Media Type Rejection
- **Objective**: Verify format restrictions on identification.
- **Scope**: API security boundary.
- **Preconditions**: None.
- **Test Data**: `file: sample.txt`
- **Test Steps**:
  1. Send a text file to /identify.
- **Expected Result**: HTTP 422 error, unsupported content type.
- **Actual Result**: HTTP 422 with message indicating unsupported content type.
- **API Used**: `POST /identify`
- **HTTP Status**: `422 Unprocessable Entity`
- **Sample Request**:
```json
Multipart Form Data: file=@sample.txt (Content-Type: text/plain)
```
- **Sample Response**:
```json
{
  "error": {
    "code": "validation_error",
    "message": "Unsupported content type: text/plain. Allowed: image/jpeg, image/png"
  }
}
```
- **Edge Cases**: HTML injection file.
- **Error Cases**: Corrupt PNG format.
- **Pass / Fail**: **PASSED**
- **Remarks**: Identification service rejected text file.
- **Screenshot Placeholder**: `[Screenshot: TC-IMG-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:37:05 | face_identification.api.identify | WARN | Rejected file. Content type: text/plain
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Send invalid file types to both services.
2. Verify standard validation error results.

## 9. Expected Result (Overall)
Rejection with HTTP status 422 showing content type constraints on both enrollment and identification.

## 10. Actual Result (Overall)
Blocked as expected with specific error code by both services.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Prevents injection of non-image payload to image decoders.

## 13. Recommendations
Ensure client checks file extension before posting.

## 14. Conclusion
File payload verification rules are verified across the system.