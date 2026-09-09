"""
Global Configuration and Path Resolver for JainBiz Lead Miner.
Supports both Local Windows environment and 24/7 Cloud Docker / Linux deployments.
"""

import os

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
        
    # Default fallback
    if os.path.exists(data_excel):
        return data_excel
    if os.path.exists(desktop_dir):
        return os.path.join(desktop_dir, "Jain_Leads_Verified_Photos_HD.xlsx")
    return data_excel
