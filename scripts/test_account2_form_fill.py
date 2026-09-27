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
    load_leads_from_excel
)
from backend.system_guard import CHROMIUM_TURBO_ARGS
from backend.config import get_master_excel_path
from backend.auto_batch_engine import is_lead_pending

async def run_test():
    email, password, acc_id = get_active_account_credentials()
    session_file = get_session_file_path(email)
    print(f"Testing with Account: {email} (ID: {acc_id})")
    print(f"Session file: {session_file} (Exists: {os.path.exists(session_file)})")

    # Load 1 pending lead
    excel_path = get_master_excel_path()
    leads = load_leads_from_excel(excel_path)
    pending = [l for l in leads if is_lead_pending(l)]
    if not pending:
        print("No pending leads found!")
        return
    test_lead = pending[0]
    print(f"\nTarget Lead: Row {test_lead.get('row_idx')} - {test_lead.get('name')}")
    print(f"Category: {test_lead.get('category')} | City: {test_lead.get('city')} | Phone: {test_lead.get('phone')}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        
        ctx_kwargs = {"viewport": {"width": 1400, "height": 950}}
        if os.path.exists(session_file):
            ctx_kwargs["storage_state"] = session_file
            
        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()

        try:
            print(f"\n1. Navigating to CREATE_URL: {CREATE_URL}")
            resp = await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=30000)
            print(f"HTTP Status: {resp.status if resp else 'None'}")
            print(f"Current URL: {page.url}")
            
            # Check if redirected to login
            if "/member/login" in page.url:
                print("Redirected to login. Attempting fresh login...")
                logged = await login_to_portal(page, email, password)
                print("Login result:", logged)
                await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=30000)
                print(f"URL after login: {page.url}")

            # Check page content
            content = await page.content()
            page_title = await page.title()
            print(f"Page Title: {page_title}")

            # Check for any quota or membership alerts
            for keyword in ["Listing Limit", "Allowed", "package", "plan", "quota", "Subscription", "Remaining", "upgrade", "0 Left"]:
                if keyword.lower() in content.lower():
                    print(f"⚠️ KEYWORD FOUND: '{keyword}' in page content!")

            # Take screenshot of whatever is currently on the screen
            screenshot_path = "account2_create_page.png"
            await page.screenshot(path=screenshot_path)
            print(f"Saved screenshot to {screenshot_path}")

            # Now try fill_listing_form with dry_run=True (fills tab 1,2,3,4 without clicking final submit)
            print("\n2. Executing fill_listing_form (dry_run=True)...")
            res = await fill_listing_form(page, test_lead, dry_run=True)
            print("Form Fill Result:", res)

        except Exception as e:
            print(f"\n❌ EXCEPTION during form fill test: {e}")
            traceback.print_exc()
            try:
                err_screenshot = "account2_error.png"
                await page.screenshot(path=err_screenshot)
                print(f"Saved error screenshot to {err_screenshot}")
            except Exception:
                pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
