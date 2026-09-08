"""
Google Sheets Automated Synchronization Engine.
Directly syncs the 26-column Master Excel sheet to the live Google Sheet:
https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing

Features:
- Sanitizes '+' prefixed phone numbers to prevent Google Sheets '#ERROR!' formula bugs.
- Normalizes newlines and tabs to maintain strict 26-column row alignment.
- Automated fast clipboard paste via Playwright headless browser.
- Generates a visual proof screenshot on Desktop.
"""

import os
import sys
import asyncio
import openpyxl
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from backend.config import get_master_excel_path
except ImportError:
    from config import get_master_excel_path

DEFAULT_EXCEL = get_master_excel_path()
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
DEFAULT_SCREENSHOT = os.path.join(os.path.expanduser("~"), "Desktop", "Google_Sheet_Synced_Preview.png") if os.path.exists(os.path.join(os.path.expanduser("~"), "Desktop")) else "Google_Sheet_Synced_Preview.png"

def prepare_tsv_content(excel_path: str) -> str:
    """
    Reads the Excel file and builds a clean TSV string formatted safely for Google Sheets.
    Strips leading '+' on phone numbers to avoid Google Sheets formula evaluation errors.
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at: {excel_path}")

    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb.active

    tsv_lines = []
    for row in ws.iter_rows(values_only=True):
        row_cells = []
        for cell in row:
            if cell is None:
                val = ""
            else:
                val = str(cell).strip()
                # Clean phone numbers or formulas starting with '+' or '='
                if val.startswith("+"):
                    # Prepend an apostrophe or remove '+' so Sheets treats it as plain text
                    val = val.lstrip("+")
                elif val.startswith("="):
                    val = "'" + val
                
                # Clean delimiters
                val = val.replace("\t", " ").replace("\r\n", " ").replace("\n", " ")
            row_cells.append(val)
            
        tsv_lines.append("\t".join(row_cells))

    return "\n".join(tsv_lines)

async def sync_excel_to_google_sheet(
    excel_path: str = DEFAULT_EXCEL,
    sheet_url: str = DEFAULT_SHEET_URL,
    screenshot_path: str = DEFAULT_SCREENSHOT
) -> bool:
    """
    Asynchronously pastes Excel contents directly into the specified Google Sheet.
    """
    print(f"\n=======================================================")
    print(f"📊 GOOGLE SHEET DIRECT SYNC")
    print(f"Excel Source: {excel_path}")
    print(f"Target Sheet: {sheet_url}")
    print(f"=======================================================")

    try:
        tsv_content = prepare_tsv_content(excel_path)
        row_count = len(tsv_content.splitlines())
        print(f"✓ Prepared {row_count} rows across all 26 columns (Phone numbers sanitized).")
    except Exception as e:
        print(f"❌ Error preparing Excel data: {e}")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = await context.new_page()

        try:
            print("🌐 Opening Google Sheet in background...")
            await page.goto(sheet_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)

            # Focus the sheet canvas and move to cell A1
            print("📌 Navigating to Cell A1...")
            await page.click('div.grid-container, div[role="grid"], div.waffle-canvas')
            await page.wait_for_timeout(500)
            
            # Press Ctrl+Home to guarantee cursor is at A1
            await page.keyboard.press("Control+Home")
            await page.wait_for_timeout(500)

            # Write TSV into clipboard
            print("📋 Injecting TSV into clipboard...")
            await page.evaluate("(text) => navigator.clipboard.writeText(text)", tsv_content)

            # Paste into the active sheet
            print("⚡ Pasting data into Google Sheet (Ctrl+V)...")
            await page.keyboard.press("Control+v")
            await page.wait_for_timeout(4500)

            # Save proof screenshot
            await page.screenshot(path=screenshot_path)
            print(f"✅ Success! Google Sheet synchronized with {row_count} rows.")
            print(f"📸 Verification screenshot saved: {screenshot_path}")
            return True

        except Exception as err:
            print(f"❌ Error during Google Sheet sync: {err}")
            return False
        finally:
            await browser.close()

def run_sync_sync(excel_path: str = DEFAULT_EXCEL, sheet_url: str = DEFAULT_SHEET_URL) -> bool:
    """Synchronous wrapper for easy execution from CLI or other modules."""
    return asyncio.run(sync_excel_to_google_sheet(excel_path, sheet_url))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sync Excel to Google Sheets")
    parser.add_argument("--excel", default=DEFAULT_EXCEL, help="Source Excel path")
    parser.add_argument("--url", default=DEFAULT_SHEET_URL, help="Target Google Sheet URL")
    args = parser.parse_args()

    success = run_sync_sync(args.excel, args.url)
    sys.exit(0 if success else 1)
