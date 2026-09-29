import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path
from backend.system_guard import CHROMIUM_TURBO_ARGS

async def inspect_account2_portal():
    session_file = get_session_file_path("mohit12836+1@gmail.com")
    print(f"Using session file: {session_file}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        context = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        # 1. Inspect /member dashboard
        print("\n=== 1. Inspecting /member ===")
        await page.goto("https://jainforjain.com/member", wait_until="domcontentloaded")
        print("URL:", page.url)
        content_member = await page.content()
        await page.screenshot(path="account2_member_dashboard.png", full_page=True)
        print("Saved screenshot to account2_member_dashboard.png")

        # Extract text snippets
        body_text = await page.locator("body").inner_text()
        lines = [line.strip() for line in body_text.split("\n") if line.strip()]
        print("Dashboard Text Summary:")
        for l in lines[:30]:
            print("  ", l)

        # 2. Inspect /member/business-listings
        print("\n=== 2. Inspecting /member/business-listings ===")
        await page.goto("https://jainforjain.com/member/business-listings", wait_until="domcontentloaded")
        print("URL:", page.url)
        await page.screenshot(path="account2_listings_list.png", full_page=True)
        print("Saved screenshot to account2_listings_list.png")
        body_text_list = await page.locator("body").inner_text()
        lines_list = [line.strip() for line in body_text_list.split("\n") if line.strip()]
        print("Listings Page Text Summary:")
        for l in lines_list[:30]:
            print("  ", l)

        # 3. Inspect /member/manage-subscription
        print("\n=== 3. Inspecting /member/manage-subscription ===")
        await page.goto("https://jainforjain.com/member/manage-subscription", wait_until="domcontentloaded")
        print("URL:", page.url)
        await page.screenshot(path="account2_subscription.png", full_page=True)
        print("Saved screenshot to account2_subscription.png")
        sub_text = await page.locator("body").inner_text()
        for l in [x.strip() for x in sub_text.split("\n") if x.strip()][:30]:
            print("  ", l)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_account2_portal())
