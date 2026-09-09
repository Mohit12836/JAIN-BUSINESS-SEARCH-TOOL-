import os
import sys
import asyncio
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS

async def inspect_edit_page(listing_id=252):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 950})
        
        print("Logging in to portal...")
        await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        
        edit_url = f"https://jainforjain.com/member/business-listings/{listing_id}/edit"
        print(f"Opening {edit_url}...")
        await page.goto(edit_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(4000)
        
        print(f"Current URL: {page.url}")
        
        # Take a screenshot to inspect
        ss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"debug_edit_{listing_id}.png")
        await page.screenshot(path=ss_path, full_page=True)
        print(f"Saved debug screenshot to {ss_path}")
        
        # Inspect tabs
        tabs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button[role="tab"], nav button')).map(b => b.innerText.trim());
        }''')
        print(f"Tabs found: {tabs}")
        
        # Check Images tab
        images_btn = page.locator('button:has-text("Images")')
        if await images_btn.count() > 0:
            print("Clicking Images tab...")
            await images_btn.first.click()
            await page.wait_for_timeout(2000)
            
            # Check inputs in Images tab
            inputs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('input, select')).map(el => ({
                    id: el.id,
                    name: el.name,
                    type: el.type,
                    value: el.value
                }));
            }''')
            print("Inputs in Images tab:")
            for inp in inputs:
                print("  ", inp)
                
            # Check FilePond elements
            fileponds = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('.filepond--root, [data-filepond-item-state]')).map(el => ({
                    className: el.className,
                    text: el.innerText
                }));
            }''')
            print(f"FilePond elements: {fileponds}")
            
        # Check save buttons
        save_buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button[type="submit"], button')).map(b => b.innerText.trim()).filter(t => t.toLowerCase().includes('save') || t.toLowerCase().includes('update') || t.toLowerCase().includes('submit'));
        }''')
        print(f"Save/Update buttons: {save_buttons}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_edit_page(252))
