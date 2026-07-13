# Final Pre-Deployment QA Checklist

Ensure all tests are run and signed off by the QA team before scheduling production release. Both Enrollment Microservice (port 8000) and Face Identification Microservice (port 8001) are fully validated.

## 1. Functional Tests
- [x] **01. Candidate Registration**: Verify candidate and embedding creation flow on Enrollment.
- [x] **02. Duplicate Candidate**: Confirm unique candidate_id and email restrictions on Enrollment.
- [x] **03. Candidate Identification**: Verify correct match for enrolled candidates on Identification.
- [x] **04. Unknown Candidate**: Confirm unmatched return format (matched=false) on Identification.
- [x] **05. Threshold Testing**: Confirm customizable match threshold parameter overrides on Identification.

## 2. Image Quality & Preprocessing Checks (Validated on BOTH Services)
- [x] **06. No Face**: Confirm rejection of images containing no human face on both services.
- [x] **07. Multiple Faces**: Verify rejection of images containing more than one face on both services.
- [x] **08. Blur Check**: Verify rejection of blurred pictures (Laplacian variance < 50.0) on both services.
- [x] **09. Brightness Validation**: Verify rejection of underexposed and overexposed photos on both services.
- [x] **10. Invalid Image**: Verify rejection of unsupported file types and oversize payloads on both services.

## 3. Database & FAISS Mechanics (Cross-Service Integrations)
- [x] **11. API Validation**: Malformed schema input constraints (email/date structures) on both services.
- [x] **12. Error Responses**: Unified JSON error envelope configurations checked on both services.
- [x] **13. Database Testing**: Transaction safety and foreign key cascading checks.
- [x] **14. FAISS Search**: Correctness of FAISS nearest neighbor Inner Product calculation on Identification.
- [x] **15. FAISS Index Rebuild**: On-demand indexing from PostgreSQL database records on Identification.

## 4. Observability & Performance
- [x] **16. Health API**: Heartbeat diagnostics endpoints validated on both services.
- [x] **17. Metrics API**: Observability and request metrics tracking checked on Identification.
- [x] **18. Accuracy Evaluation**: Evaluated match accuracy checks.
- [x] **19. Rank-1 Accuracy**: Verify true match is the top result on Identification.
- [x] **20. FAR (False Acceptance Rate)**: FAR remains at 0.0% using default threshold boundaries on Identification.
- [x] **21. FRR (False Rejection Rate)**: FRR remains low (<5.0%) on Identification.
- [x] **22. Latency Breakdown**: Confirm processing stages are under 200ms budget limit.

## 5. Load, Stress, and Resilience Tests (Both Services Audited)
- [x] **23. Load Testing**: k6 load profile verified (10 to 500 VUs) on Identification.
- [x] **24. Stress Testing**: Locust breaking point limits determined (350 Users) on Identification.
- [x] **25. Memory Usage Profile**: Zero memory leaks verified over 1000 sequential runs on both services.
- [x] **26. CPU Usage Profile**: Profile processor saturation thresholds on both services.
- [x] **27. Server Restart**: Warm preloader initialization routines tested on both services.
- [x] **28. Database Restart**: Automatic connection pool reconnections validated on both services.
- [x] **29. Logging Verification**: Check formats in enrollment_service.log and face_identification.log.

## 6. API Documentation & Integration Checks
- [x] **30. Swagger Documentation**: Verify Swagger schema definitions on both services.
- [x] **31. Postman Collection**: Verify exported Postman collections targeting both services.
- [x] **32. Security Checks**: CORS checking and SQL injection parameterizations on both services.
- [x] **33. Performance Benchmarks**: Confirm system throughput.
- [x] **34. Endurance (Soak) Testing**: 24-hour run check on Identification.
- [x] **35. Production Readiness**: Audited configurations check on both services.