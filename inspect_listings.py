import asyncio
from playwright.async_api import async_playwright

async def inspect_business_listings():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://jainforjain.com/member/login", wait_until="networkidle")
        await page.fill("input[id='data.email']", "mohit12836@gmail.com")
        await page.fill("input[id='data.password']", "223034000")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(4000)
        
        print("Navigating to my business listings...")
        await page.goto("https://jainforjain.com/member/business-listings", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        print("Page URL:", page.url)
        print("Title:", await page.title())
        
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a, button')).map(el => ({
                text: (el.innerText || '').trim(),
                href: el.href || ''
            })).filter(l => l.text.length > 0 && l.text.length < 60);
        }''')
        
        print("\nAction Buttons / Links:")
        for b in buttons:
            print(f"  [{b['text']}] -> {b['href']}")
            
        await page.screenshot(path="business_listings_screenshot.png")
        await browser.close()

asyncio.run(inspect_business_listings())
