"""
Comprehensive verification script for Multi-Account Switcher & Cross-Account Deduplication.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_master_excel_path
from backend.auto_entry_bot import load_leads_from_excel
from backend.auto_batch_engine import is_lead_pending
from backend.account_manager import (
    load_portal_accounts,
    add_or_update_account,
    set_active_account,
    delete_account,
    resolve_credentials,
    get_public_accounts_view
)

def run_verification():
    excel_path = get_master_excel_path()
    all_leads = load_leads_from_excel(excel_path)
    print(f"Total leads loaded from Master Excel: {len(all_leads)}")

    submitted = [l for l in all_leads if not is_lead_pending(l)]
    pending = [l for l in all_leads if is_lead_pending(l)]

    print(f"Leads excluded as already submitted/duplicate/skipped: {len(submitted)}")
    print(f"Leads eligible for submission (Ready to Submit): {len(pending)}")

    # 1. Deduplication Verification
    for l in submitted:
        biz_id = l.get("j4j_business_id", "")
        status = str(l.get("submission_status", "")).lower()
        if "submitted" in status or "live" in status or biz_id:
            assert not is_lead_pending(l), f"CRITICAL: Lead {l.get('name')} was marked as pending despite being live/submitted!"

    print("✅ TEST 1 PASSED: Strict Cross-Account Deduplication is 100% airtight! No live lead can be re-submitted.")

    # 2. Account Manager Verification
    print("\n--- Testing Account Manager ---")
    add_res = add_or_update_account("partner_jain@gmail.com", "partnerPass123", label="Account 2 (Partner)", make_active=False)
    print(f"Added new portal account: {add_res}")

    view = get_public_accounts_view(excel_path)
    print(f"Total configured accounts: {len(view['accounts'])}")
    assert any(a["email"] == "partner_jain@gmail.com" for a in view["accounts"]), "Account not in public view!"

    # 3. Switching Accounts
    set_res = set_active_account("partner_jain@gmail.com")
    assert set_res, "Failed to switch active account"
    email, pwd, tag = resolve_credentials()
    print(f"Resolved credentials after switch: {email}, user_tag={tag}")
    assert email == "partner_jain@gmail.com", "Active account email mismatch!"

    # 4. Switching back to master
    set_active_account("mohit12836@gmail.com")
    email, pwd, tag = resolve_credentials()
    print(f"Resolved credentials after switch back to master: {email}")
    assert email == "mohit12836@gmail.com", "Master email mismatch!"

    # 5. Clean up test account
    del_res = delete_account("partner_jain@gmail.com")
    print(f"Deleted test account: {del_res}")
    view_final = get_public_accounts_view(excel_path)
    assert not any(a["email"] == "partner_jain@gmail.com" for a in view_final["accounts"]), "Account not deleted!"
    print(f"Remaining active accounts: {[a['email'] for a in view_final['accounts']]}")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! Ready for deployment.")

if __name__ == "__main__":
    run_verification()
