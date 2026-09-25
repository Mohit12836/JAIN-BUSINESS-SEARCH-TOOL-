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

if __name__ == "__main__":
    asyncio.run(test_account2())
