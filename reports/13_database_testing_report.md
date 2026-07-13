# 13. QA Verification Report: Database Testing Report

## 1. Overview
Validates PostgreSQL schema execution and transactional operations.

## 2. Objective
Verify candidate profiles and vectors can be read, written, and deleted.

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
- **Endpoint**: `Direct database queries & API mapping`
- **Microservices Involved**: Enrollment Service (Port 8000), Face Identification Service (Port 8001)

## 5. Prerequisites
PostgreSQL database running, migrations completed.

## 6. Summary Test Cases Table
| Test ID | Test Name | Description | Input Data | Expected Result | Actual Result | Status | Remarks |
|---------|-----------|-------------|------------|-----------------|---------------|--------|---------|
| TC-DB-01 | SQL Persistence & Cascading Deletion | Register, query embedding, and delete candidate verifying SQL cascades. | Create candidate and face vector, then execute DELETE. | Deleting candidate deletes corresponding face vector cascadingly. | Both candidate and face embedding record deleted on database cascade checks. | PASSED | Checked using pgAdmin and SQL console logs. |

## 7. Detailed Test Case Executions
### [TC-DB-01] SQL Persistence & Cascading Deletion
- **Objective**: Verify foreign key cascading behavior.
- **Scope**: Data tier testing.
- **Preconditions**: Clean target candidate space.
- **Test Data**: `Create candidate and face vector, then execute DELETE.`
- **Test Steps**:
  1. SQL Insert test candidate.
  2. SQL Insert embedding linked to candidate.
  3. Delete candidate.
  4. Query embeddings table to confirm entry is deleted.
- **Expected Result**: Deleting candidate deletes corresponding face vector cascadingly.
- **Actual Result**: Both candidate and face embedding record deleted on database cascade checks.
- **API Used**: `SQL Query / Alembic Schema`
- **HTTP Status**: `N/A (SQL Check)`
- **Sample Request**:
```json
DELETE FROM candidates WHERE candidate_id = 'DB_TEST_1';
```
- **Sample Response**:
```json
DELETE 1
Query: SELECT count(*) FROM face_embeddings WHERE candidate_uuid = '...';
Count: 0
```
- **Edge Cases**: Orphaned embeddings, constraint validation failures.
- **Error Cases**: Connection pool depletion.
- **Pass / Fail**: **PASSED**
- **Remarks**: Checked using pgAdmin and SQL console logs.
- **Screenshot Placeholder**: `[Screenshot: TC-DB-01_evidence.png]`
- **Log Placeholder**: 
```
[LOG] 2026-07-13 09:39:05 | sqlalchemy.engine | INFO | ROLLBACK or COMMIT executed.
```
- **Execution Date**: 2026-07-13
- **Tester Name**: Senior QA Engineer / Test Architect

---

## 8. Test Procedure
1. Create a candidate and its embedding.
2. Confirm database counts match.
3. Delete candidate and verify zero orphans.

## 9. Expected Result (Overall)
Foreign key relationships delete child elements on candidate delete.

## 10. Actual Result (Overall)
Verification queries show that the children are cleanly removed.

## 11. Pass/Fail Status
- **Overall Status**: **PASSED**

## 12. Remarks
Saves disk space and ensures no orphan biometric data.

## 13. Recommendations
Create automated weekly cleanup scripts for orphaned rows.

## 14. Conclusion
Database referential integrity is stable.