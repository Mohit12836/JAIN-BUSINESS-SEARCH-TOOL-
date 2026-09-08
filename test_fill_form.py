import asyncio
import openpyxl
from playwright.async_api import async_playwright

SHEET_URL = "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
EXCEL_PATH = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx"

async def sync_to_google_sheets():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb.active
    
    tsv_lines = []
    for row in ws.iter_rows(values_only=True):
        clean_row = []
        for cell in row:
            val = str(cell or "").replace("\t", " ").replace("\n", " ").strip()
            # If starts with + like +91, remove + so Google Sheets doesn't treat it as formula
            if val.startswith("+"):
                val = val[1:].strip()
            clean_row.append(val)
        tsv_lines.append("\t".join(clean_row))
        
    tsv_content = "\n".join(tsv_lines)
    print(f"Prepared {len(tsv_lines)} rows of TSV data (clean phone numbers).")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            permissions=["clipboard-read", "clipboard-write"],
            viewport={"width": 1400, "height": 900}
        )
        page = await context.new_page()
        print(f"Opening Google Sheet: {SHEET_URL}")
        await page.goto(SHEET_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(6000)
        
        # Click on grid canvas
        print("Clicking into grid...")
        await page.mouse.click(180, 220)
        await page.wait_for_timeout(1000)
        
        # Select all and delete previous content if any
        await page.keyboard.press("Control+a")
        await page.wait_for_timeout(500)
        
        # Write to clipboard via evaluate
        await page.evaluate("(text) => navigator.clipboard.writeText(text)", tsv_content)
        print("Clipboard set. Pasting with Ctrl+V...")
        await page.keyboard.press("Control+v")
        await page.wait_for_timeout(6000)
        
        # Take verification screenshot
        screenshot_path = r"C:\Users\hp\Desktop\Google_Sheet_Synced_Preview.png"
        await page.screenshot(path=screenshot_path)
        print(f"Saved screenshot to Desktop: {screenshot_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(sync_to_google_sheets())









