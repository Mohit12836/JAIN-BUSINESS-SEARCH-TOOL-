"""
Global Configuration and Path Resolver for JainBiz Lead Miner.
Supports both Local Windows environment and 24/7 Cloud Docker / Linux deployments.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

def get_master_excel_path() -> str:
    """
    Resolves the active path to Master Excel sheet.
    Prefers Windows Desktop if available; falls back to repo /data directory in Cloud / Docker.
    """
    # 1. Check Desktop (Windows local development)
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(desktop_dir):
        desktop_excel = os.path.join(desktop_dir, "Jain_Leads_Verified_Photos_HD.xlsx")
        if os.path.exists(desktop_excel) and os.path.getsize(desktop_excel) > 500:
            return desktop_excel

    # 2. Check repo /data directory (Cloud / Docker / Linux VPS)
    data_excel = os.path.join(DATA_DIR, "Jain_Leads_Verified_Photos_HD.xlsx")
    if os.path.exists(data_excel) and os.path.getsize(data_excel) > 500:
        return data_excel
        
    return data_excel

def is_cloud_environment() -> bool:
    """Detects whether running in Cloud Docker (Render/VPS) or Local PC (Windows)."""
    return os.environ.get("RENDER") is not None or os.environ.get("PORT") is not None or not sys.platform.startswith("win")


# ==============================================================================
# PERMANENT SYSTEM RULES: CONCURRENCY & PORTAL INTEGRITY
# ==============================================================================
MAX_SCRAPING_CONCURRENCY = 5        # Max parallel tabs for read-only data extraction
MAX_PORTAL_CONCURRENCY = 2          # Max parallel tabs for Livewire/Filament (prevents session collisions & photo deletion)
FILEPOND_TIMEOUT_SECONDS = 18       # Strict wait for file uploads to reach processing-complete
LIVEWIRE_REDIRECT_TIMEOUT_SECONDS = 12 # Timeout to capture live business ID upon creation

