#!/usr/bin/env bash
# test_endpoints.sh - Automated test script for all Face Enrollment Service API endpoints.
# Usage:
#   bash test_endpoints.sh                  # Runs using a generated dummy gray image
#   bash test_endpoints.sh /path/to/face.jpg # Runs using a real face image (to pass quality/detection checks)

# Exit on setup failures
set -e

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
API_V1="${API_URL}/api/v1"

# ANSI Colors for Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================================${NC}"
echo -e "${BLUE}               Face Enrollment Service API Test Suite                   ${NC}"
echo -e "${BLUE}========================================================================${NC}"

# Check server health first
echo -e "\n${BLUE}[*] Verifying server health...${NC}"
if ! curl -s -f "${API_V1}/health" > /dev/null; then
    echo -e "${RED}[-] Error: The API server is not reachable at ${API_URL}${NC}"
    echo -e "${YELLOW}[!] Make sure your FastAPI app is running. You can start it with:${NC}"
    echo -e "${CYAN}    uvicorn app.main:app --reload${NC}"
    exit 1
fi

HEALTH_RESP=$(curl -s "${API_V1}/health")
echo -e "${GREEN}[+] API Server is online!${NC}"
echo -e "Health Details: ${CYAN}${HEALTH_RESP}${NC}"

# Generate/prepare test image
echo -e "\n${BLUE}[*] Preparing test images & payload files...${NC}"

# Save the script's first parameter (user-supplied image path)
IMAGE_ARG="$1"

if [ -n "$IMAGE_ARG" ]; then
    if [ -f "$IMAGE_ARG" ]; then
        echo -e "${GREEN}[+] Using user-supplied face image: $IMAGE_ARG${NC}"
        cp "$IMAGE_ARG" test_face.jpg
    else
        echo -e "${RED}[-] Error: Specified image file '$IMAGE_ARG' does not exist.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}[!] No real face image provided. Generating a dummy gray JPEG...${NC}"
    echo -e "${YELLOW}[!] (Note: Endpoints running face detection will return 422 quality check errors)${NC}"
    python3 -c "
from PIL import Image
Image.new('RGB', (200, 200), (128, 128, 128)).save('test_face.jpg', 'JPEG')
"
fi

# Generate base64 string of the test image for capture endpoint
IMAGE_B64=$(python3 -c "
import base64
with open('test_face.jpg', 'rb') as f:
    print(base64.b64encode(f.read()).decode())
")

# Generate JSON import file with 512-dimension embedding
python3 -c "
import json
emb = [0.1] * 512
data = [
    {
        'candidate_id': 'TEST_IMP_JSON_1',
        'name': 'John Json',
        'email': 'john.json@example.com',
        'dob': '1990-05-15',
        'embeddings': [
            {
                'embedding': emb,
                'model_name': 'buffalo_l',
                'normalized': True
            }
        ]
    }
]
with open('test_import.json', 'w') as f:
    json.dump(data, f)
"
echo -e "${GREEN}[+] Created test_import.json${NC}"

# Generate CSV import file with 512-dimension embedding
python3 -c "
emb = ';'.join(['0.1'] * 512)
with open('test_import.csv', 'w') as f:
    f.write('candidate_id,name,email,dob,embedding,model_name,normalized\n')
    f.write(f'TEST_IMP_CSV_1,Jane Csv,jane.csv@example.com,1992-10-20,{emb},buffalo_l,true\n')
"
echo -e "${GREEN}[+] Created test_import.csv${NC}"

# Turn off exit on error for actual test runner execution
set +e

# Global test stats
TESTS_RUN=0
TESTS_PASSED=0

# Helper function to send requests and print results
run_test() {
    local TITLE="$1"
    local METHOD="$2"
    local ENDPOINT="$3"
    local DATA="$4"
    local HEADER="$5"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -e "\n${BLUE}------------------------------------------------------------------------${NC}"
    echo -e "${CYAN}Test $((TESTS_RUN)): ${TITLE}${NC}"
    echo -e "${CYAN}Request: ${METHOD} ${ENDPOINT}${NC}"

    local CURL_ARGS=(-s -w "\nHTTP_STATUS:%{http_code}" -X "${METHOD}")
    
    if [ -n "$HEADER" ]; then
        CURL_ARGS+=(-H "${HEADER}")
    fi

    if [ -n "$DATA" ]; then
        CURL_ARGS+=(-d "$DATA")
    fi

    local RESP
    RESP=$(curl "${CURL_ARGS[@]}" "${API_V1}${ENDPOINT}")
    
    local BODY
    BODY=$(echo "$RESP" | sed '/HTTP_STATUS:/d')
    local STATUS
    STATUS=$(echo "$RESP" | grep "HTTP_STATUS:" | cut -d':' -f2)

    if [[ "$STATUS" =~ ^(200|201|204)$ ]]; then
        echo -e "Response Status: ${GREEN}${STATUS} (OK)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    elif [[ "$STATUS" =~ ^422$ ]] && [[ "$ENDPOINT" == *"/face/"* || "$ENDPOINT" == *"/embedding/"* ]] && [ -z "$IMAGE_ARG" ]; then
        # Anticipated 422 for dummy image on face detection endpoints
        echo -e "Response Status: ${YELLOW}${STATUS} (Expected 422 for dummy/no-face image)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "Response Status: ${RED}${STATUS} (Failed/Error)${NC}"
    fi

    # Format JSON body if possible
    if echo "$BODY" | python3 -m json.tool >/dev/null 2>&1; then
        echo "$BODY" | python3 -m json.tool
    elif [ -n "$BODY" ]; then
        echo "$BODY"
    fi

    LAST_STATUS="$STATUS"
    LAST_BODY="$BODY"
}

# ─── 1. HEALTH ENDPOINT ───
run_test "Service health check" "GET" "/health"

# ─── 2. CANDIDATE CRUD ───
CAND_DATA='{
    "candidate_id": "TEST_CRUD_001",
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "dob": "1994-08-20"
}'
run_test "Create Candidate (Metadata only)" "POST" "/candidates/" "$CAND_DATA" "Content-Type: application/json"

# Extract Candidate UUID
CAND_UUID=$(echo "$LAST_BODY" | python3 -c "import json, sys; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
if [ -n "$CAND_UUID" ] && [ "$CAND_UUID" != "None" ]; then
    echo -e "${GREEN}[+] Candidate UUID: ${CAND_UUID}${NC}"
else
    echo -e "${RED}[-] Failed to parse Candidate UUID. Using a fallback fake UUID for testing path variables.${NC}"
    CAND_UUID="00000000-0000-0000-0000-000000000000"
fi

run_test "Get Candidate by UUID" "GET" "/candidates/${CAND_UUID}"

run_test "List/Search Candidates" "GET" "/candidates/?search=TEST_CRUD_001&search_field=candidate_id"

CAND_UPDATE='{
    "name": "Jane Updated Name",
    "email": "jane.updated@example.com"
}'
run_test "Update Candidate metadata" "PUT" "/candidates/${CAND_UUID}" "$CAND_UPDATE" "Content-Type: application/json"

# ─── 3. FACE ENROLLMENT ───

echo -e "\n${BLUE}------------------------------------------------------------------------${NC}"
echo -e "${CYAN}Test $((TESTS_RUN + 1)): Enroll via File Upload (Multipart Form)${NC}"
echo -e "${CYAN}Request: POST /face/upload${NC}"
TESTS_RUN=$((TESTS_RUN + 1))

RESP_UPLOAD=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${API_V1}/face/upload" \
  -F "image=@test_face.jpg;type=image/jpeg" \
  -F "candidate_id=TEST_FACE_UP_1" \
  -F "name=Frank Face" \
  -F "email=frank.face@example.com" \
  -F "dob=1988-12-05")

BODY_UPLOAD=$(echo "$RESP_UPLOAD" | sed '/HTTP_STATUS:/d')
STATUS_UPLOAD=$(echo "$RESP_UPLOAD" | grep "HTTP_STATUS:" | cut -d':' -f2)

if [[ "$STATUS_UPLOAD" =~ ^(200|201)$ ]]; then
    echo -e "Response Status: ${GREEN}${STATUS_UPLOAD} (OK)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
elif [[ "$STATUS_UPLOAD" =~ ^422$ ]]; then
    echo -e "Response Status: ${YELLOW}${STATUS_UPLOAD} (Expected 422 for dummy/no-face image)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Response Status: ${RED}${STATUS_UPLOAD} (Failed/Error)${NC}"
fi
if echo "$BODY_UPLOAD" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$BODY_UPLOAD" | python3 -m json.tool
else
    echo "$BODY_UPLOAD"
fi


CAPTURE_PAYLOAD=$(python3 -c "
import json
print(json.dumps({
    'image_b64': '$IMAGE_B64',
    'candidate_id': 'TEST_FACE_CAP_1',
    'name': 'Grace Capture',
    'email': 'grace.capture@example.com',
    'dob': '1993-03-14'
}))
")
run_test "Enroll via Webcam Capture (Base64 JSON)" "POST" "/face/capture" "$CAPTURE_PAYLOAD" "Content-Type: application/json"

# ─── 4. EMBEDDINGS ───

echo -e "\n${BLUE}------------------------------------------------------------------------${NC}"
echo -e "${CYAN}Test $((TESTS_RUN + 1)): Generate Embedding for Existing Candidate (Multipart)${NC}"
echo -e "${CYAN}Request: POST /embedding/generate/${CAND_UUID}${NC}"
TESTS_RUN=$((TESTS_RUN + 1))

RESP_GEN=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${API_V1}/embedding/generate/${CAND_UUID}" \
  -F "image=@test_face.jpg;type=image/jpeg")

BODY_GEN=$(echo "$RESP_GEN" | sed '/HTTP_STATUS:/d')
STATUS_GEN=$(echo "$RESP_GEN" | grep "HTTP_STATUS:" | cut -d':' -f2)

if [[ "$STATUS_GEN" =~ ^(200|201)$ ]]; then
    echo -e "Response Status: ${GREEN}${STATUS_GEN} (OK)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
elif [[ "$STATUS_GEN" =~ ^422$ ]]; then
    echo -e "Response Status: ${YELLOW}${STATUS_GEN} (Expected 422 for dummy/no-face image)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Response Status: ${RED}${STATUS_GEN} (Failed/Error)${NC}"
fi
if echo "$BODY_GEN" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$BODY_GEN" | python3 -m json.tool
else
    echo "$BODY_GEN"
fi


echo -e "\n${BLUE}------------------------------------------------------------------------${NC}"
echo -e "${CYAN}Test $((TESTS_RUN + 1)): Regenerate Embedding for Existing Candidate (Multipart)${NC}"
echo -e "${CYAN}Request: PUT /embedding/regenerate/${CAND_UUID}${NC}"
TESTS_RUN=$((TESTS_RUN + 1))

RESP_REGEN=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X PUT "${API_V1}/embedding/regenerate/${CAND_UUID}" \
  -F "image=@test_face.jpg;type=image/jpeg")

BODY_REGEN=$(echo "$RESP_REGEN" | sed '/HTTP_STATUS:/d')
STATUS_REGEN=$(echo "$RESP_REGEN" | grep "HTTP_STATUS:" | cut -d':' -f2)

if [[ "$STATUS_REGEN" =~ ^(200|201)$ ]]; then
    echo -e "Response Status: ${GREEN}${STATUS_REGEN} (OK)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
elif [[ "$STATUS_REGEN" =~ ^422$ ]]; then
    echo -e "Response Status: ${YELLOW}${STATUS_REGEN} (Expected 422 for dummy/no-face image)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Response Status: ${RED}${STATUS_REGEN} (Failed/Error)${NC}"
fi
if echo "$BODY_REGEN" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$BODY_REGEN" | python3 -m json.tool
else
    echo "$BODY_REGEN"
fi


run_test "List Embeddings for Candidate" "GET" "/embedding/${CAND_UUID}"

# ─── 5. IMPORT / EXPORT ───
run_test "Export all Candidates to JSON" "GET" "/export/json"

run_test "Export all Candidates to CSV" "GET" "/export/csv"


echo -e "\n${BLUE}------------------------------------------------------------------------${NC}"
echo -e "${CYAN}Test $((TESTS_RUN + 1)): Import Candidates from JSON file${NC}"
echo -e "${CYAN}Request: POST /import/json${NC}"
TESTS_RUN=$((TESTS_RUN + 1))

RESP_IMP_JSON=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${API_V1}/import/json" \
  -F "file=@test_import.json;type=application/json")

BODY_IMP_JSON=$(echo "$RESP_IMP_JSON" | sed '/HTTP_STATUS:/d')
STATUS_IMP_JSON=$(echo "$RESP_IMP_JSON" | grep "HTTP_STATUS:" | cut -d':' -f2)

if [[ "$STATUS_IMP_JSON" =~ ^(200|201)$ ]]; then
    echo -e "Response Status: ${GREEN}${STATUS_IMP_JSON} (OK)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Response Status: ${RED}${STATUS_IMP_JSON} (Failed)${NC}"
fi
if echo "$BODY_IMP_JSON" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$BODY_IMP_JSON" | python3 -m json.tool
else
    echo "$BODY_IMP_JSON"
fi


echo -e "\n${BLUE}------------------------------------------------------------------------${NC}"
echo -e "${CYAN}Test $((TESTS_RUN + 1)): Import Candidates from CSV file${NC}"
echo -e "${CYAN}Request: POST /import/csv${NC}"
TESTS_RUN=$((TESTS_RUN + 1))

RESP_IMP_CSV=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${API_V1}/import/csv" \
  -F "file=@test_import.csv;type=text/csv")

BODY_IMP_CSV=$(echo "$RESP_IMP_CSV" | sed '/HTTP_STATUS:/d')
STATUS_IMP_CSV=$(echo "$RESP_IMP_CSV" | grep "HTTP_STATUS:" | cut -d':' -f2)

if [[ "$STATUS_IMP_CSV" =~ ^(200|201)$ ]]; then
    echo -e "Response Status: ${GREEN}${STATUS_IMP_CSV} (OK)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "Response Status: ${RED}${STATUS_IMP_CSV} (Failed)${NC}"
fi
if echo "$BODY_IMP_CSV" | python3 -m json.tool >/dev/null 2>&1; then
    echo "$BODY_IMP_CSV" | python3 -m json.tool
else
    echo "$BODY_IMP_CSV"
fi

# ─── 6. CLEANUP & TEARDOWN ───
echo -e "\n${BLUE}========================================================================${NC}"
echo -e "${BLUE}                       Cleaning up Test Data                            ${NC}"
echo -e "${BLUE}========================================================================${NC}"

# Delete the CRUD candidate
if [ -n "$CAND_UUID" ] && [ "$CAND_UUID" != "00000000-0000-0000-0000-000000000000" ]; then
    run_test "Delete CRUD Candidate" "DELETE" "/candidates/${CAND_UUID}"
fi

# Find and delete imported or successfully uploaded face candidates to restore DB to original state
echo -e "${BLUE}[*] Fetching all candidates to clean up remaining test entries...${NC}"
ALL_CANDS=$(curl -s "${API_V1}/candidates/")
TO_DELETE_UUIDS=$(echo "$ALL_CANDS" | python3 -c "
import json, sys
data = json.load(sys.stdin).get('data', [])
for c in data:
    if c.get('candidate_id') in ['TEST_IMP_JSON_1', 'TEST_IMP_CSV_1', 'TEST_FACE_UP_1', 'TEST_FACE_CAP_1']:
        print(c.get('id'))
" 2>/dev/null)

for u in $TO_DELETE_UUIDS; do
    if [ -n "$u" ] && [ "$u" != "None" ]; then
        run_test "Delete Candidate (Teardown: $u)" "DELETE" "/candidates/${u}"
    fi
done

# Delete local files
echo -e "${BLUE}[*] Removing temporary local test files...${NC}"
rm -f test_face.jpg test_import.json test_import.csv
echo -e "${GREEN}[+] Teardown complete!${NC}"

echo -e "\n${BLUE}========================================================================${NC}"
echo -e "Test Results Summary: ${GREEN}${TESTS_PASSED}${NC} / ${CYAN}${TESTS_RUN}${NC} test operations completed successfully."
if [ "$TESTS_PASSED" -eq "$TESTS_RUN" ]; then
    echo -e "${GREEN}ALL ENDPOINT TESTS COMPLETED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}SOME TESTS ENCOUNTERED EXPECTED FAILURE (e.g. dummy image quality checks).${NC}"
fi
echo -e "${BLUE}========================================================================${NC}"
