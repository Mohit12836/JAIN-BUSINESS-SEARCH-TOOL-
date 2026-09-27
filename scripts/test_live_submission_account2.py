import os
import sys
import asyncio
import traceback
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.account_manager import get_active_account, get_session_file_path, get_active_account_credentials
from backend.auto_entry_bot import (
    fill_listing_form,
    login_to_portal,
    CREATE_URL,
    load_leads_from_excel,
    update_excel_lead_status
)
from backend.system_guard import CHROMIUM_TURBO_ARGS
from backend.config import get_master_excel_path
from backend.auto_batch_engine import is_lead_pending

async def run_live_test():
    email, password, acc_id = get_active_account_credentials()
    session_file = get_session_file_path(email)
    print(f"=== TESTING 1 LIVE SUBMISSION FOR ACCOUNT 2 ===")
    print(f"Account: {email} (ID: {acc_id})")
    print(f"Session File: {session_file}")

    excel_path = get_master_excel_path()
    leads = load_leads_from_excel(excel_path)
    pending = [l for l in leads if is_lead_pending(l)]
    target_row = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    if target_row:
        matches = [l for l in leads if l.get("row_idx") == target_row]
        test_lead = matches[0] if matches else (pending[0] if pending else None)
    else:
        test_lead = pending[0] if pending else None

    if not test_lead:
        print("No pending or target lead found!")
        return
        
    row_idx = test_lead.get("row_idx", 2)
    print(f"\nTargeting Lead [Row {row_idx}]: {test_lead.get('name')}")
    print(f"Category: {test_lead.get('category')} | City: {test_lead.get('city')} | Phone: {test_lead.get('phone')}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        ctx_kwargs = {"viewport": {"width": 1400, "height": 950}}
        if os.path.exists(session_file):
            ctx_kwargs["storage_state"] = session_file
            
        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()

        try:
            print("\n1. Navigating to Create Listing Form...")
            await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=30000)
            
            if "/member/login" in page.url:
                print("Logging in fresh...")
                await login_to_portal(page, email, password)
                await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=30000)

            print("Current URL:", page.url)
            print("\n2. Executing LIVE Form Submission (dry_run=False)...")
            res = await fill_listing_form(page, test_lead, dry_run=False)
            print("\n=== SUBMISSION RESULT ===")
            print("Status:", res.get("status"))
            print("Business ID:", res.get("biz_id"))
            print("Profile URL:", res.get("profile_url"))
            print("Full Details:", res)

            biz_id = res.get("biz_id", "")
            profile_url = res.get("profile_url", "")
            status_txt = res.get("status", "")

            if res.get("duplicate") or "Already" in status_txt:
                update_excel_lead_status(excel_path, row_idx, "ALREADY_LISTED", profile_url, "Skipped - Already on Portal")
                print(f"Updated Excel Row {row_idx} as Skipped - Already on Portal")
            elif biz_id and biz_id.startswith("JFJ-") and status_txt == "submitted_success":
                status_label = f"Submitted - Live [{email}]"
                update_excel_lead_status(excel_path, row_idx, biz_id, profile_url, status_label)
                print(f"🎉 SUCCESS! Excel Row {row_idx} updated as: {status_label} with ID: {biz_id}")
            else:
                print(f"Notice: Form returned {res}")

        except Exception as e:
            print(f"\n❌ EXCEPTION during live submit: {e}")
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_live_test())
