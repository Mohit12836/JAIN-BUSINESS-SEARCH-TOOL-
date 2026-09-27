import os
import sys
import asyncio
import json
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

async def run_inspection():
    email, password, acc_id = get_active_account_credentials()
    session_file = get_session_file_path(email)
    print(f"=== DEEP INSPECTION OF FORM SUBMISSION FOR ACCOUNT 2 ===")
    print(f"Account: {email} (ID: {acc_id})")

    excel_path = get_master_excel_path()
    leads = load_leads_from_excel(excel_path)
    
    # Pick a fresh lead: Row 382 (Jain Gift)
    target_row = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 382
    matches = [l for l in leads if l.get("row_idx") == target_row]
    test_lead = matches[0] if matches else leads[0]
    
    print(f"Target Lead [Row {test_lead.get('row_idx')}]: {test_lead.get('name')}")
    print(f"Category: {test_lead.get('category')} | Phone: {test_lead.get('phone')}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        ctx_kwargs = {"viewport": {"width": 1400, "height": 950}}
        if os.path.exists(session_file):
            ctx_kwargs["storage_state"] = session_file
            
        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()

        # Capture console & network responses
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        
        async def on_response(response):
            if "livewire" in response.url or response.status >= 400:
                try:
                    body = await response.text()
                    print(f"\n[HTTP {response.status}] {response.url}")
                    if response.status >= 400 or "error" in body.lower() or "exception" in body.lower():
                        print(f"  Response Body snippet: {body[:300]}")
                except Exception:
                    pass
        page.on("response", on_response)

        try:
            print("\n1. Navigating to Create Listing Form...")
            await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=30000)
            if "/member/login" in page.url:
                print("Fresh login needed...")
                await login_to_portal(page, email, password)
                await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=30000)

            print("Current URL before fill:", page.url)

            # Run fill_listing_form
            res = await fill_listing_form(page, test_lead, dry_run=False)
            print("\n=== Result from fill_listing_form ===")
            print(json.dumps(res, indent=2))

            # Inspect what is currently on the DOM
            print("\n=== Current DOM Errors / Notifications ===")
            dom_info = await page.evaluate('''() => {
                const notifications = Array.from(document.querySelectorAll('.fi-no-notification, .fi-notification, [role="alert"]')).map(el => el.innerText.trim());
                const fieldErrors = Array.from(document.querySelectorAll('.fi-fo-field-wrp-error-message, .text-danger-600, .fi-error')).map(el => el.innerText.trim());
                const allButtons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(t => t.length > 0);
                return {
                    url: window.location.href,
                    notifications,
                    fieldErrors,
                    allButtons: allButtons.slice(0, 10)
                };
            }''')
            print(json.dumps(dom_info, indent=2))

            # Screenshot after submit attempt
            post_screen = "post_submit_inspection.png"
            await page.screenshot(path=post_screen, full_page=True)
            print(f"Saved full-page screenshot to {post_screen}")

        except Exception as e:
            print(f"Exception during inspection: {e}")
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_inspection())
