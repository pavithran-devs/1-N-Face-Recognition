# 18. QA Verification Report: Accuracy Evaluation Report

## 1. Overview
Evaluates overall match accuracy of the face recognition platform on a sample test subset.

## 2. Objective
Verify matching precision remains high under cross-verification criteria.

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
- **Endpoint**: `N/A (Evaluation Runner Results)`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
Evaluation dataset with registered templates and multiple testing images.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-ACC-01 | Subset Accuracy Run | Execute verification runner against LFW subset. | 10 enrolled candidates, 20 test query photos. | Accuracy >= 95%. | Accuracy evaluated at 100.0%. | PASSED | All test images resolved correctly. |

## 7. Detailed Test Case Executions
### [TC-ACC-01] Subset Accuracy Run
- **Objective**: Measure overall system accuracy.
- **Scope**: Accuracy audit.
- **Preconditions**: 10 distinct subjects enrolled.
- **Test Data**: `10 enrolled candidates, 20 test query photos.`
- **Test Steps**:
  1. Run run_comprehensive_tests.py script.
  2. Observe evaluation metrics output.
- **Expected Result**: Accuracy >= 95%.
- **Actual Result**: Accuracy evaluated at 100.0%.
- **API Used**: `Internal Runner`
- **HTTP Status**: `N/A`
- **Sample Request**:
```json
run_comprehensive_tests.py --eval-size 10
```
- **Sample Response**:
```json
{
  "total_evaluated": 20,
  "correct": 20,
  "accuracy": 1.00
}
```
- **Edge Cases**: Identical twins, changing makeup, lighting variances.
- **Error Cases**: Under-enrolled targets.
- **Pass / Fail**: **PASSED**
- **Remarks**: All test images resolved correctly.
- **Screenshot Placeholder**: `[Screenshot: TC-ACC-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:42:15 | comprehensive_verification | INFO | Test Run Completed. Accuracy: 100.0%
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Execute the comprehensive evaluation tests runner.
2. Collect accuracy summary data.

## 9. Expected Result (Overall)
Accuracy must be high (>95%) with clear differentiation of subjects.

## 10. Actual Result (Overall)
100.0% accuracy on LFW sub-sample.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Validated using LFW deepfunneled pictures.

## 13. Recommendations
Run evaluations on larger datasets (e.g. 1000 candidates) to find real boundary cases.

## 14. Conclusion
System matching accuracy is high.