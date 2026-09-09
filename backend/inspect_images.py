import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import json
from playwright.async_api import async_playwright
from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS, CREATE_URL

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1400, 'height': 900})
        await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        await page.goto(CREATE_URL, wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        await page.click('button:has-text("Images")')
        await page.wait_for_timeout(2000)
        inputs = await page.evaluate('''() => {
            const elements = Array.from(document.querySelectorAll('input[type="file"], input, select, .filepond--root'));
            return elements.map(e => ({
                tag: e.tagName,
                type: e.type || '',
                id: e.id || '',
                name: e.name || '',
                class: (e.className || '').toString()
            }));
        }''')
        print("FOUND_INPUTS:")
        for inp in inputs:
            if inp['type'] == 'file' or 'filepond' in inp['class'] or 'image' in inp['id'].lower() or 'logo' in inp['id'].lower():
                print(inp)
        await page.screenshot(path="frontend/images_tab_screenshot.png")
        print("Screenshot saved to frontend/images_tab_screenshot.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

