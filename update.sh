#!/bin/bash
# ==============================================================================
# JAINBIZ - 1-CLICK INSTANT UPDATE SCRIPT FOR HOSTINGER VPS
# Pulls latest GitHub code, installs any new packages & restarts the 24/7 service
# ==============================================================================

set -e

# Auto-locate project directory if executed from outside
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "🔄 UPDATING JAINBIZ IN $SCRIPT_DIR FROM GITHUB..."
echo "=================================================================="

# 1. Clean any stuck chromium background processes
pkill -f chromium 2>/dev/null || true

# 2. Stash any runtime database/config changes so git pull never conflicts
git stash 2>/dev/null || true

# 3. Pull latest code from GitHub
git pull origin main

# 4. Activate virtual environment and update packages
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt --quiet
fi

# 5. Restart the background 24/7 service
sudo systemctl restart jainbiz.service

echo "=================================================================="
echo "✅ UPDATE COMPLETE! YOUR VPS IS NOW RUNNING THE LATEST CODE!"
echo "📌 Check live status: sudo systemctl status jainbiz.service"
echo "=================================================================="
