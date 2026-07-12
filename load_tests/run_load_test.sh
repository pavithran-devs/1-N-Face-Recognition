#!/usr/bin/env bash
# run_load_test.sh - Automated Locust setup and execution script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "========================================================================"
echo "                  Face Recognition Load Testing Bootstrapper            "
echo "========================================================================"

# 1. Setup Virtual Environment for Load Tests
VENV_DIR="${VENV_PATH:-$HOME/.venvs/load_tests}"
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment in $VENV_DIR..."
    mkdir -p "$(dirname "$VENV_DIR")"
    python3 -m venv "$VENV_DIR"
fi

if [ ! -L "load_tests/.venv" ] && [ ! -d "load_tests/.venv" ]; then
    echo "[*] Creating symlink to venv..."
    ln -s "$VENV_DIR" load_tests/.venv
fi

echo "[*] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[*] Installing dependencies (Locust & Pillow)..."
pip install --upgrade pip
pip install locust pillow

# 2. Check if services are running, start them if not
ENROLL_RUNNING=true
IDENT_RUNNING=true

if ! curl -s -f http://localhost:8000/api/v1/health >/dev/null; then
    ENROLL_RUNNING=false
fi

if ! curl -s -f http://localhost:8001/health >/dev/null; then
    IDENT_RUNNING=false
fi

# Track PIDs of servers we start to stop them later
STARTED_ENROLL_PID=""
STARTED_IDENT_PID=""

if [ "$ENROLL_RUNNING" = false ]; then
    echo "[!] Enrollment Service (port 8000) is offline. Starting in background..."
    nohup bash enrollment_service/scripts/run_server.sh > enrollment_console.log 2>&1 &
    STARTED_ENROLL_PID=$!
fi

if [ "$IDENT_RUNNING" = false ]; then
    echo "[!] Face Identification Service (port 8001) is offline. Starting in background..."
    nohup bash face_identification/scripts/run_server.sh > face_console.log 2>&1 &
    STARTED_IDENT_PID=$!
fi

# Wait for services to load models
if [ "$ENROLL_RUNNING" = false ] || [ "$IDENT_RUNNING" = false ]; then
    echo "[*] Waiting 8 seconds for ML models to warm up and load..."
    sleep 8
fi

# Verify online status
echo "[*] Checking online health status..."
if curl -s -f http://localhost:8000/api/v1/health >/dev/null && curl -s -f http://localhost:8001/health >/dev/null; then
    echo "[+] Both services are ONLINE and ready."
else
    echo "[-] Error: One or both services failed to startup."
    exit 1
fi

# 3. Execute Locust Load Test
echo ""
echo "========================================================================"
echo "                   Starting Headless Locust Load Test                   "
echo "   Users: 10 | Spawn Rate: 2/sec | Duration: 60s | Concurrency Stress   "
echo "========================================================================"
echo ""

locust -f load_tests/locustfile.py \
    --headless \
    -u 10 \
    -r 2 \
    --run-time 60s \
    --csv=load_tests/report_locust \
    --only-summary

echo ""
echo "========================================================================"
echo "                          Load Test Completed                           "
echo "========================================================================"
echo ""

# 4. Print Summary Reports
if [ -f "load_tests/report_locust_stats.csv" ]; then
    echo "[*] Summary Stats (load_tests/report_locust_stats.csv):"
    echo "------------------------------------------------------------------------"
    column -s, -t < load_tests/report_locust_stats.csv
    echo "------------------------------------------------------------------------"
else
    echo "[!] CSV Stats file not found."
fi

# 5. Teardown Started Services
if [ -n "$STARTED_ENROLL_PID" ] || [ -n "$STARTED_IDENT_PID" ]; then
    echo "[*] Stopping local servers started by this script..."
    # Kill uvicorn/python started processes
    # We find processes using port 8000 and 8001 and kill them
    if [ -n "$STARTED_ENROLL_PID" ]; then
        echo "[*] Stopping enrollment service (Port 8000)..."
        fuser -k 8000/tcp || kill $STARTED_ENROLL_PID || true
    fi
    if [ -n "$STARTED_IDENT_PID" ]; then
        echo "[*] Stopping face identification service (Port 8001)..."
        fuser -k 8001/tcp || kill $STARTED_IDENT_PID || true
    fi
    echo "[+] Stopped background servers."
fi

echo "[+] Load testing script finished successfully."
