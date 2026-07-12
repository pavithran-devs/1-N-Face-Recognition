#!/usr/bin/env bash
# scripts/curl_verification.sh - Automated curl verification for Face Recognition APIs
set -e

echo "========================================================================"
echo "                 Curl-Based API Integration Verification                "
echo "========================================================================"

ENROLL_URL="http://localhost:8000/api/v1"
IDENT_URL="http://localhost:8001"

# 1. Health Verification
echo -e "\n[*] 1. Verifying Health Endpoints..."
curl -s -f "${ENROLL_URL}/health" | grep -q "ok" && echo "[+] Enrollment Service health OK."
curl -s -f "${IDENT_URL}/health" | grep -q "healthy" && echo "[+] Face Identification Service health OK."

# 2. Candidate Creation (Metadata only)
echo -e "\n[*] 2. Registering Candidate via curl..."
CAND_RESP=$(curl -s -X POST "${ENROLL_URL}/candidates/" \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": "CURL_TEST_001", "name": "Bruce Wayne", "email": "bruce.wayne@gotham.com", "dob": "1980-02-19"}')
echo "[+] Response: ${CAND_RESP}"
CAND_UUID=$(echo "${CAND_RESP}" | python3 -c "import json, sys; print(json.load(sys.stdin).get('id', ''))")

if [ -n "${CAND_UUID}" ]; then
  echo "[+] Registered Candidate UUID: ${CAND_UUID}"

  # 3. Get Candidate
  echo -e "\n[*] 3. Fetching Candidate details..."
  GET_RESP=$(curl -s "${ENROLL_URL}/candidates/${CAND_UUID}")
  echo "[+] Response: ${GET_RESP}"

  # 4. Search Candidate
  echo -e "\n[*] 4. Searching for Candidate by ID..."
  SRCH_RESP=$(curl -s "${ENROLL_URL}/candidates/?search=CURL_TEST_001&search_field=candidate_id")
  echo "[+] Response: ${SRCH_RESP}"

  # 5. Clean up Candidate
  echo -e "\n[*] 5. Cleaning up Candidate entries..."
  curl -s -X DELETE "${ENROLL_URL}/candidates/${CAND_UUID}" && echo "[+] Candidate deleted successfully."
else
  echo "[-] Failed to parse candidate UUID."
  exit 1
fi

# 6. FAISS index status
echo -e "\n[*] 6. Checking FAISS index status..."
FAISS_STATUS=$(curl -s "${IDENT_URL}/health" | python3 -c "import json, sys; print(json.load(sys.stdin).get('faiss_index', ''))")
echo "[+] FAISS index metadata: ${FAISS_STATUS}"

# 7. Metrics endpoint check
echo -e "\n[*] 7. Fetching performance telemetry metrics..."
METRICS_RESP=$(curl -s "${IDENT_URL}/metrics")
echo "[+] Metrics response: ${METRICS_RESP}"

echo -e "\n========================================================================"
echo "                   Curl Verification Completed                          "
echo "========================================================================"
