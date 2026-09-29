import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path
from backend.system_guard import CHROMIUM_TURBO_ARGS

async def inspect_filepond_buttons():
    session_file = get_session_file_path("mohit12836+1@gmail.com")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        context = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        await page.goto("https://jainforjain.com/member/business-listings/2134/edit", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        images_tab = page.locator('button:has-text("Images")')
        if await images_tab.count() > 0:
            await images_tab.first.click()
            await page.wait_for_timeout(2000)

        buttons = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('.filepond--root button, .filepond--file-action-button')).map(b => ({
                className: b.className,
                title: b.title,
                innerText: b.innerText,
                type: b.type
            }));
            return btns;
        }''')
        print("FilePond buttons:", buttons)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_filepond_buttons())
