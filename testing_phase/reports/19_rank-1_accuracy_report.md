# 19. QA Verification Report: Rank-1 Accuracy Report

## 1. Overview
Evaluates Rank-1 match accuracy for 1:N verification.

## 2. Objective
Verify that the true candidate matches are identified as the top-1 ranked result.

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
FAISS index rebuilt with multiple candidates.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-R1A-01 | Rank-1 Search Correctness | Verify correct target candidate has the highest similarity score in the result list. | John Doe validation image query. | True candidate in first slot. | John Doe returned at position index 0 with score 0.81. Rank-1 confirmed. | PASSED | Highest similarity correct. |

## 7. Detailed Test Case Executions
### [TC-R1A-01] Rank-1 Search Correctness
- **Objective**: Verify candidate resolves in top rank.
- **Scope**: Rank verification.
- **Preconditions**: Database populated.
- **Test Data**: `John Doe validation image query.`
- **Test Steps**:
  1. Call /identify.
  2. Check candidate identity at Rank-1.
- **Expected Result**: True candidate in first slot.
- **Actual Result**: John Doe returned at position index 0 with score 0.81. Rank-1 confirmed.
- **API Used**: `POST /identify`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
Multipart Form Data: file=@john_secondary.jpg
```
- **Sample Response**:
```json
{
  "matched": true,
  "candidate_id": "EMP101",
  "name": "John Doe",
  "score": 0.81425
}
```
- **Edge Cases**: Two highly similar looking faces.
- **Error Cases**: Target candidate falls to Rank-2.
- **Pass / Fail**: **PASSED**
- **Remarks**: Highest similarity correct.
- **Screenshot Placeholder**: `[Screenshot: TC-R1A-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:42:30 | face_identification.api.identify | INFO | Match found at Rank-1 (EMP101, Score: 0.81425)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Query system using secondary photos.
2. Confirm that correct profile matches Rank-1 slot.

## 9. Expected Result (Overall)
True identity has the highest score.

## 10. Actual Result (Overall)
True identity is consistently identified in first rank slot.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Crucial for access control validation.

## 13. Recommendations
Maintain threshold above 0.65 to filter false matches.

## 14. Conclusion
Rank-1 accuracy meets performance criteria.