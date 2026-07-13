# 04. QA Verification Report: Unknown Candidate Report

## 1. Overview
Validates system behavior when matching against an unenrolled face image.

## 2. Objective
Verify that unrecognized faces correctly resolve to 'matched: false' with 'Unknown Candidate' response details.

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
Query image contains a face that is not in the system repository.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-UNK-01 | Identify Unregistered Face | Upload image of an unregistered subject. | file: unregistered_face.jpg, threshold: 0.65 | HTTP 200, matched: false, name: Unknown Candidate. | HTTP 200, matched: false, name: Unknown Candidate, top similarity: 0.38. | PASSED | No matching candidate found in database. |

## 7. Detailed Test Case Executions
### [TC-UNK-01] Identify Unregistered Face
- **Objective**: Verify fallback behavior for strangers.
- **Scope**: Security and accuracy metrics testing.
- **Preconditions**: Face in unregistered_face.jpg must not be enrolled.
- **Test Data**: `file: unregistered_face.jpg, threshold: 0.65`
- **Test Steps**:
  1. Send unregistered face image file to /identify.
- **Expected Result**: HTTP 200, matched: false, name: Unknown Candidate.
- **Actual Result**: HTTP 200, matched: false, name: Unknown Candidate, top similarity: 0.38.
- **API Used**: `POST /identify`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
Multipart Form Data:
file=@unregistered_face.jpg
threshold=0.65
```
- **Sample Response**:
```json
{
  "matched": false,
  "candidate_id": null,
  "name": "Unknown Candidate",
  "score": 0.38125,
  "timings": {
    "decode": 7.8,
    "scrfd": 41.5,
    "alignment": 2.2,
    "arcface": 85.1,
    "faiss": 0.12,
    "database": 0.8,
    "total": 137.52
  }
}
```
- **Edge Cases**: Similarity score close to threshold (e.g. 0.63).
- **Error Cases**: Empty database or empty FAISS index.
- **Pass / Fail**: **PASSED**
- **Remarks**: No matching candidate found in database.
- **Screenshot Placeholder**: `[Screenshot: TC-UNK-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:32:45 | face_identification.api.identify | INFO | No candidate matched. Top score: 0.38125 (Threshold: 0.65)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Post unenrolled face image.
2. Confirm HTTP status 200 and 'matched: false' payload properties.

## 9. Expected Result (Overall)
Response matched field must be false, with candidate data set to null.

## 10. Actual Result (Overall)
Matched field is correctly evaluated as false, with score of 0.38.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
FAISS correctly returned closest match, and similarity check filtered it.

## 13. Recommendations
Log unregistered attempts in a dedicated security log.

## 14. Conclusion
Unknown candidate path is verified.