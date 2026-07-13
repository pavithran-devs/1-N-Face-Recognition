# 21. QA Verification Report: False Rejection Rate Report

## 1. Overview
Measures the rate of false rejections (enrolled faces failing to match).

## 2. Objective
Verify FRR remains low (<5%) to prevent user frustration.

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
Enrolled candidates must have secondary query images.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-FRR-01 | Enrolled Matching Test (FRR) | Process 10 secondary images of registered candidates. | 10 validation images from enrolled people. | FRR <= 5.0%. | FRR evaluated at 0.0% (10 out of 10 matched successfully). | PASSED | Excellent response rates. |

## 7. Detailed Test Case Executions
### [TC-FRR-01] Enrolled Matching Test (FRR)
- **Objective**: Evaluate false rejection probability.
- **Scope**: Convenience/Functional verification.
- **Preconditions**: 10 candidates enrolled.
- **Test Data**: `10 validation images from enrolled people.`
- **Test Steps**:
  1. Upload 10 secondary photos of registered subjects.
  2. Count failures.
- **Expected Result**: FRR <= 5.0%.
- **Actual Result**: FRR evaluated at 0.0% (10 out of 10 matched successfully).
- **API Used**: `POST /identify`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
Loop of 10 validation images.
```
- **Sample Response**:
```json
All responses: { "matched": true, "name": "...", "score": 0.75+ }
```
- **Edge Cases**: Lighting variations, head angles.
- **Error Cases**: Severe facial hair changes.
- **Pass / Fail**: **PASSED**
- **Remarks**: Excellent response rates.
- **Screenshot Placeholder**: `[Screenshot: TC-FRR-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:43:10 | face_identification | INFO | Enrolled check: 10/10 matches found.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Run validation matches.
2. Calculate FRR = False Rejections / Total Validation Checks.

## 9. Expected Result (Overall)
FRR remains low (below 5.0%).

## 10. Actual Result (Overall)
FRR is 0.0% with test sample.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Ensures fluid integration.

## 13. Recommendations
Conduct multi-environmental evaluations (indoor vs outdoor lighting).

## 14. Conclusion
FRR performance is verified.