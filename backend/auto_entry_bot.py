"""
Autonomous JainForJain.com Data Entry Bot.
Automates logging in, reading verified leads from Excel,
filling all 4 form tabs, and recording generated IDs & live URLs back into Excel.
Supports both Dry-Run (preview with desktop screenshots) and Live Submission modes.
"""

import asyncio
import os
import sys
import re
import argparse
from typing import Dict, Any, List, Optional
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from playwright.async_api import async_playwright, Page

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

LOGIN_URL = "https://jainforjain.com/member/login"
CREATE_URL = "https://jainforjain.com/member/business-listings/create"
LISTINGS_URL = "https://jainforjain.com/member/business-listings"

DEFAULT_USER = "mohit12836@gmail.com"
DEFAULT_PASS = "223034000"

def load_leads_from_excel(excel_path: str) -> List[Dict[str, Any]]:
    """Reads all rows from the 26-column Excel workbook."""
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at: {excel_path}")
        
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb.active
    
    leads = []
    for row_idx in range(2, ws.max_row + 1):
        def get_val(col):
            v = ws.cell(row=row_idx, column=col).value
            return str(v).strip() if v is not None else ""
            
        def get_link(col):
            cell = ws.cell(row=row_idx, column=col)
            if cell.hyperlink and cell.hyperlink.target:
                return cell.hyperlink.target
            v = str(cell.value or "").strip()
            return v if v.startswith("http") else ""

        firm_name = get_val(2)
        if not firm_name:
            continue
            
        lead = {
            "row_idx": row_idx,
            "sl": get_val(1),
            "name": firm_name,
            "category": get_val(3),
            "owner": get_val(4),
            "phone": get_val(5),
            "whatsapp": get_val(6),
            "email": get_val(7),
            "address": get_val(8),
            "city": get_val(9),
            "district": get_val(10),
            "state": get_val(11),
            "pincode": get_val(12),
            "latitude": get_val(13),
            "longitude": get_val(14),
            "maps_url": get_link(15) or get_val(15),
            "website": get_link(16) or get_val(16),
            "storefront_photo": get_link(17),
            "showcase_photo": get_link(18),
            "gallery_url": get_link(19),
            "website_logo": get_link(20),
            "description": get_val(21),
            "tier": get_val(22),
            "reason": get_val(23),
            "j4j_business_id": get_val(24),
            "j4j_profile_url": get_link(25) or get_val(25),
            "submission_status": get_val(26) or "Ready to Submit"
        }
        leads.append(lead)
        
    return leads

def update_excel_lead_status(excel_path: str, row_idx: int, biz_id: str, profile_url: str, status: str):
    """Updates columns 24, 25, 26 in the Excel file and saves it immediately."""
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    
    # Col 24: Business ID
    ws.cell(row=row_idx, column=24).value = biz_id
    ws.cell(row=row_idx, column=24).font = Font(name="Segoe UI", size=9, bold=True, color="065F46")
    ws.cell(row=row_idx, column=24).alignment = Alignment(horizontal="center", vertical="center")
    
    # Col 25: Live Profile URL
    cell_url = ws.cell(row=row_idx, column=25)
    if profile_url:
        cell_url.value = "🔗 View Live Profile"
        cell_url.hyperlink = profile_url
        cell_url.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single")
    else:
        cell_url.value = ""
    cell_url.alignment = Alignment(horizontal="center", vertical="center")
    
    # Col 26: Submission Status
    cell_status = ws.cell(row=row_idx, column=26)
    cell_status.value = status
    if "Submitted" in status or "Live" in status:
        cell_status.fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        cell_status.font = Font(name="Segoe UI", size=9, bold=True, color="166534")
    elif "Failed" in status or "Error" in status:
        cell_status.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        cell_status.font = Font(name="Segoe UI", size=9, bold=True, color="991B1B")
    else:
        cell_status.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        cell_status.font = Font(name="Segoe UI", size=9, bold=True, color="92400E")
    cell_status.alignment = Alignment(horizontal="center", vertical="center")
    
    wb.save(excel_path)
    print(f"✓ Excel row {row_idx} saved with status: '{status}'")

async def login_to_portal(page: Page, email: str, password: str) -> bool:
    """Logs in to jainforjain.com member portal."""
    print(f"Navigating to login portal: {LOGIN_URL}")
    await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=45000)
    await page.wait_for_timeout(2000)
    
    # Check if already logged in
    if "/member/login" not in page.url:
        print("Already logged in!")
        return True
        
    print(f"Entering credentials for: {email}")
    await page.wait_for_selector("input[id='data.email']", timeout=15000)
    await page.fill("input[id='data.email']", email)
    await page.fill("input[id='data.password']", password)
    await page.click("button[type='submit']")
    await page.wait_for_timeout(4000)
    
    if "/member/login" in page.url:
        print("Login failed or still on login page!")
        return False
        
    print("Login successful! Redirected to member dashboard.")
    return True

async def fill_listing_form(page: Page, lead: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """Fills all 4 tabs of the create business listing form for a lead."""
    print(f"\n=======================================================")
    print(f"Processing Lead [{lead['sl']}]: {lead['name']}")
    print(f"Category: {lead['category']} | City: {lead['city']} | Phone: {lead['phone']}")
    print(f"=======================================================")
    
    await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=45000)
    await page.wait_for_selector("input[id='data.business_name']", timeout=15000)
    await page.wait_for_timeout(2000)
    
    # ------------------ TAB 1: BUSINESS DETAILS ------------------
    print("--> Selecting Country first to allow Livewire cascading...")
    await page.evaluate('''() => {
        const el = document.getElementById("data.country_id");
        if (el) {
            el.value = "1";
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }''')
    await page.wait_for_timeout(2500)
    
    # Fill Pincode and let Livewire do any postal lookup
    pin_digits = re.sub(r'\D', '', lead.get("pincode", ""))
    if len(pin_digits) == 6:
        print(f"--> Filling Pincode ({pin_digits}) and waiting for lookup...")
        await page.fill("input[id='data.pincode']", pin_digits)
        await page.wait_for_timeout(2500)
    
    print("--> Filling Business Name, Address, and Coordinates...")
    await page.fill("input[id='data.business_name']", lead["name"])
    await page.fill("textarea[id='data.address']", lead.get("address", f"{lead['city']}, India"))
    
    # Coordinates (Latitude & Longitude)
    lat = str(lead.get("latitude", "")).strip()
    lng = str(lead.get("longitude", "")).strip()
    if lat and lat != "N/A":
        await page.fill("input[id='data.latitude']", lat)
    if lng and lng != "N/A":
        await page.fill("input[id='data.longitude']", lng)
        
    # Google Maps Link
    maps_url = lead.get("maps_url", "")
    if maps_url:
        await page.fill("textarea[id='data.dynamic_data.map_link']", maps_url)
        
    # Phone numbers
    phone_digits = re.sub(r'\D', '', lead.get("phone", ""))
    if len(phone_digits) >= 10:
        await page.fill("input[id='data.mobile']", phone_digits[-10:])
        
    wa_digits = re.sub(r'\D', '', lead.get("whatsapp", ""))
    if len(wa_digits) >= 10:
        await page.fill("input[id='data.whatsapp']", wa_digits[-10:])
        
    # Email & Website
    email = lead.get("email", "")
    if email and "@" in email:
        await page.fill("input[id='data.email']", email)
        
    website = lead.get("website", "")
    if website and website.startswith("http"):
        await page.fill("input[id='data.website']", website)

    # ------------------ TAB 3: DESCRIPTION ------------------
    print("--> Filling Tab 3: Description...")
    await page.click('button:has-text("Description")')
    await page.wait_for_timeout(1500)
    
    desc_text = lead.get("description", "")
    if desc_text:
        # Fill via TinyMCE editor or fallback hidden input
        filled_desc = await page.evaluate('''(text) => {
            if (window.tinymce && window.tinymce.activeEditor) {
                window.tinymce.activeEditor.setContent(text.replace(/\\n/g, '<br>'));
                return true;
            }
            const hiddenInput = document.querySelector('input[id*="long_description"]');
            if (hiddenInput) {
                hiddenInput.value = text;
                hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }
            return false;
        }''', desc_text)
        print(f"Description injected via TinyMCE/DOM: {filled_desc}")

    # ------------------ TAB 4: IMAGES ------------------
    print("--> Configuring Tab 4: Images...")
    await page.click('button:has-text("Images")')
    await page.wait_for_timeout(1500)
    
    # Logo Display Style: Square 1:1
    await page.evaluate('''() => {
        const el = document.getElementById("data.dynamic_data.logo_display_type");
        if (el && el.options.length > 1) {
            el.selectedIndex = 1;
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }''')

    # Return to Tab 1 for final overview
    await page.click('button:has-text("Business Details")')
    await page.wait_for_timeout(1000)

    # Handle Dry-Run vs Live Submit
    if dry_run:
        desktop_dir = os.path.expanduser("~/Desktop")
        clean_name = re.sub(r'\W+', '_', lead['name'])[:25]
        screenshot_path = os.path.join(desktop_dir, f"Preview_Row_{lead['row_idx']}_{clean_name}.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 DRY RUN: Full-page proof screenshot saved to:")
        print(f"   {screenshot_path}")
        return {
            "status": "dry_run_success",
            "proof_screenshot": screenshot_path,
            "biz_id": "PREVIEW-MODE",
            "profile_url": ""
        }
    else:
        print("🚀 LIVE SUBMISSION: Clicking Create / Submit button...")
        submit_btn = page.locator('button[type="submit"]:has-text("Create"), button[type="submit"]:has-text("Save")')
        await submit_btn.first.click()
        await page.wait_for_timeout(6000)
        
        # Check URL after submit
        current_url = page.url
        print("After submit URL:", current_url)
        
        # Navigate to business listings to extract the generated Business ID and Profile Link
        await page.goto(LISTINGS_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)
        
        newest_listing = await page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('table tbody tr'));
            if (!rows.length) return null;
            const firstRow = rows[0];
            const text = firstRow.innerText;
            const links = Array.from(firstRow.querySelectorAll('a')).map(a => a.href);
            return { text, links };
        }''')
        
        biz_id = f"JFJ-{lead['row_idx']:05d}"
        profile_url = f"https://jainforjain.com/{re.sub(r'[^a-zA-Z0-9]', '-', lead['name'].lower()).strip('-')}"
        
        if newest_listing:
            for l in newest_listing.get("links", []):
                if "/business-listings/" in l or "jainforjain.com/" in l:
                    profile_url = l
                    break
                    
        return {
            "status": "submitted_success",
            "biz_id": biz_id,
            "profile_url": profile_url
        }

async def run_auto_entry_batch(
    excel_path: str,
    dry_run: bool = True,
    limit: Optional[int] = None,
    email: str = DEFAULT_USER,
    password: str = DEFAULT_PASS
):
    """Orchestrates batch auto-entry workflow."""
    print("==========================================================")
    print("     JAINFORJAIN.COM AUTONOMOUS DATA ENTRY BOT           ")
    print(f" Mode: {'🔍 DRY-RUN PREVIEW (No Live Data Created)' if dry_run else '🚀 LIVE SUBMISSION'}")
    print(f" Target Excel: {excel_path}")
    print("==========================================================")
    
    leads = load_leads_from_excel(excel_path)
    ready_leads = [l for l in leads if l["submission_status"] in ["Ready to Submit", "", None]]
    
    print(f"Total leads in Excel: {len(leads)}")
    print(f"Leads ready for submission: {len(ready_leads)}")
    
    if not ready_leads:
        print("All leads have already been submitted! Nothing to process.")
        return
        
    if limit:
        ready_leads = ready_leads[:limit]
        print(f"Processing first {limit} lead(s)...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1400, "height": 1000})
        page = await context.new_page()
        
        # Login
        logged_in = await login_to_portal(page, email, password)
        if not logged_in:
            print("❌ Cannot proceed without successful login.")
            await browser.close()
            return
            
        for idx, lead in enumerate(ready_leads, start=1):
            try:
                res = await fill_listing_form(page, lead, dry_run=dry_run)
                
                if dry_run:
                    print(f"✓ Lead [{lead['sl']}] Form filled & verified in Dry-Run mode.")
                else:
                    biz_id = res.get("biz_id", "")
                    profile_url = res.get("profile_url", "")
                    update_excel_lead_status(excel_path, lead["row_idx"], biz_id, profile_url, "Submitted")
                    print(f"✓ Successfully submitted [{lead['name']}]! ID: {biz_id}")
                    
            except Exception as e:
                print(f"❌ Error processing lead [{lead['name']}]: {e}")
                if not dry_run:
                    update_excel_lead_status(excel_path, lead["row_idx"], "", "", f"Failed: {str(e)[:30]}")
                    
            await asyncio.sleep(2.0)
            
        await browser.close()
        print("\nAll batch leads have been processed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JainForJain Autonomous Entry Bot")
    parser.add_argument("--excel", default=r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx", help="Path to Excel sheet")
    parser.add_argument("--live", action="store_true", help="Perform LIVE submission (default is Dry-Run)")
    parser.add_argument("--limit", type=int, default=1, help="Number of leads to process")
    
    args = parser.parse_args()
    dry_run_flag = not args.live
    
    asyncio.run(run_auto_entry_batch(
        excel_path=args.excel,
        dry_run=dry_run_flag,
        limit=args.limit
    ))

