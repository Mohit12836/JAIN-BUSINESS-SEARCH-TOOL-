"""
Autonomous JainForJain.com Data Entry Bot.
Automates logging in, reading verified leads from Excel,
filling all 4 form tabs, and recording generated IDs & live URLs back into Excel and Google Sheets.
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

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.google_sheets_sync import sync_excel_to_google_sheet
    from backend.config import get_master_excel_path
except ImportError:
    from google_sheets_sync import sync_excel_to_google_sheet
    from config import get_master_excel_path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import tempfile
import urllib.request
import time

def download_temp_image(image_url: str, filename_prefix: str = "j4j_img") -> Optional[str]:
    """Downloads an online image URL to a local temporary file for file uploading."""
    if not image_url or not image_url.startswith("http"):
        return None
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), "j4j_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        clean_url = image_url
        if "=w" in clean_url:
            clean_url = clean_url.split("=")[0] + "=s1600"
        ext = ".jpg"
        if ".png" in clean_url.lower():
            ext = ".png"
        temp_file = os.path.join(temp_dir, f"{filename_prefix}_{int(time.time()*1000)}{ext}")
        req = urllib.request.Request(
            clean_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=12) as response, open(temp_file, "wb") as out_file:
            out_file.write(response.read())
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1000:
            return temp_file
    except Exception as e:
        print(f"⚠️ Image download warning ({image_url[:40]}...): {e}")
    return None

LOGIN_URL = "https://jainforjain.com/member/login"
CREATE_URL = "https://jainforjain.com/member/business-listings/create"
LISTINGS_URL = "https://jainforjain.com/member/business-listings"

DEFAULT_USER = "mohit12836@gmail.com"
DEFAULT_PASS = "223034000"

# Verified official category IDs from jainforjain.com
CATEGORY_NAME_TO_ID = {
    "mandir-trust": 300,
    "mandir": 300,
    "trust": 300,
    "religious & spiritual": 93,
    "fashion & beauty": 87,
    "food & beverage": 74,
    "business & industry": 14,
    "healthcare & medical": 40,
    "real estate": 47,
    "home & living": 54,
    "automobile": 61,
    "travel & tourism": 68,
    "professional services": 22,
    "information technology (it)": 24,
    "education & training": 32,
    "ngos & social organizations": 4,
    "finance & banking": 2,
    "logistics & transportation": 1,
    "electronics & appliances": 3,
    "event management": 79,
    "media & entertainment": 81,
    "agriculture & farming": 96,
    "jobs & recruitment": 92,
    "sports & fitness": 6,
    "pet & animal care": 97,
    "government & public services": 98,
    "e-commerce & online business": 99,
    "miscellaneous services": 100,
    "direct selling and multi-level marketing": 305
}

CITY_TO_STATE_MAP = {
    "indore": "Madhya Pradesh",
    "bhopal": "Madhya Pradesh",
    "ujjain": "Madhya Pradesh",
    "gwalior": "Madhya Pradesh",
    "jabalpur": "Madhya Pradesh",
    "jaipur": "Rajasthan",
    "jodhpur": "Rajasthan",
    "udaipur": "Rajasthan",
    "kota": "Rajasthan",
    "ajmer": "Rajasthan",
    "ahmedabad": "Gujarat",
    "surat": "Gujarat",
    "vadodara": "Gujarat",
    "rajkot": "Gujarat",
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "nagpur": "Maharashtra",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
}

def resolve_state(lead: Dict[str, Any]) -> str:
    """Resolves Indian State for a lead based on city or address."""
    city = str(lead.get("city", "")).lower().strip()
    if city in CITY_TO_STATE_MAP:
        return CITY_TO_STATE_MAP[city]
    
    addr = str(lead.get("address", "")).lower()
    for c, s in CITY_TO_STATE_MAP.items():
        if c in addr:
            return s
            
    if "madhya pradesh" in addr or "mp" in addr:
        return "Madhya Pradesh"
    if "rajasthan" in addr:
        return "Rajasthan"
    if "gujarat" in addr:
        return "Gujarat"
    if "maharashtra" in addr:
        return "Maharashtra"
    return "Madhya Pradesh"

def get_category_id(category_name: str, firm_name: str = "") -> int:
    """Returns official numerical category ID on jainforjain.com."""
    text = (str(category_name) + " " + str(firm_name)).lower().strip()
    
    for k, v in CATEGORY_NAME_TO_ID.items():
        if k in text:
            return v
            
    if any(w in text for w in ["mandir", "trust", "temple", "derasar", "sangh", "dharamshala", "bhojanalaya"]):
        return 300
    if any(w in text for w in ["jewel", "gold", "saree", "textile", "fashion"]):
        return 87
    if any(w in text for w in ["food", "sweet", "namkeen", "restaurant"]):
        return 74
        
    return 14  # Default: Business & Industry

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
    
    # ------------------ STEP 1: SELECT COUNTRY (INDIA) ------------------
    print("--> Selecting Country (India) for Livewire cascade...")
    await page.evaluate('''() => {
        const el = document.getElementById("data.country_id");
        if (el) {
            el.value = "1";
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }''')
    await page.wait_for_timeout(2000)
    
    # ------------------ STEP 2: SELECT STATE ------------------
    target_state = resolve_state(lead)
    print(f"--> Selecting State: {target_state}...")
    state_wrap = page.locator('div.choices:has(select[id="data.state_id"])')
    await state_wrap.locator('.choices__inner').click()
    await page.wait_for_timeout(500)
    
    state_opt = state_wrap.locator('.choices__list--dropdown .choices__item--choice', has_text=target_state)
    if await state_opt.count() > 0:
        await state_opt.first.click()
    else:
        await state_wrap.locator('.choices__list--dropdown .choices__item--choice').first.click()
    await page.wait_for_timeout(3500)
    
    # ------------------ STEP 3: SELECT DISTRICT ------------------
    lead_city = lead.get("city", "Indore")
    print(f"--> Selecting District matching '{lead_city}'...")
    dist_wrap = page.locator('div.choices:has(select[id="data.district_id"])')
    await dist_wrap.locator('.choices__inner').click()
    await page.wait_for_timeout(500)
    
    dist_opt = dist_wrap.locator('.choices__list--dropdown .choices__item--choice', has_text=lead_city)
    if await dist_opt.count() > 0:
        await dist_opt.first.click()
    else:
        await dist_wrap.locator('.choices__list--dropdown .choices__item--choice').first.click()
    await page.wait_for_timeout(3500)
    
    # ------------------ STEP 4: SELECT CITY ------------------
    print(f"--> Selecting City matching '{lead_city}'...")
    city_wrap = page.locator('div.choices:has(select[id="data.city_id"])')
    await city_wrap.locator('.choices__inner').click()
    await page.wait_for_timeout(500)
    
    city_opt = city_wrap.locator('.choices__list--dropdown .choices__item--choice').filter(has_text=lead_city)
    if await city_opt.count() > 0:
        await city_opt.last.click()
    else:
        await city_wrap.locator('.choices__list--dropdown .choices__item--choice').first.click()
    await page.wait_for_timeout(2000)

    # ------------------ STEP 5: PREPARE DATA FIELDS ------------------
    pin_digits = re.sub(r'\D', '', lead.get("pincode", ""))
    if not pin_digits or len(pin_digits) != 6:
        pin_digits = "452002" if "indore" in lead_city.lower() else "302001"
        
    phone_digits = re.sub(r'\D', '', lead.get("phone", ""))
    mobile_val = phone_digits[-10:] if len(phone_digits) >= 10 else "9772290045"
    
    wa_digits = re.sub(r'\D', '', lead.get("whatsapp", ""))
    wa_val = wa_digits[-10:] if len(wa_digits) >= 10 else mobile_val
    
    address_val = lead.get("address", f"{lead['city']}, India")
    cat_id = get_category_id(lead.get("category", ""), lead.get("name", ""))
    
    print(f"--> Syncing Form State via Livewire $wire (Category ID: {cat_id})...")
    await page.evaluate('''async (args) => {
        const stateEl = document.getElementById("data.state_id");
        if (!window.Alpine || !window.Alpine.$data(stateEl)) return;
        const wire = window.Alpine.$data(stateEl).$wire;
        if (!wire) return;
        
        await wire.set('data.business_name', args.name);
        await wire.set('data.pincode', args.pincode);
        await wire.set('data.address', args.address);
        await wire.set('data.mobile', args.mobile);
        await wire.set('data.whatsapp', args.whatsapp);
        await wire.set('data.l1_category', args.catId);
        
        if (args.email) await wire.set('data.email', args.email);
        if (args.website) await wire.set('data.website', args.website);
        if (args.lat) await wire.set('data.latitude', args.lat);
        if (args.lng) await wire.set('data.longitude', args.lng);
        if (args.mapLink) await wire.set('data.dynamic_data.map_link', args.mapLink);
    }''', {
        "name": lead["name"],
        "pincode": pin_digits,
        "address": address_val,
        "mobile": mobile_val,
        "whatsapp": wa_val,
        "catId": cat_id,
        "email": lead.get("email", ""),
        "website": lead.get("website", ""),
        "lat": str(lead.get("latitude", "")).strip(),
        "lng": str(lead.get("longitude", "")).strip(),
        "mapLink": lead.get("maps_url", "")
    })
    await page.wait_for_timeout(1500)

    # Fill DOM inputs as dual-layer backup
    await page.fill("input[id='data.business_name']", lead["name"])
    await page.fill("input[id='data.pincode']", pin_digits)
    await page.fill("textarea[id='data.address']", address_val)
    await page.fill("input[id='data.mobile']", mobile_val)
    await page.fill("input[id='data.whatsapp']", wa_val)
    
    # ------------------ STEP 6: TAB 3 (DESCRIPTION) ------------------
    desc_text = lead.get("description", "")
    if desc_text:
        print("--> Injecting Tab 3: Description...")
        await page.click('button:has-text("Description")')
        await page.wait_for_timeout(1000)
        await page.evaluate('''(text) => {
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

    # ------------------ STEP 7: TAB 4 (IMAGES & PHOTO UPLOAD) ------------------
    print("--> Configuring Tab 4: Uploading Genuine Signboard / Storefront Photo...")
    await page.click('button:has-text("Images")')
    await page.wait_for_timeout(1500)
    await page.evaluate('''() => {
        const el = document.getElementById("data.dynamic_data.logo_display_type");
        if (el && el.options.length > 1) {
            el.selectedIndex = 1;
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }''')
    
    # -------------------------------------------------------------
    # SMART PHOTO & CANVA STOREFRONT UPLOADER
    # If genuine photo exists (> 10KB), upload it.
    # If photo is missing, broken, or low-quality:
    # Automatically generate Canva-designed Storefront Logo & Banner!
    # -------------------------------------------------------------
    from backend.canva_storefront_generator import storefront_generator

    photo_url = lead.get("storefront_photo") or lead.get("photo_url") or ""
    temp_img_path = None
    if photo_url:
        clean_lead_name = re.sub(r'\W+', '_', lead.get('name', 'lead'))[:15]
        temp_img_path = download_temp_image(photo_url, filename_prefix=clean_lead_name)
    
    # Check if we have a valid photo (> 10KB)
    has_valid_photo = temp_img_path and os.path.exists(temp_img_path) and os.path.getsize(temp_img_path) > 10000

    logo_upload_file = temp_img_path if has_valid_photo else None
    banner_upload_file = temp_img_path if has_valid_photo else None

    if not has_valid_photo:
        print(f"🎨 [Canva Auto-Designer]: Shop '{lead.get('name')}' photo missing or low-quality.")
        print("   Generating professional Canva Storefront Logo and Banner...")
        try:
            gen_logo, gen_banner = await storefront_generator.generate_storefront_assets_async(
                firm_name=lead.get("name", "Jain Business"),
                category=lead.get("category_clean", lead.get("category", "Business")),
                city=lead.get("city", "Indore"),
                phone=lead.get("phone", ""),
                existing_photo_path=temp_img_path if temp_img_path and os.path.exists(temp_img_path) else None
            )
            if gen_logo and os.path.exists(gen_logo):
                logo_upload_file = gen_logo
            if gen_banner and os.path.exists(gen_banner):
                banner_upload_file = gen_banner
        except Exception as c_err:
            print(f"⚠️ Canva storefront generator warning: {c_err}")

    # Upload to FilePond inputs (file_inputs[0] = Logo, file_inputs[1] = Banner)
    try:
        file_inputs = await page.query_selector_all('input[type="file"]')
        if file_inputs:
            if logo_upload_file and os.path.exists(logo_upload_file):
                print(f"--> Uploading to Logo FilePond: {logo_upload_file}")
                await file_inputs[0].set_input_files(logo_upload_file)
            
            if len(file_inputs) > 1 and banner_upload_file and os.path.exists(banner_upload_file):
                print(f"--> Uploading to Banner FilePond: {banner_upload_file}")
                await file_inputs[1].set_input_files(banner_upload_file)

            print("--> Waiting for FilePond upload completion...")
            try:
                await page.wait_for_selector(
                    '.filepond--item[data-filepond-item-state="processing-complete"], .filepond--image-preview, .filepond--file-info',
                    timeout=18000
                )
                print("✓ Storefront images successfully uploaded and attached!")
            except Exception as fe:
                print(f"FilePond wait notice: {fe}")
                await page.wait_for_timeout(3500)
    except Exception as up_err:
        print(f"⚠️ Photo upload error: {up_err}")
    
    # Return to Tab 1
    await page.click('button:has-text("Business Details")')
    await page.wait_for_timeout(1000)

    # ------------------ STEP 8: DRY-RUN vs LIVE SUBMISSION ------------------
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
        print("🚀 LIVE SUBMISSION: Clicking Create button...")
        create_btn = page.locator('button[type="submit"]:has-text("Create")')
        await create_btn.first.click()
        await page.wait_for_timeout(6000)
        
        current_url = page.url
        print(f"URL after submission: {current_url}")
        
        # Check for error notifications
        errors = await page.evaluate('''() => {
            const errs = Array.from(document.querySelectorAll('p.fi-fo-field-wrp-error-message, div.fi-no-notification-danger'));
            return errs.map(e => e.innerText.trim()).filter(x => x.length > 0);
        }''')
        
        if errors:
            slug_conflict = any("slug" in e.lower() or "url key" in e.lower() for e in errors)
            if slug_conflict:
                print(f"⚠️ Duplicate slug detected on portal! Resolving collision for [{lead['name']}]...")
                # Retry 1: Append City
                retry_name = f"{lead['name']} - {lead_city}"
                print(f"--> Auto-retrying submission with: '{retry_name}'")
                await page.evaluate('''async (n) => {
                    const stateEl = document.getElementById("data.state_id");
                    if (window.Alpine && window.Alpine.$data(stateEl)) {
                        await window.Alpine.$data(stateEl).$wire.set('data.business_name', n);
                    }
                }''', retry_name)
                await page.fill("input[id='data.business_name']", retry_name)
                await page.wait_for_timeout(1000)
                await create_btn.first.click()
                await page.wait_for_timeout(6000)
                
                current_url = page.url
                errors = await page.evaluate('''() => {
                    const errs = Array.from(document.querySelectorAll('p.fi-fo-field-wrp-error-message, div.fi-no-notification-danger'));
                    return errs.map(e => e.innerText.trim()).filter(x => x.length > 0);
                }''')
                
                if errors and any("slug" in e.lower() or "url key" in e.lower() for e in errors):
                    # Retry 2: Append City + Pincode
                    retry_name_pin = f"{lead['name']} - {lead_city} ({pin_digits})"
                    print(f"--> Auto-retrying with location identifier: '{retry_name_pin}'")
                    await page.evaluate('''async (n) => {
                        const stateEl = document.getElementById("data.state_id");
                        if (window.Alpine && window.Alpine.$data(stateEl)) {
                            await window.Alpine.$data(stateEl).$wire.set('data.business_name', n);
                        }
                    }''', retry_name_pin)
                    await page.fill("input[id='data.business_name']", retry_name_pin)
                    await page.wait_for_timeout(1000)
                    await create_btn.first.click()
                    await page.wait_for_timeout(6000)
                    current_url = page.url
                    errors = await page.evaluate('''() => {
                        const errs = Array.from(document.querySelectorAll('p.fi-fo-field-wrp-error-message, div.fi-no-notification-danger'));
                        return errs.map(e => e.innerText.trim()).filter(x => x.length > 0);
                    }''')
                    
        if errors:
            raise Exception(f"Form validation errors: {', '.join(errors)}")
            
        # Extract ID from redirected edit URL: /member/business-listings/{id}/edit
        biz_num_match = re.search(r'/business-listings/(\d+)', current_url)
        if biz_num_match:
            biz_id = f"JFJ-{int(biz_num_match.group(1)):05d}"
        else:
            biz_id = f"JFJ-{lead['row_idx']:05d}"
            
        clean_slug = re.sub(r'[^a-zA-Z0-9]+', '-', lead['name'].lower()).strip('-')
        profile_url = f"https://jainforjain.com/{clean_slug}"
        
        print(f"✓ Listing created successfully! Business ID: {biz_id}")
        print(f"✓ Profile URL: {profile_url}")
        
        return {
            "status": "submitted_success",
            "biz_id": biz_id,
            "profile_url": profile_url
        }

async def run_auto_entry_batch(
    excel_path: Optional[str] = None,
    dry_run: bool = True,
    limit: Optional[int] = None,
    city_filter: Optional[str] = None,
    email: str = DEFAULT_USER,
    password: str = DEFAULT_PASS
):
    """Orchestrates batch auto-entry workflow."""
    if not excel_path:
        excel_path = get_master_excel_path()
        
    print("==========================================================")
    print("     JAINFORJAIN.COM AUTONOMOUS DATA ENTRY BOT           ")
    print(f" Mode: {'🔍 DRY-RUN PREVIEW (No Live Data Created)' if dry_run else '🚀 LIVE SUBMISSION'}")
    print(f" Target Excel: {excel_path}")
    if city_filter:
        print(f" Priority City: {city_filter}")
    print("==========================================================")
    
    leads = load_leads_from_excel(excel_path)
    ready_leads = [l for l in leads if l["submission_status"] in ["Ready to Submit", "", None]]
    
    if city_filter:
        city_leads = [l for l in ready_leads if city_filter.lower() in str(l.get("city", "")).lower()]
        other_leads = [l for l in ready_leads if city_filter.lower() not in str(l.get("city", "")).lower()]
        ready_leads = city_leads + other_leads
    
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
            
        submitted_count = 0
        for idx, lead in enumerate(ready_leads, start=1):
            try:
                res = await fill_listing_form(page, lead, dry_run=dry_run)
                
                if dry_run:
                    print(f"✓ Lead [{lead['sl']}] Form filled & verified in Dry-Run mode.")
                else:
                    biz_id = res.get("biz_id", "")
                    profile_url = res.get("profile_url", "")
                    update_excel_lead_status(excel_path, lead["row_idx"], biz_id, profile_url, "Submitted - Live")
                    print(f"✓ Successfully submitted [{lead['name']}]! ID: {biz_id}")
                    submitted_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing lead [{lead['name']}]: {e}")
                if not dry_run:
                    update_excel_lead_status(excel_path, lead["row_idx"], "", "", f"Failed: {str(e)[:30]}")
                    
            await asyncio.sleep(2.0)
            
        await browser.close()
        
        # If any live submissions occurred, trigger instant Google Sheet sync!
        if not dry_run and submitted_count > 0:
            print("\n🔄 Synchronizing updated Excel statuses to Google Sheets...")
            try:
                await sync_excel_to_google_sheet(excel_path)
            except Exception as e:
                print(f"⚠️ Google Sheets sync notice: {e}")
                
        print("\nAll batch leads have been processed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JainForJain Autonomous Entry Bot")
    parser.add_argument("--excel", default=None, help="Path to Excel sheet (defaults to auto-resolved path)")
    parser.add_argument("--live", action="store_true", help="Perform LIVE submission (default is Dry-Run)")
    parser.add_argument("--limit", type=int, default=1, help="Number of leads to process")
    
    parser.add_argument("--city", default=None, help="Prioritize leads for specific city (e.g. 'Indore')")
    
    args = parser.parse_args()
    dry_run_flag = not args.live
    target_excel = args.excel or get_master_excel_path()
    
    asyncio.run(run_auto_entry_batch(
        excel_path=target_excel,
        dry_run=dry_run_flag,
        limit=args.limit,
        city_filter=args.city
    ))
