# Verification Log Formats

This document defines the structured log formats used across the Face Recognition system modules. All microservices output logs to stdout and write them to dedicated log files (`enrollment_service.log` and `face_identification.log`).

## Common Log Standard
```
Timestamp | Module | API | Status | Latency | Candidate ID | Similarity | Threshold | Database Status | FAISS Status | Error
```

---

## 1. Registration Logs
- **Trigger**: During candidate metadata or embedding creation.
- **Format**:
```
2026-07-13 09:30:12 | enrollment_service.services.enrollment | POST /api/v1/candidates/ | SUCCESS | 12.4ms | c001f35f-3315-4ba8-bb58-372986429f4a | N/A | N/A | connected | N/A | None
2026-07-13 09:30:15 | enrollment_service.services.enrollment | POST /api/v1/embedding/generate/c001f35f-3315-4ba8-bb58-372986429f4a | SUCCESS | 148.5ms | c001f35f-3315-4ba8-bb58-372986429f4a | N/A | N/A | connected | N/A | None
```

## 2. Identification Logs
- **Trigger**: During 1:N face identification queries.
- **Format**:
```
2026-07-13 09:32:00 | face_identification.api.identify | POST /identify | MATCH_FOUND | 142.6ms | c001f35f-3315-4ba8-bb58-372986429f4a | 0.8142 | 0.65 | connected | loaded | None
2026-07-13 09:32:45 | face_identification.api.identify | POST /identify | NO_MATCH | 137.5ms | null | 0.3812 | 0.65 | connected | loaded | None
```

## 3. Database Logs
- **Trigger**: SQLAlchemy connection pool events and transaction rollbacks.
- **Format**:
```
2026-07-13 09:39:05 | sqlalchemy.engine | SQL_TRANSACTION | SUCCESS | 2.1ms | N/A | N/A | N/A | active_connections=3 | N/A | None
2026-07-13 09:47:45 | face_identification.database | DB_RECONNECT | RECOVERED | 1500ms | N/A | N/A | N/A | reconnected | N/A | None
```

## 4. FAISS Logs
- **Trigger**: Index search queries, rebuild operations, and file saves.
- **Format**:
```
2026-07-13 09:40:02 | face_identification.faiss.manager | INDEX_SEARCH | SUCCESS | 0.15ms | N/A | N/A | N/A | N/A | loaded (size=12) | None
2026-07-13 09:40:55 | face_identification.faiss.manager | INDEX_REBUILD | SUCCESS | 84.5ms | N/A | N/A | N/A | connected | synced_to_disk | None
```

## 5. Health Logs
- **Trigger**: Standard service heartbeat polling checks.
- **Format**:
```
2026-07-13 09:41:12 | face_identification.api.health | GET /health | SUCCESS | 0.8ms | N/A | N/A | N/A | connected | loaded | None
```

## 6. Metrics Logs
- **Trigger**: Telemetry reads.
- **Format**:
```
2026-07-13 09:41:45 | face_identification.api.metrics | GET /metrics | SUCCESS | 1.1ms | N/A | N/A | N/A | connected | loaded | None
```

## 7. API Logs
- **Trigger**: Routing requests and validation rejections.
- **Format**:
```
2026-07-13 09:37:05 | face_identification.api | POST /identify | VALIDATION_ERROR | 4.2ms | N/A | N/A | N/A | N/A | N/A | Unsupported content type
2026-07-13 09:37:45 | enrollment_service.api | POST /api/v1/candidates/ | VALIDATION_ERROR | 3.5ms | N/A | N/A | N/A | N/A | N/A | Input validation failed: 2 errors
```

## 8. Authentication Logs
- **Trigger**: Access validation checks (CORS and rate limits).
- **Format**:
```
2026-07-13 09:49:15 | face_identification.security | OPTIONS /identify | ALLOWED | 0.5ms | N/A | N/A | N/A | N/A | N/A | None
2026-07-13 09:44:12 | face_identification.middleware | POST /identify | BLOCKED_RATE_LIMIT | 0.2ms | N/A | N/A | N/A | N/A | N/A | Too Many Requests (429)
```

## 9. Errors Logs
- **Trigger**: System crashes, timeouts, and hardware issues.
- **Format**:
```
2026-07-13 09:34:02 | face_identification.api.identify | POST /identify | PIPELINE_ERROR | 124.2ms | N/A | N/A | N/A | connected | loaded | quality_check_failed: no_face
2026-07-13 09:45:02 | face_identification.app | POST /identify | TIMEOUT | 10000ms | N/A | N/A | N/A | connected | loaded | Timeout error occurred
```

## 10. Load Test Logs
- **Trigger**: Parallel requests from k6.
- **Format**:
```
2026-07-13 09:44:05 | face_identification.load_tester | VU_REQUEST | SUCCESS | 215.4ms | c001f35f-3315-4ba8-bb58-372986429f4a | 0.7954 | 0.65 | connected | loaded | None
2026-07-13 09:44:06 | face_identification.load_tester | VU_REQUEST | RATE_LIMITED | 0.3ms | null | N/A | 0.65 | connected | loaded | HTTP 429 Too Many Requests
```

## 11. Stress Test Logs
- **Trigger**: High density traffic from Locust.
- **Format**:
```
2026-07-13 09:45:01 | face_identification.stress_tester | LOAD_STRESS | TIMEOUT | 5000ms | null | N/A | 0.65 | connected | loaded | HTTP 504 Gateway Timeout
2026-07-13 09:45:02 | face_identification.stress_tester | LOAD_STRESS | SUCCESS | 895.4ms | c001f35f-3315-4ba8-bb58-372986429f4a | 0.8012 | 0.65 | connected | loaded | None
```