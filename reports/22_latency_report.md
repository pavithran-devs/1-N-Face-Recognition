# 22. QA Verification Report: Latency Report

## 1. Overview
Details latency profiles of face processing pipelines and vector query operations.

## 2. Objective
Verify execution metrics across all pipeline steps are within 200ms budget.

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
System pre-warmed to prevent initial CPU cold start overhead.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-LAT-01 | Pipeline Latency Profiling | Measure timing breakdown during a search check. | Standard face image file. | Average execution time <= 200.0 ms. | Total elapsed: 142.6 ms. | PASSED | Timing metrics detailed below. |

## 7. Detailed Test Case Executions
### [TC-LAT-01] Pipeline Latency Profiling
- **Objective**: Profile latency breakdown.
- **Scope**: Performance profiling.
- **Preconditions**: Warm models.
- **Test Data**: `Standard face image file.`
- **Test Steps**:
  1. Send image to /identify.
  2. Capture timings field from response.
- **Expected Result**: Average execution time <= 200.0 ms.
- **Actual Result**: Total elapsed: 142.6 ms.
- **API Used**: `POST /identify`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
Multipart Form Data: file=@face.jpg
```
- **Sample Response**:
```json
{
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
- **Edge Cases**: Large images (longer decoding/resizing), multi-threaded requests.
- **Error Cases**: Hardware throttling.
- **Pass / Fail**: **PASSED**
- **Remarks**: Timing metrics detailed below.
- **Screenshot Placeholder**: `[Screenshot: TC-LAT-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:43:45 | face_identification.api.identify | INFO | Timing Profiler: Decode=8.5ms, SCRFD=42.1ms, ArcFace=88.3ms, FAISS=0.15ms
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Run sample identification requests.
2. Extract timings dictionary to check step bottlenecks.

## 9. Expected Result (Overall)
All component times must be within operational limits, total under 200ms.

## 10. Actual Result (Overall)
Cumulative latency is 142.65ms, with ArcFace extraction being the primary consumer (88.3ms).

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
CPU execution provider was used.

## 13. Recommendations
Move to CUDA (GPU Execution Provider) for production to decrease ArcFace times to ~15ms.

## 14. Conclusion
Platform speed profiles meet latency requirements.