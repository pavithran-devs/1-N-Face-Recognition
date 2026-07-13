# Face Recognition Testing Walkthrough (Mayilmurugan Directory)

This document summarizes the results of running face recognition on the `Mayilmurugan` directory, matching against the enrolled database candidates without applying similarity thresholding constraints.

## Task Overview
We ran a test script against the 70 face images in the directory `Mayilmurugan/`.
- **Target Candidate in DB**: Name: `Mayil`, ID: `4567`, UUID: `8ea8bc66-026c-433b-be60-24827e0a4181`.
- **Bypassed Match Threshold**: Recorded the raw top-1 match score regardless of whether it was above or below the configured `SIMILARITY_THRESHOLD` (0.65).
- **Result Log & CSV**: Created the similarity log and saved it to a CSV file.

---

## Testing Results Summary

| Metric | Value |
| :--- | :--- |
| **Total Images Processed** | 70 |
| **Detections Succeeded** | 56 |
| **Detections Failed (Quality Check/Read)** | 14 |
| **Correct Matches (to Mayil)** | 56 |
| **Incorrect Matches (to other candidates)** | 0 |
| **Unidentified Matches (no FAISS results)** | 0 |
| **Average Similarity Score (Correct Match)** | **0.6943** |
| **Minimum Similarity Score (Correct Match)** | **0.3382** (low confidence but still matched) |
| **Maximum Similarity Score (Correct Match)** | **0.8426** |

### Output Files Created
- **CSV Log**: [mayilmurugan_test_results.csv](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/mayilmurugan_test_results.csv)
- **Detailed Run Logs**: [task-77.log](file:///home/pavithranraj/.gemini/antigravity-ide/brain/08414b4a-341b-4183-b248-fcfbe198fecb/.system_generated/tasks/task-77.log)

---

## Detailed Observations

### 1. Quality Failures (14 images)
14 images failed the pipeline's composite quality checks and were logged as `Unidentified` / `Pipeline Quality Failure`:
- **Blurry Images**: 12 images failed because their Laplacian variance fell below the minimum quality threshold (`min=50.0`).
  - Example files: `photo_2026-07-13_12-27-06.jpg` (variance = 45.9), `photo_2026-07-13_12-27-31.jpg` (variance = 35.0).
- **Multiple Faces**: 2 images were flagged as having multiple faces detected (e.g. `photo_2026-07-13_12-27-22.jpg` had 3 faces; `photo_2026-07-13_12-26-23.jpg` had 2 faces).

### 2. High Similarity & Low Similarity Matches
- Most of the successful matches scored well above the `0.65` threshold (with a peak score of **0.8426** on `photo_2026-07-13_12-26-16.jpg`).
- Bypassing the similarity threshold allowed us to correctly identify the candidate even in low-scoring images, such as:
  - `photo_2026-07-13_12-27-27.jpg` (Score: **0.3382**)
  - `photo_2026-07-13_12-27-29.jpg` (Score: **0.3885**)
  - `photo_2026-07-13_12-25-35.jpg` (Score: **0.3885**)
  
  These would normally be rejected as "Unknown Candidate" due to the 0.65 threshold constraint, but the raw match correctly points to `Mayil`.

---

# Face Recognition Testing Walkthrough (One vs Every - Guru Krishnan)

This section summarizes the results of running face recognition on the updated query image of Guru Krishnan (`guru.jpeg`) and comparing it against every registered candidate in the database to calculate similarity scores.

## Task Overview
We ran a test script that:
1. Sourced the virtual environment and loaded the updated query image [guru.jpeg](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/one_vs_every/guru.jpeg).
2. Extracted the 512-d ArcFace embedding for Guru Krishnan.
3. Fetched all 393 candidate profiles and their registered face embeddings from PostgreSQL.
4. Calculated the cosine similarity (vector dot product of normalized embeddings) between Guru Krishnan's query embedding and the embedding of every single candidate in the database.
5. Generated a CSV report containing the similarity scores for all 393 candidates sorted in descending order.

---

## Top 10 Similarity Matches

| Rank | Candidate Name | Candidate ID | Email | Similarity Score | Match Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Guru** | **0017** | **guru@gmail.com** | **0.6683** | **Target Candidate (Correct Match)** |
| 2 | Antony Leung | Antony_Leung | antony_leung@example.com | 0.1456 | Non-Match |
| 3 | Dexter Jackson | Dexter_Jackson | dexter_jackson@example.com | 0.1354 | Non-Match |
| 4 | Daisy Fuentes | Daisy_Fuentes | daisy_fuentes@example.com | 0.1289 | Non-Match |
| 5 | Load Test Candidate 74d003f8 | LOAD_TEST_74d003f8 | load_74d003f8@example.com | 0.1230 | Non-Match |
| 6 | Load Test Candidate 19277f0b | LOAD_TEST_19277f0b | load_19277f0b@example.com | 0.1225 | Non-Match |
| 7 | Anders Ebbeson | Anders_Ebbeson | anders_ebbeson@example.com | 0.1204 | Non-Match |
| 8 | Annette Lu | Annette_Lu | annette_lu@example.com | 0.1125 | Non-Match |
| 9 | Load Test Candidate e4429400 | LOAD_TEST_e4429400 | load_e4429400@example.com | 0.1115 | Non-Match |
| 10 | Ai Sugiyama | Ai_Sugiyama | ai_sugiyama@example.com | 0.1110 | Non-Match |

### Key Observations
* **Correct Target Identification**: The query image `guru.jpeg` matched the enrolled profile for **Guru** (ID: `0017`) at Rank 1 with a similarity score of **0.6683**. This successfully exceeds the standard `0.65` system threshold.
* **Separability Margin**: The margin between the correct match (`0.6683`) and the highest false candidate (`0.1456` for Antony Leung) is **0.5227**. This indicates strong robustness against false matches in the 1:N database.

### Output Files Created
* **CSV Results**: [guru_krishnan_vs_all_results.csv](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/guru_krishnan_vs_all_results.csv)

---

## Clean-up
We created the temporary execution scripts in the `scripts/` directory:
- [test_mayilmurugan_directory.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/test_mayilmurugan_directory.py)
- [test_one_vs_every.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/test_one_vs_every.py)
- [check_candidates.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/check_candidates.py)
- [check_guru.py](file:///home/pavithranraj/Desktop/1:N%20Face%20recognition/face_identification/scripts/check_guru.py)


