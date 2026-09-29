import asyncio
import os
import sys
import re
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path, get_active_account_credentials
from backend.system_guard import CHROMIUM_TURBO_ARGS

async def get_listings_for_account(email, password):
    session_file = get_session_file_path(email)
    print(f"\n=======================================================")
    print(f" Checking Member Listings for: {email}")
    print(f"=======================================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        ctx_kwargs = {"viewport": {"width": 1400, "height": 950}}
        if os.path.exists(session_file):
            ctx_kwargs["storage_state"] = session_file
        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()
        
        await page.goto("https://jainforjain.com/member/business-listings", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)
        
        if "/member/login" in page.url:
            print("Logging in...")
            from backend.auto_entry_bot import login_to_portal
            await login_to_portal(page, email, password)
            await page.goto("https://jainforjain.com/member/business-listings", wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(3000)
            
        print("Page URL:", page.url)
        
        # Extract rows from Filament table
        listings = await page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('table tbody tr'));
            return rows.map(tr => {
                const text = tr.innerText;
                const links = Array.from(tr.querySelectorAll('a')).map(a => a.href);
                const editLink = links.find(h => h.includes('/edit')) || '';
                return { text: text.replace(/\\s+/g, ' ').trim(), editLink };
            });
        }''')
        
        print(f"Found {len(listings)} listings on first page:")
        for idx, item in enumerate(listings[:15], 1):
            edit_id = ""
            if item["editLink"]:
                m = re.search(r'/business-listings/(\d+)/edit', item["editLink"])
                if m: edit_id = m.group(1)
            print(f"  [{idx}] ID: {edit_id} | Edit URL: {item['editLink']} | Summary: {item['text'][:80]}")
            
        await browser.close()
        return listings

async def main():
    # Check Account 2 first
    await get_listings_for_account("mohit12836+1@gmail.com", "12345678")
    # Check Account 1
    await get_listings_for_account("mohit12836@gmail.com", "223034000")

if __name__ == "__main__":
    asyncio.run(main())
