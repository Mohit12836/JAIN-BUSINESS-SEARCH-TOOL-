import asyncio
import os
import sys
import shutil
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS

async def verify():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={"width": 1400, "height": 1200})
        logged = await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        print(f"Logged in: {logged}")
        await page.goto("https://jainforjain.com/member/business-listings/267/edit", wait_until="networkidle")
        
        # Click Images tab
        btn = page.locator('button', has_text="Images")
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_timeout(2500)
            
        shot_path = os.path.join(os.path.expanduser("~"), "Desktop", "proof_listing_267_images.png")
        await page.screenshot(path=shot_path, full_page=True)
        print(f"✓ Screenshot saved to: {shot_path}")
        
        dst = os.path.join(r"C:\Users\hp\.gemini\antigravity\brain\b0c352c9-a8dd-444e-93c6-f049650ebc00", "proof_listing_267_images.png")
        shutil.copyfile(shot_path, dst)
        print(f"✓ Copied to artifacts: {dst}")
        
        await b.close()

if __name__ == "__main__":
    asyncio.run(verify())
