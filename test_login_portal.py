import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Opening login page...")
        await page.goto("https://jainforjain.com/member/login", wait_until="networkidle", timeout=30000)
        
        print("Filling credentials...")
        await page.fill("input[id='data.email']", "mohit12836@gmail.com")
        await page.fill("input[id='data.password']", "223034000")
        
        print("Clicking Sign in...")
        await page.click("button[type='submit']")
        
        await page.wait_for_timeout(6000)
        
        print("After login URL:", page.url)
        print("Page title:", await page.title())
        
        body_text = await page.evaluate("() => document.body.innerText")
        print("\n--- Page Content Preview ---")
        print(body_text[:1000])
        print("------------------------------------------------")
        
        nav_links = await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a, button')).map(el => ({
                text: (el.innerText || '').trim(),
                href: el.href || ''
            })).filter(l => l.text.length > 0 && l.text.length < 55);
            return links;
        }''')
        
        print("\nAvailable Navigation Links:")
        for l in nav_links[:30]:
            print(f"  [{l['text']}] -> {l['href']}")
            
        await page.screenshot(path="dashboard_screenshot.png")
        print("\nScreenshot saved as dashboard_screenshot.png")
        await browser.close()

asyncio.run(test_login())
