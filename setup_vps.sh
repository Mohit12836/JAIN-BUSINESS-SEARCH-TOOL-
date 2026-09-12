#!/bin/bash
# ==============================================================================
# JAINBIZ LEAD MINER - 1-CLICK HOSTINGER VPS SETUP SCRIPT
# Runs 24/7 Autopilot, Headless Playwright Chromium, FastAPI & Auto-Restart on Boot
# ==============================================================================

set -e

echo "=================================================================="
echo "🚀 STARTING JAINBIZ 24/7 AUTOPILOT SETUP ON HOSTINGER VPS"
echo "=================================================================="

# 1. Update OS Packages and Install Python & Dependencies
echo "--> [1/5] Updating Linux packages and installing system libraries..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv git curl uvicorn

# 2. Setup Virtual Environment
APP_DIR="$(pwd)"
echo "--> [2/5] Setting up Python virtual environment in $APP_DIR..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Python Requirements
echo "--> [3/5] Installing Python libraries from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright Headless Chromium & Linux OS Libraries
echo "--> [4/5] Installing Playwright Chromium & system display dependencies..."
playwright install --with-deps chromium

# 5. Create Systemd Service for 24/7 Autopilot & Auto-Boot
SERVICE_FILE="/etc/systemd/system/jainbiz.service"
echo "--> [5/5] Creating Systemd service at $SERVICE_FILE..."

sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=JainBiz Lead Miner and Saturation Engine 24/7
After=network.target

[Service]
Type=simple
User=\$(whoami)
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python run_server.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=PORT=8000

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable jainbiz.service
sudo systemctl restart jainbiz.service

echo "=================================================================="
echo "🎉 100% SETUP COMPLETE! JAINBIZ IS NOW RUNNING 24/7 ON YOUR VPS!"
echo "=================================================================="
IP_ADDR=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
echo "🌐 Open your Live Dashboard at: http://$IP_ADDR:8000"
echo "📊 Health Check status: http://$IP_ADDR:8000/health"
echo "📌 Check service logs anytime with: sudo journalctl -u jainbiz.service -f"
echo "=================================================================="
