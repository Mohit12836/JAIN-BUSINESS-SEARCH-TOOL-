import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path, get_active_account_credentials
from backend.system_guard import CHROMIUM_TURBO_ARGS
from backend.auto_entry_bot import fill_listing_form, CREATE_URL

async def test_unique_submission():
    email, password, acc_id = get_active_account_credentials()
    session_file = get_session_file_path(email)
    print(f"Testing with Account: {email}")

    # A mock lead with a guaranteed unique business name
    import random
    unique_num = random.randint(1000, 9999)
    test_lead = {
        "sl": 9999,
        "row_idx": 9999,
        "name": f"Shree Parasnath Traders {unique_num}",
        "category": "Fashion & Beauty",
        "phone": "9826012345",
        "owner": "Parasnath Jain",
        "city": "Indore",
        "state": "Madhya Pradesh",
        "district": "Indore",
        "address": "Sarafa Bazar, Indore, Madhya Pradesh",
        "pincode": "452002",
        "description": "Authentic Jain business in Sarafa Bazar Indore.",
        "services": "Retail, Wholesale"
    }
    print(f"Submitting unique test lead: '{test_lead['name']}'...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        context = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        page.on("console", lambda msg: print(f"[Console] {msg.type}: {msg.text}"))
        async def on_resp(r):
            if r.status >= 400:
                print(f"[HTTP {r.status}] {r.url}")
                try:
                    text = await r.text()
                    print(f"  Error body snippet: {text[:200]}")
                except Exception:
                    pass
        page.on("response", on_resp)

        await page.goto(CREATE_URL, wait_until="domcontentloaded")
        print("Page URL:", page.url)

        res = await fill_listing_form(page, test_lead, dry_run=False)
        print("\n=== FINAL TEST SUBMISSION RESULT ===")
        print(json.dumps(res, indent=2))

        await page.screenshot(path="test_unique_result.png", full_page=True)
        print("Saved screenshot to test_unique_result.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_unique_submission())
