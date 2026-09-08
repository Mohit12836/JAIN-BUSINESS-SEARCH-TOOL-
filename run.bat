@echo off
title JainBiz Miner - Zero API Lead Extractor
color 0B

echo ================================================================
echo          JAINBIZ MINER: ZERO-API PAN-INDIA LEAD MINER
echo ================================================================
echo.
echo [1/3] Checking environment and dependencies...
python -m pip install -q fastapi uvicorn openpyxl playwright beautifulsoup4

echo [2/3] Starting backend server on http://127.0.0.1:8000 ...
start "" http://127.0.0.1:8000

echo [3/3] Launching application...
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
pause
