# 17. QA Verification Report: Metrics Endpoint Report

## 1. Overview
Validates tracking metrics and request analytics tracking.

## 2. Objective
Verify request performance telemetry data is captured at /metrics endpoint.

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
- **Endpoint**: `GET /metrics`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
Some sample transactions must have run beforehand.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-MET-01 | Verify Telemetry Counters | Check /metrics stats output. | GET /metrics | HTTP 200, contains query count, positive match counts, and averages. | HTTP 200, output verified. | PASSED | Metrics match expectations. |

## 7. Detailed Test Case Executions
### [TC-MET-01] Verify Telemetry Counters
- **Objective**: Ensure metrics endpoint functions correctly.
- **Scope**: Observability validation.
- **Preconditions**: Queries have been processed.
- **Test Data**: `GET /metrics`
- **Test Steps**:
  1. Send requests to /identify.
  2. Query /metrics.
  3. Verify counts incremented.
- **Expected Result**: HTTP 200, contains query count, positive match counts, and averages.
- **Actual Result**: HTTP 200, output verified.
- **API Used**: `GET /metrics`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
GET /metrics
```
- **Sample Response**:
```json
{
  "total_searches": 22,
  "matched_searches": 10,
  "hit_rate": 0.4545,
  "avg_latency_ms": 141.25
}
```
- **Edge Cases**: Zero division handling prior to first search.
- **Error Cases**: Metrics cache failure.
- **Pass / Fail**: **PASSED**
- **Remarks**: Metrics match expectations.
- **Screenshot Placeholder**: `[Screenshot: TC-MET-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:41:45 | face_identification.api.metrics | INFO | Telemetry logged.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Inspect values after run activities.
2. Confirm fields match query totals.

## 9. Expected Result (Overall)
Total search matches are tracked in real-time.

## 10. Actual Result (Overall)
Telemetry metrics are logged correctly.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Highly useful for production monitoring dashboards.

## 13. Recommendations
Integrate endpoint output directly with Prometheus collector formats.

## 14. Conclusion
Telemetry output functions correctly.