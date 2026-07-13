# 03. QA Verification Report: Candidate Identification Report

## 1. Overview
Validates 1:N face identification queries matching enrolled candidates.

## 2. Objective
Verify that a clear, non-blurry face image resolves to the correct enrolled candidate profile.

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
- **Endpoint**: `POST /identify`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
Candidate John Doe (EMP101) must be enrolled and indexed in FAISS.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-IDENT-01 | Identify Enrolled Candidate | Query the system using a secondary photo of John Doe. | file: john_secondary.jpg, threshold: 0.65, top_k: 5 | HTTP 200, matched: true, name: John Doe, similarity score > 0.65. | HTTP 200, matched: true, candidate_id: EMP101, name: John Doe, score: 0.81. | PASSED | Match was resolved successfully. |

## 7. Detailed Test Case Executions
### [TC-IDENT-01] Identify Enrolled Candidate
- **Objective**: Verify 1:N match resolving.
- **Scope**: Core face identification pipeline.
- **Preconditions**: John Doe enrolled and FAISS rebuilt.
- **Test Data**: `file: john_secondary.jpg, threshold: 0.65, top_k: 5`
- **Test Steps**:
  1. Send multipart/form-data request containing image to /identify.
- **Expected Result**: HTTP 200, matched: true, name: John Doe, similarity score > 0.65.
- **Actual Result**: HTTP 200, matched: true, candidate_id: EMP101, name: John Doe, score: 0.81.
- **API Used**: `POST /identify`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
Multipart Form Data:
file=@john_secondary.jpg
threshold=0.65
top_k=5
```
- **Sample Response**:
```json
{
  "matched": true,
  "candidate_id": "EMP101",
  "name": "John Doe",
  "score": 0.81425,
  "timings": {
    "decode": 8.5,
    "scrfd": 42.1,
    "alignment": 2.4,
    "arcface": 88.3,
    "faiss": 0.15,
    "database": 1.2,
    "total": 142.65
  }
}
```
- **Edge Cases**: Minor hair changes, accessories (glasses), facial expression.
- **Error Cases**: Database lookup fail, index search failure.
- **Pass / Fail**: **PASSED**
- **Remarks**: Match was resolved successfully.
- **Screenshot Placeholder**: `[Screenshot: TC-IDENT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:32:00 | face_identification.api.identify | INFO | Match found! EMP101 John Doe (Score: 0.81425)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Run face identification request with file attachment.
2. Confirm match results and execution time.

## 9. Expected Result (Overall)
Correct candidate resolved with highly accurate score and standard timing details.

## 10. Actual Result (Overall)
Successful match with score 0.81 within 142.6ms.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
ArcFace generates clean normalized vectors, FAISS works correctly.

## 13. Recommendations
Add support for bounding box response in JSON payload.

## 14. Conclusion
The candidate identification pipeline is functional and ready.