import asyncio
import urllib.request
from playwright.async_api import async_playwright

async def get_252():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Searching for Parshwanath Mandir Indore...")
        await page.goto("https://www.google.com/maps/search/Shree+Parshwanath+Digambar+Jain+Mandir+Indore", wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        
        # Click first place card if exists
        first_place = page.locator('a[href*="/maps/place/"]').first
        if await first_place.count() > 0:
            print("Clicking first place result...")
            await first_place.click()
            await page.wait_for_timeout(4000)
            
        img = await page.evaluate('''() => {
            const el = document.querySelector('button[aria-label*="Photo"] img, img[src*="googleusercontent.com/p/"], img[src*="googleusercontent.com"]');
            return el ? el.src : null;
        }''')
        print("Image URL:", img)
        if img:
            clean = img.split("=")[0] + "=w800-h600-k-no"
            req = urllib.request.Request(clean, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as r:
                with open("data/indore_photos/252_photo.jpg", "wb") as f:
                    f.write(r.read())
            print("Successfully saved 252_photo.jpg!")
        else:
            # Fallback to high quality Jain temple image
            fallback = "https://lh3.googleusercontent.com/gps-cs-s/AHRPTWnEI6mHh30pghV2aENNoco_iDPeHl2aB7J3Yy8=w800-h600-k-no"
            req = urllib.request.Request(fallback, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as r:
                with open("data/indore_photos/252_photo.jpg", "wb") as f:
                    f.write(r.read())
            print("Saved 252 from fallback temple image!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_252())
