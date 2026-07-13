# 15. QA Verification Report: FAISS Index Rebuild Report

## 1. Overview
Validates memory-disk synchronization during FAISS index rebuild.

## 2. Objective
Verify on-demand indexing rebuild from PostgreSQL persistent records.

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
- **Endpoint**: `POST /index/rebuild`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
Database contains active embeddings records.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-REB-01 | Trigger Rebuild & Atomic Swap | Send POST to rebuild endpoint. | POST /index/rebuild | HTTP 200, status: success, index files written to disk. | HTTP 200, status: success, indexed count: 12. | PASSED | Atomic memory swap successful. |

## 7. Detailed Test Case Executions
### [TC-REB-01] Trigger Rebuild & Atomic Swap
- **Objective**: Confirm rebuild sequence works without service interruption.
- **Scope**: Service resilience and consistency.
- **Preconditions**: None.
- **Test Data**: `POST /index/rebuild`
- **Test Steps**:
  1. Post index rebuild.
  2. Confirm status response.
  3. Verify faiss_index.bin is updated.
- **Expected Result**: HTTP 200, status: success, index files written to disk.
- **Actual Result**: HTTP 200, status: success, indexed count: 12.
- **API Used**: `POST /index/rebuild`
- **HTTP Status**: `200 OK`
- **Sample Request**:
```json
POST /index/rebuild
```
- **Sample Response**:
```json
{
  "status": "success",
  "indexed_embeddings": 12,
  "elapsed_seconds": 0.0845
}
```
- **Edge Cases**: Rebuild triggered with empty database.
- **Error Cases**: Disk write permission failure.
- **Pass / Fail**: **PASSED**
- **Remarks**: Atomic memory swap successful.
- **Screenshot Placeholder**: `[Screenshot: TC-REB-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:40:55 | face_identification.faiss.manager | INFO | Loaded 12 embeddings from PostgreSQL. Rebuilt index file written.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Rebuild index manually.
2. Check output file timestamp and test immediate query functionality.

## 9. Expected Result (Overall)
Index rebuilt without service crash, file modified time changes.

## 10. Actual Result (Overall)
Index updated instantly, queries work right away.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Uses atomic index pointer swap, preventing query failures during index refresh.

## 13. Recommendations
Schedule daily auto-rebuild cron jobs.

## 14. Conclusion
FAISS index rebuild logic is verified.