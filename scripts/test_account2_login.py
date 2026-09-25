"""
Test login with Account 2 on jainforjain.com.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from backend.auto_entry_bot import login_to_portal
from backend.system_guard import CHROMIUM_TURBO_ARGS

async def test_account2():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        page = await browser.new_page()
        try:
            print("Attempting login to jainforjain.com with mohit12836+1@gmail.com...")
            res = await login_to_portal(page, "mohit12836+1@gmail.com", "12345678")
            print("LOGIN_RESULT:", res)
            print("PAGE_URL:", page.url)
            if "/member/login" not in page.url:
                print("SUCCESS: Logged in to member dashboard!")
            else:
                print("FAILED: Still on login page.")
        finally:
            await browser.close()

async def test_zero_login():
    import time
    from backend.account_manager import get_session_file_path
    from backend.auto_entry_bot import CREATE_URL
    session_file = get_session_file_path("mohit12836+1@gmail.com")
    print(f"\n--- Testing Zero-Login with session cache: {session_file} ---")
    start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        ctx = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await ctx.new_page()
        try:
            await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=20000)
            dur = round(time.time() - start, 2)
            print(f"Time to load create form directly: {dur}s")
            print("Current page URL:", page.url)
            if "/business-listings/create" in page.url:
                print("⚡ SUCCESS: Direct Zero-Login Confirmed! Landed directly on Create form in zero seconds flat!")
            else:
                print("Notice: Redirected to", page.url)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_account2())
    asyncio.run(test_zero_login())
