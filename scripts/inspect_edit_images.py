import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path
from backend.system_guard import CHROMIUM_TURBO_ARGS

async def inspect_edit_form():
    session_file = get_session_file_path("mohit12836+1@gmail.com")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        context = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        edit_url = "https://jainforjain.com/member/business-listings/2134/edit"
        print(f"Navigating to {edit_url}...")
        await page.goto(edit_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Click Images tab
        images_tab = page.locator('button:has-text("Images")')
        if await images_tab.count() > 0:
            print("Clicking Images tab...")
            await images_tab.first.click()
            await page.wait_for_timeout(2000)

        # Inspect FilePond elements and file inputs
        info = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input[type="file"]')).map(i => ({
                id: i.id,
                name: i.name,
                accept: i.accept
            }));
            const fileponds = Array.from(document.querySelectorAll('.filepond--root')).map(f => ({
                className: f.className,
                items: Array.from(f.querySelectorAll('.filepond--item')).length
            }));
            return { inputs, fileponds };
        }''')
        print("Images tab info:", info)
        await page.screenshot(path="edit_2134_images_tab.png", full_page=True)
        print("Saved screenshot to edit_2134_images_tab.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_edit_form())
