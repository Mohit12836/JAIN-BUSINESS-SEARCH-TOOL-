import asyncio
import os
import sys
import re
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path
from backend.system_guard import CHROMIUM_TURBO_ARGS

async def inspect_5():
    session_file = get_session_file_path("mohit12836+1@gmail.com")
    listing_ids = [2125, 2134, 2135, 2136, 2137]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        context = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        results = []
        for lid in listing_ids:
            url = f"https://jainforjain.com/member/business-listings/{lid}/edit"
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # Get business name and category
            name_val = await page.input_value("input[id='data.business_name']") if await page.locator("input[id='data.business_name']").count() > 0 else ""
            cat_val = await page.evaluate('''() => {
                const el = document.querySelector("select[id*='category'], select[id*='business_category']");
                return el ? el.options[el.selectedIndex]?.text : "";
            }''')
            phone_val = await page.input_value("input[id='data.mobile']") if await page.locator("input[id='data.mobile']").count() > 0 else ""
            city_val = await page.evaluate('''() => {
                const el = document.querySelector("select[id*='city_id']");
                return el ? el.options[el.selectedIndex]?.text : "Indore";
            }''')

            results.append({
                "id": lid,
                "name": name_val,
                "category": cat_val,
                "phone": phone_val,
                "city": city_val
            })
            print(f"ID {lid}: Name='{name_val}' | Cat='{cat_val}' | Phone='{phone_val}' | City='{city_val}'")

        await browser.close()
        return results

if __name__ == "__main__":
    asyncio.run(inspect_5())
