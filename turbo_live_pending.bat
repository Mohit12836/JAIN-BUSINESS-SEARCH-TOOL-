@echo off
title JainBiz - Turbo Live Submissions (All Pending Leads)
color 0A

echo ================================================================
echo     JAINBIZ MINER: TURBO LIVE SUBMITTER (ALL PENDING LEADS)
echo ================================================================
echo.
echo [1/2] Connecting to Master Excel ^& Preparing Turbo Workers...
echo.
python run_autopilot.py --mode live-pending --workers 3
echo.
echo ================================================================
echo [2/2] Process finished! All updated statuses synced to Google Sheet.
echo ================================================================
pause
