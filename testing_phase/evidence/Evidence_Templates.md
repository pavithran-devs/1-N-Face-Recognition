# QA Verification Evidence Templates

This document contains worksheets for capturing evidence during QA testing runs. Use these tables to record manual verification screenshots and output logs.

## 1. Biometric Pipeline Quality Check Rejections
| Test ID | Rejection Code | Target Cause | Captured Console Log Excerpt | Attached Evidence Filename |
|---------|----------------|--------------|-------------------------------|-----------------------------|
| TC-NOF-REG-01 | `no_face` | Solid gray image | `[WARN] Face quality validation failed: no_face` | `evidence/TC-NOF-REG-01_screenshot.png` |
| TC-NOF-IDENT-01 | `no_face` | Solid gray image | `[WARN] Face quality validation failed: no_face` | `evidence/TC-NOF-IDENT-01_screenshot.png` |
| TC-MUL-REG-01 | `multiple_faces` | Group photo | `[WARN] Face quality validation failed: multiple_faces` | `evidence/TC-MUL-REG-01_screenshot.png` |
| TC-MUL-IDENT-01 | `multiple_faces` | Group photo | `[WARN] Face quality validation failed: multiple_faces` | `evidence/TC-MUL-IDENT-01_screenshot.png` |
| TC-BLR-REG-01 | `blurry` | Blur image (variance=12.45) | `[WARN] Quality check failed: blurry (variance: 12.45)` | `evidence/TC-BLR-REG-01_screenshot.png` |
| TC-BLR-IDENT-01 | `blurry` | Blur image (variance=12.45) | `[WARN] Quality check failed: blurry (variance: 12.45)` | `evidence/TC-BLR-IDENT-01_screenshot.png` |
| TC-EXP-REG-01 | `too_dark` | Dark image (mean=15.2) | `[WARN] Quality check failed: too_dark (mean: 15.2)` | `evidence/TC-EXP-REG-01_screenshot.png` |
| TC-EXP-IDENT-01 | `too_dark` | Dark image (mean=15.2) | `[WARN] Quality check failed: too_dark (mean: 15.2)` | `evidence/TC-EXP-IDENT-01_screenshot.png` |

---

## 2. Platform Resiliency Check Evidence
| Event Cause | Trigger Command | Verification Metric | Captured Status Payload | Recovery Status |
|-------------|-----------------|---------------------|-------------------------|-----------------|
| DB Restart | `sudo systemctl restart postgresql` | API /health check | `{"status": "healthy", "database": "connected"}` | Recovered in 3 seconds |
| Service Restart | `uvicorn app.main:app --reload` | Warm launch time | `Loaded model pack buffalo_l successfully.` | warm launch in 4.5 seconds |