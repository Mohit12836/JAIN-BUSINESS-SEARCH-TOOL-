#!/bin/bash
# ==============================================================================
# JAINBIZ - 1-CLICK INSTANT UPDATE SCRIPT FOR HOSTINGER VPS
# Pulls latest GitHub code, installs any new packages & restarts the 24/7 service
# ==============================================================================

set -e

echo "=================================================================="
echo "🔄 UPDATING JAINBIZ TO LATEST VERSION FROM GITHUB..."
echo "=================================================================="

# 1. Pull latest code from GitHub
git pull origin main

# 2. Activate virtual environment and update packages
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
fi

# 3. Restart the background 24/7 service
sudo systemctl restart jainbiz.service

echo "=================================================================="
echo "✅ UPDATE COMPLETE! YOUR VPS IS NOW RUNNING THE LATEST CODE!"
echo "📌 Check live status: sudo systemctl status jainbiz.service"
echo "=================================================================="
