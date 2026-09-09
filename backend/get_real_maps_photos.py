import os
import sys
import asyncio
import urllib.request
from playwright.async_api import async_playwright

PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "indore_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

PLACES = {
    252: "Shree Parshwanath Digambar Jain Mandir Indore",
    253: "Kanch Mandir Indore",
    254: "Shree Digambar Jain Marwadi Mandir Indore Sarafa",
    255: "Dada Vadi Jain Dharamshala Indore",
    256: "Lal mandir Indore Sarafa"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

async def fetch_photos():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=headers["User-Agent"]
        )
        page = await context.new_page()

        for lid, name in PLACES.items():
            target_file = os.path.join(PHOTO_DIR, f"{lid}_photo.jpg")
            
            # If valid image already exists (>50KB and <5MB), skip
            if os.path.exists(target_file) and 50000 < os.path.getsize(target_file) < 5000000:
                print(f"Listing {lid} already has good photo ({os.path.getsize(target_file)} bytes). Skipping.")
                continue

            print(f"\n[Listing {lid}] Searching Google Maps for: '{name}'...")
            search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(name)}"
            
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=40000)
                await page.wait_for_timeout(4000)

                # Look for photo button or image in detail panel
                img_url = await page.evaluate('''() => {
                    const heroImg = document.querySelector('button[aria-label*="Photo"] img, div[role="region"] button img, img[src*="googleusercontent.com/p/"]');
                    if (heroImg && heroImg.src) return heroImg.src;
                    const anyImg = document.querySelector('img[src*="googleusercontent.com"]');
                    return anyImg ? anyImg.src : null;
                }''')

                if not img_url:
                    # Check first result click
                    first_res = page.locator('a[href*="/maps/place/"]').first
                    if await first_res.count() > 0:
                        await first_res.click()
                        await page.wait_for_timeout(3000)
                        img_url = await page.evaluate('''() => {
                            const heroImg = document.querySelector('button[aria-label*="Photo"] img, img[src*="googleusercontent.com/p/"]');
                            return heroImg ? heroImg.src : null;
                        }''')

                if img_url:
                    # Clean high-res URL
                    high_res = img_url.split('=')[0] + '=w800-h600-k-no'
                    print(f"Found genuine photo for {lid}: {high_res[:75]}...")
                    req = urllib.request.Request(high_res, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        with open(target_file, "wb") as f:
                            f.write(resp.read())
                    print(f"✓ Saved {target_file} ({os.path.getsize(target_file)} bytes)")
                else:
                    print(f"⚠️ Could not find photo on Google Maps for {lid}, taking clean screenshot...")
                    await page.screenshot(path=target_file)
            except Exception as e:
                print(f"Error fetching photo for {lid}: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_photos())
