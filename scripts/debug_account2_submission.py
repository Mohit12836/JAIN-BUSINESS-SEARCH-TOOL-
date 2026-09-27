import os
import sys
import json
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.account_manager import get_all_portal_accounts, get_active_portal_account, get_session_file_path, has_valid_session
from backend.config import get_master_excel_path
from backend.auto_batch_engine import is_lead_pending, load_leads_from_excel

def main():
    print("=== 1. PORTAL ACCOUNTS CHECK ===")
    accounts = get_all_portal_accounts()
    active_acc = get_active_portal_account()
    print("Active Account:", json.dumps(active_acc, indent=2))
    print(f"Total Accounts: {len(accounts)}")
    for a in accounts:
        has_sess = has_valid_session(a['email'])
        sess_path = get_session_file_path(a['email'])
        print(f" - {a['email']} (Active: {a.get('is_active')}, Session file exists: {has_sess} at {sess_path})")

    print("\n=== 2. EXCEL LEADS STATUS CHECK ===")
    excel_path = get_master_excel_path()
    print("Master Excel Path:", excel_path)
    if os.path.exists(excel_path):
        leads = load_leads_from_excel(excel_path)
        print(f"Total Leads loaded: {len(leads)}")
        pending = [l for l in leads if is_lead_pending(l)]
        submitted_1 = [l for l in leads if "mohit12836@gmail.com" in str(l.get("submission_status", ""))]
        submitted_2 = [l for l in leads if "mohit12836+1@gmail.com" in str(l.get("submission_status", ""))]
        submitted_other = [l for l in leads if "submitted" in str(l.get("submission_status", "")).lower() and not ("mohit12836@gmail.com" in str(l.get("submission_status", "")) or "mohit12836+1@gmail.com" in str(l.get("submission_status", "")))]
        skipped = [l for l in leads if "skipped" in str(l.get("submission_status", "")).lower()]
        
        print(f"Pending Leads (Ready to Submit): {len(pending)}")
        print(f"Submitted under Account 1 (mohit12836@gmail.com): {len(submitted_1)}")
        print(f"Submitted under Account 2 (mohit12836+1@gmail.com): {len(submitted_2)}")
        print(f"Submitted other: {len(submitted_other)}")
        print(f"Skipped Leads: {len(skipped)}")

        # Check skipped reasons
        skipped_reasons = {}
        for l in skipped:
            st = str(l.get("submission_status", ""))
            skipped_reasons[st] = skipped_reasons.get(st, 0) + 1
        print("Skipped reasons breakdown:")
        for r, c in skipped_reasons.items():
            print(f"   * {r}: {c}")

        if pending:
            print("\nFirst 3 pending leads:")
            for p in pending[:3]:
                print(f"   - Row {p.get('row_idx')}: {p.get('name')} | Status: {p.get('submission_status')}")
    else:
        print("Excel file not found!")

if __name__ == "__main__":
    main()
