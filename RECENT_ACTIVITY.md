# Documentation: Summary of Recent Technical Activities

This document details the recent dataset cleanups, startup optimizations, cross-validation testing, duplicate identification, and workspace structural reorganizations carried out in the **1:N Face Recognition System**.

---

## 1. Database & Dataset Cleanups
*   **Script**: [Untitled-1.sh](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/Untitled-1.sh)
*   **Methodology**: Scans the LFW deep-funneled dataset directories (`enrollment_service/lfw-deepfunneled/`) and deletes directories that have **at most 1 image file**.
*   **Outcome**: Removed single-image folders to clean up database noise and focus multi-sample verification runs on actual database candidate pools.

---

## 2. FAISS Startup Rebuild Optimizations
*   **Modified Files**:
    *   [events.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/app/core/events.py): Bypasses the startup database-sync and FAISS-rebuild from PostgreSQL when running test suites. It detects the active test suite by checking the `TESTING` environment variable or if `pytest` is loaded in the python runtime environment.
    *   [conftest.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/tests/conftest.py): Set `os.environ["TESTING"] = "True"` automatically during test initialization, resolving a runtime lag and dependency issue during test suites.
*   **Outcome**: Dramatically reduced startup delay and configuration dependency issues during automated test suite runs.

---

## 3. Directory Testing (Mayilmurugan Dataset)
*   **Testing Script**: [test_mayilmurugan_directory.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/test_mayilmurugan_directory.py)
*   **Methodology**: Run face recognition on all **70 images** in the `Mayilmurugan/` folder. The standard similarity threshold constraint (`0.65`) was bypassed to record raw top-1 cosine match scores.
*   **Results Summary**:
    *   **Total Images Processed**: 70
    *   **Pipeline Quality Failures**: 14 (12 due to blur quality constraints—Laplacian variance below `50.0`; 2 due to multiple face detections in group photos).
    *   **Detections Succeeded**: 56 (all 56 images correctly resolved to candidate `Mayil` with ID `4567`).
    *   **Similarity Scores**:
        *   **Average Score**: `0.6943`
        *   **Maximum Score**: `0.8426`
        *   **Minimum Score**: `0.3382` (correctly matched but would have been flagged as "Unknown" under standard constraints).
    *   **Output CSV**: [mayilmurugan_test_results.csv](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/mayilmurugan_test_results.csv)
    *   **Detailed Log**: [face_testing.md](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/face_testing.md)

---

## 4. One-vs-Every Cosine Similarity Verification (Guru Krishnan)
*   **Testing Script**: [test_one_vs_every.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/test_one_vs_every.py)
*   **Methodology**: Extracted the 512-d ArcFace embedding from the updated query image `guru.jpeg` and computed its cosine similarity against all 393 enrolled candidates.
*   **Results Summary**:
    *   **Target Match**: Successfully matched the target candidate **Guru** (ID: `0017`) at Rank 1 with a similarity score of **0.6683** (passing the default `0.65` threshold boundary).
    *   **Separability Margin**: The runner-up match was Antony Leung at **0.1456**, resulting in a robust security separation margin of **0.5227**.
    *   **Output CSV**: [guru_krishnan_vs_all_results.csv](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/guru_krishnan_vs_all_results.csv)

---

## 5. All-to-All Candidate Duplicate Detector
*   **Script**: [find_duplicates_all_to_all.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/find_duplicates_all_to_all.py)
*   **Methodology**: Extracts normalized ArcFace embeddings for all database candidate profiles and calculates the full cross-comparison cosine similarity matrix to detect exact duplicates and spelling/duplicate registration variants.
*   **Discovered Examples**:
    *   **Exact duplicates (Score: 1.00)**: `Chinoy` vs `Chinoy` (different emails/IDs), `Stanley_Tong` vs `Load Test Candidate 582274c8` (different emails/IDs).
    *   **Spelling/Duplicate registrations**: `Dicaprio` vs `Leonardo DiCaprio` (Score: `0.7923`), `Will smith` vs `Will Smith` (Score: `0.6540`), `Tom Cruse` vs `Tom Cruise` (Score: `0.5818`), `Pavithranraj AP` vs `Pavithranraj AP` (Score: `0.5797`).
    *   **Output CSV**: [all_to_all_duplicates.csv](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/all_to_all_duplicates.csv)

---

## 6. Directory Structure & Compliance Reorganization
*   **Action**: Created a structured [testing_phase](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/testing_phase/) directory.
*   **Reorganization**: Moved all 35 pre-deployment QA reports (`reports/`), Postman structure files (`postman/`), Locust stress-test plans (`stress-test/`), k6 load test plans (`load-test/`), template forms (`evidence/`), and compilation run scripts (`scripts/compile_master_pdf.py` etc.) into the new subfolder to keep the workspace root clean and standardized.
