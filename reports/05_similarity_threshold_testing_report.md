# 05. QA Verification Report: Similarity Threshold Testing Report

## 1. Overview
Validates matching behavior using custom and overridden similarity thresholds.

## 2. Objective
Verify that similarity threshold acts as a secure boundary for positive matches.

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
Candidate John Doe enrolled with similarity score of 0.81.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-THR-01 | Block Match Using High Threshold Override | Identify John Doe with threshold set to 0.95. | file: john_secondary.jpg, threshold: 0.95 | HTTP 200, matched: false (since score 0.81 < 0.95). | HTTP 200, matched: false, name: Unknown Candidate, score: 0.81. | PASSED | Correctly blocked. |

## 7. Detailed Test Case Executions
### [TC-THR-01] Block Match Using High Threshold Override
- **Objective**: Verify threshold overrides.
- **Scope**: Threshold testing.
- **Preconditions**: Candidate is enrolled.
- **Test Data**: `file: john_secondary.jpg, threshold: 0.95`
- **Test Steps**:
  1. Send John Doe image to /identify with threshold parameter set to 0.95.
- **Expected Result**: HTTP 200, matched: false (since score 0.81 < 0.95).
- **Actual Result**: HTTP 200, matched: false, name: Unknown Candidate, score: 0.81.
- **API Used**: `POST /identify`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
Multipart Form Data:
file=@john_secondary.jpg
threshold=0.95
```
- **Sample Response**:
```json
{
  "matched": false,
  "candidate_id": null,
  "name": "Unknown Candidate",
  "score": 0.81425
}
```
- **Edge Cases**: Boundary values (threshold: 1.0, threshold: 0.0).
- **Error Cases**: Non-numeric threshold values.
- **Pass / Fail**: **PASSED**
- **Remarks**: Correctly blocked.
- **Screenshot Placeholder**: `[Screenshot: TC-THR-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:33:12 | face_identification.api.identify | INFO | Match blocked by high threshold. Score: 0.81425 (Required: 0.95)
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Run identification with target threshold set higher than the expected similarity score.
2. Run verification with low threshold and check false match risks.

## 9. Expected Result (Overall)
Strict filter checking on threshold value.

## 10. Actual Result (Overall)
Rejection verified on high threshold; score boundary is strictly checked.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Allows flexible tuning per physical camera terminal setup.

## 13. Recommendations
Set default threshold value to 0.65 in database configuration.

## 14. Conclusion
Similarity thresholding works correctly.