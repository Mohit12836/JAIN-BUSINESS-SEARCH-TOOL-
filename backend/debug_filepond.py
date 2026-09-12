import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS

async def test_filepond():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 1200})
        
        # Monitor network requests to see Livewire / upload endpoints
        page.on("request", lambda req: print(f"REQ: {req.method} {req.url[:70]}") if "upload" in req.url or "livewire" in req.url else None)
        page.on("response", lambda res: print(f"RES: {res.status} {res.url[:70]}") if "upload" in res.url or "livewire" in res.url else None)
        
        await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        await page.goto("https://jainforjain.com/member/business-listings/267/edit", wait_until="networkidle")
        
        print("Clicking Images tab...")
        await page.locator('button', has_text="Images").first.click()
        await page.wait_for_timeout(1000)
        
        inputs = await page.query_selector_all('input[type="file"]')
        print(f"Total file inputs: {len(inputs)}")
        for i, inp in enumerate(inputs):
            name = await inp.get_attribute("name")
            id_val = await inp.get_attribute("id")
            print(f"Input {i}: name={name}, id={id_val}")
            
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "canva_storefronts", "jmj_jewellers_logo_1080x1080.png")
        banner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "canva_storefronts", "jmj_jewellers_banner_1200x500.png")
        
        print(f"Setting logo: {logo_path}")
        await inputs[0].set_input_files(logo_path)
        print("Waiting 5 seconds for logo upload...")
        await page.wait_for_timeout(5000)
        
        print(f"Setting banner: {banner_path}")
        await inputs[1].set_input_files(banner_path)
        print("Waiting 5 seconds for banner upload...")
        await page.wait_for_timeout(5000)
        
        # Check FilePond DOM state
        dom_check = await page.evaluate('''() => {
            const items = document.querySelectorAll('.filepond--item');
            const data = [];
            items.forEach((it, idx) => {
                data.push({
                    idx: idx,
                    state: it.getAttribute('data-filepond-item-state'),
                    text: it.innerText
                });
            });
            return data;
        }''')
        print("FilePond DOM state:", dom_check)
        
        # Now click Save changes
        print("Clicking Save changes button...")
        save_btn = page.locator('button', has_text="Save changes")
        await save_btn.first.click()
        await page.wait_for_timeout(5000)
        
        shot_path = os.path.join(os.path.expanduser("~"), "Desktop", "debug_after_save_images.png")
        await page.screenshot(path=shot_path, full_page=True)
        print(f"Screenshot after save: {shot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_filepond())
