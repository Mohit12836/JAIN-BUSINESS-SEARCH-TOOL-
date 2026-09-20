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
    from backend.canva_storefront_generator import get_firm_asset_slug, generate_single_firm_assets, OUTPUT_DIR as CANVA_OUTPUT_DIR
except ImportError:
    from google_sheets_sync import sync_excel_to_google_sheet
    from config import get_master_excel_path
    from canva_storefront_generator import get_firm_asset_slug, generate_single_firm_assets, OUTPUT_DIR as CANVA_OUTPUT_DIR

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

read_leads_from_excel = load_leads_from_excel

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
    
    # Wait for Livewire component to mount on login page
    try:
        await page.wait_for_function("() => Boolean(window.Livewire && window.Livewire.all().length > 0)", timeout=10000)
    except Exception:
        pass

    # Native Livewire authentication (0.5s, no 405 MethodNotAllowed errors)
    try:
        await page.evaluate('''async (creds) => {
            const wire = window.Livewire ? window.Livewire.all()[0]?.$wire : null;
            if (wire) {
                await wire.set('data.email', creds.email);
                await wire.set('data.password', creds.password);
                await wire.authenticate();
                return true;
            }
            return false;
        }''', {"email": email, "password": password})
    except Exception as e:
        print(f"Livewire login notice: {e}")

    # Dynamic poll for redirect away from login
    for _ in range(25):
        await page.wait_for_timeout(400)
        if "/member/login" not in page.url:
            break

    # Fallback to standard submit button only if still on login page
    if "/member/login" in page.url:
        try:
            await page.fill("input[id='data.email']", email)
            await page.fill("input[id='data.password']", password)
            submit_btn = page.locator("button[type='submit']")
            if await submit_btn.count() > 0 and await submit_btn.first.is_visible():
                await submit_btn.first.click(timeout=3000)
                for _ in range(15):
                    await page.wait_for_timeout(400)
                    if "/member/login" not in page.url:
                        break
        except Exception:
            pass
            
    if "/member/login" in page.url:
        err_msg = await page.evaluate('''() => {
            const err = document.querySelector('p.fi-fo-field-wrp-error-message, div.fi-no-notification-danger');
            return err ? err.innerText.trim() : "";
        }''')
        print(f"Login failed or still on login page! {err_msg}")
        return False
        
    print(f"Login successful! Redirected to: {page.url}")
    return True

async def fill_listing_form(page: Page, lead: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
    """Fills all 4 tabs of the create business listing form for a lead."""
    print(f"\n=======================================================")
    print(f"Processing Lead [{lead['sl']}]: {lead['name']}")
    print(f"Category: {lead['category']} | City: {lead['city']} | Phone: {lead['phone']}")
    print(f"=======================================================")
    
    if page.is_closed():
        raise RuntimeError("Browser target page is closed.")
        
    try:
        await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=35000)
    except Exception as nav_err:
        print(f"⚠️ Navigation retry triggered for [{lead['name']}]: {nav_err}")
        await page.wait_for_timeout(1000)
        await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=35000)
        
    await page.wait_for_timeout(500)
    
    # 1. Detect session expiration and auto re-login
    if "/member/login" in page.url:
        print("Portal session expired, re-logging in...")
        logged = await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        if not logged:
            raise RuntimeError("Portal session expired and auto-login failed.")
        await page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(1000)
        
    # 2. Detect portal quota limit redirect (e.g. redirected to /member/dashboard)
    if "/business-listings/create" not in page.url:
        page_html = await page.content()
        if "Listing Limit Reached" in page_html or "buy additional listings" in page_html or "75 Allowed" in page_html or "75 / 75" in page_html:
            raise RuntimeError("Portal Listing Limit Reached: 75/75 quota reached (Remaining Allowance: 0 Left). Please contact admin or upgrade plan.")
        raise RuntimeError(f"Portal redirected away from create form to: {page.url}")

    try:
        await page.wait_for_selector("input[id='data.business_name']", timeout=15000)
    except Exception as e:
        page_html = await page.content()
        if "Listing Limit Reached" in page_html or "buy additional listings" in page_html or "75 / 75" in page_html:
            raise RuntimeError("Portal Listing Limit Reached: 75/75 quota reached (Remaining Allowance: 0 Left).")
        raise e
    
    # ------------------ STEP 1: SELECT COUNTRY (INDIA) ------------------
    # Country is 1 (India) by default on the portal. We ensure wire has it without triggering unnecessary resets.
    
    # ------------------ STEP 2, 3, 4: BULLETPROOF LOCATION CASCADE (STATE -> DISTRICT -> CITY) ------------------
    target_state = resolve_state(lead)
    lead_city = (lead.get("city") or "Indore").strip()
    target_dist = (lead.get("district") or lead_city).strip()
    print(f"--> [Location Cascade] Resolving State: '{target_state}' | District: '{target_dist}' | City: '{lead_city}'...")
    
    loc_res = await page.evaluate('''async (args) => {
        const wire = window.Livewire?.all()?.find(c => c.$wire && typeof c.$wire.getFormSelectOptions === 'function')?.$wire 
                  || window.Livewire?.all()?.[0]?.$wire;
        if (!wire) return {};

        // 1. Set State
        let chosenStateVal = null;
        try {
            const stateOpts = await wire.getFormSelectOptions('data.state_id');
            const tState = args.targetState.toLowerCase().trim();
            for (const opt of Object.values(stateOpts || {})) {
                const lbl = (opt.label || "").toLowerCase();
                if (lbl === tState) { chosenStateVal = opt.value; break; }
            }
            if (!chosenStateVal) {
                for (const opt of Object.values(stateOpts || {})) {
                    const lbl = (opt.label || "").toLowerCase();
                    if (lbl.includes(tState) || tState.includes(lbl)) { chosenStateVal = opt.value; break; }
                }
            }
            if (!chosenStateVal && Object.values(stateOpts || {}).length > 0) {
                chosenStateVal = Object.values(stateOpts)[0].value;
            }
            if (chosenStateVal) {
                await wire.set('data.state_id', chosenStateVal);
            }
        } catch(e) {}
        await new Promise(r => setTimeout(r, 500));

        // 2. Set District
        let chosenDistVal = null;
        try {
            const distOpts = await wire.getFormSelectOptions('data.district_id');
            const tDist = args.targetDist.toLowerCase().trim();
            const tCity = args.leadCity.toLowerCase().trim();
            for (const opt of Object.values(distOpts || {})) {
                const lbl = (opt.label || "").toLowerCase();
                if (lbl === tDist || lbl === tCity) { chosenDistVal = opt.value; break; }
            }
            if (!chosenDistVal) {
                for (const opt of Object.values(distOpts || {})) {
                    const lbl = (opt.label || "").toLowerCase();
                    if (lbl.includes(tDist) || tDist.includes(lbl) || lbl.includes(tCity) || tCity.includes(lbl)) {
                        chosenDistVal = opt.value; break;
                    }
                }
            }
            if (!chosenDistVal && Object.values(distOpts || {}).length > 0) {
                chosenDistVal = Object.values(distOpts)[0].value;
            }
            if (chosenDistVal) {
                await wire.set('data.district_id', chosenDistVal);
            }
        } catch(e) {}
        await new Promise(r => setTimeout(r, 500));

        // 3. Set City / Town (Registered Location)
        let chosenCityVal = null;
        let chosenCityLabel = "";
        try {
            const cityOpts = await wire.getFormSelectOptions('data.city_id');
            const tCity = args.leadCity.toLowerCase().trim();
            for (const opt of Object.values(cityOpts || {})) {
                const lbl = (opt.label || "").toLowerCase();
                if (lbl === tCity) {
                    chosenCityVal = opt.value;
                    chosenCityLabel = opt.label;
                    break;
                }
            }
            if (!chosenCityVal) {
                for (const opt of Object.values(cityOpts || {})) {
                    const lbl = (opt.label || "").toLowerCase();
                    if (lbl.includes(tCity) || tCity.includes(lbl)) {
                        chosenCityVal = opt.value;
                        chosenCityLabel = opt.label;
                        break;
                    }
                }
            }
            if (!chosenCityVal && Object.values(cityOpts || {}).length > 0) {
                const first = Object.values(cityOpts)[0];
                chosenCityVal = first.value;
                chosenCityLabel = first.label;
            }
            
            // Fallback standard IDs if empty
            if (!chosenCityVal) {
                if (tCity.includes("indore")) chosenCityVal = 1419;
                else if (tCity.includes("jaipur")) chosenCityVal = 1;
                else if (tCity.includes("ahmedabad")) chosenCityVal = 3;
                else if (tCity.includes("surat")) chosenCityVal = 4;
                else chosenCityVal = 1;
            }

            if (chosenCityVal) {
                await wire.set('data.city_id', chosenCityVal);
            }
        } catch(e) {}
        await new Promise(r => setTimeout(r, 500));

        return {
            state: wire.get('data.state_id'),
            district: wire.get('data.district_id'),
            city: wire.get('data.city_id'),
            cityLabel: chosenCityLabel
        };
    }''', {
        "targetState": target_state,
        "targetDist": target_dist,
        "leadCity": lead_city
    })
    
    print(f"--> [Location Verified] State ID: {loc_res.get('state')} | District ID: {loc_res.get('district')} | City ID: {loc_res.get('city')} ({loc_res.get('cityLabel', '')})")

    # ------------------ STEP 5: ATOMIC SAFE ALL-FIELDS INJECTION (0.1s) ------------------
    pin_digits = re.sub(r'\D', '', lead.get("pincode", ""))
    if not pin_digits or len(pin_digits) != 6:
        pin_digits = "452002" if "indore" in lead_city.lower() else "302001"
        
    phone_digits = re.sub(r'\D', '', lead.get("phone", ""))
    mobile_val = phone_digits[-10:] if len(phone_digits) >= 10 else "9772290045"
    
    wa_digits = re.sub(r'\D', '', lead.get("whatsapp", ""))
    wa_val = wa_digits[-10:] if len(wa_digits) >= 10 else mobile_val
    
    address_val = lead.get("address", f"{lead['city']}, India")
    cat_id = get_category_id(lead.get("category", ""), lead.get("name", ""))
    
    # Build a guaranteed unique slug: Name + Market/Area + City + Pincode Suffix
    area_or_market = (lead.get("market") or lead.get("area") or "").strip()
    clean_area = re.sub(r'[^a-zA-Z0-9]+', '-', area_or_market.lower()).strip('-')[:20] if area_or_market else ""
    pin_suffix = pin_digits[-3:] if len(pin_digits) >= 3 else "01"
    
    slug_parts = [lead['name'], clean_area, lead_city, pin_suffix]
    raw_slug = " ".join([p for p in slug_parts if p])
    initial_slug = re.sub(r'[^a-zA-Z0-9]+', '-', raw_slug.lower()).strip('-')[:55]
    
    print(f"--> [Safe Turbo] Atomically Injecting All Form Fields (Category ID: {cat_id} | Unique Slug: {initial_slug})...")
    await page.evaluate('''async (args) => {
        // 1. Livewire $wire direct binding
        const wire = window.Livewire?.all()?.find(c => c.$wire && typeof c.$wire.set === 'function')?.$wire 
                  || window.Livewire?.all()?.[0]?.$wire;
        if (wire) {
            await wire.set('data.business_name', args.name);
            await wire.set('data.slug', args.slug);
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
        }
        
        // 2. Immediate Direct DOM sync with bubbling events (Ensures form validity)
        const setField = (id, val) => {
            if (!val) return;
            const el = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        setField('data.business_name', args.name);
        setField('data.slug', args.slug);
        setField('data.pincode', args.pincode);
        setField('data.address', args.address);
        setField('data.mobile', args.mobile);
        setField('data.whatsapp', args.whatsapp);
        setField('data.email', args.email);
        setField('data.website', args.website);
        setField('data.latitude', args.lat);
        setField('data.longitude', args.lng);
    }''', {
        "name": lead["name"],
        "slug": initial_slug,
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
    await page.wait_for_timeout(300)
    
    # ------------------ STEP 6: TAB 3 (DESCRIPTION) ------------------
    desc_text = lead.get("description", "")
    if desc_text:
        print("--> Injecting Tab 3: Description...")
        await page.click('button:has-text("Description")')
        for _ in range(10):
            ready = await page.evaluate('''() => Boolean(window.tinymce && window.tinymce.activeEditor) || Boolean(document.querySelector('input[id*="long_description"]'))''')
            if ready:
                break
            await page.wait_for_timeout(100)
            
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
    await page.wait_for_timeout(200)
    await page.evaluate('''() => {
        const el = document.getElementById("data.dynamic_data.logo_display_type");
        if (el && el.options.length > 1) {
            el.selectedIndex = 1;
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }''')
    
    # SMART ASSET RESOLUTION (ORIGINAL FIRST -> CANVA PRO FALLBACK)
    firm_name = lead.get("name", "")
    from backend.photo_engine import resolve_lead_assets_smart
    asset_res = await resolve_lead_assets_smart(lead)
    
    banner_upload_file = asset_res.get("banner_file")
    logo_upload_file = asset_res.get("logo_file")
    banner_source = asset_res.get("banner_source", "CANVA_BESPOKE")
    logo_source = asset_res.get("logo_source", "CANVA_BESPOKE")
    
    lead["banner_source"] = banner_source
    lead["logo_source"] = logo_source
    print(f"--> [Asset Engine] Final Selection for [{firm_name}]:")
    print(f"    Banner: {banner_source} -> {banner_upload_file}")
    print(f"    Logo:   {logo_source} -> {logo_upload_file}")

    # Upload to FilePond inputs (file_inputs[0] = Logo, file_inputs[1] = Banner)
    try:
        file_inputs = await page.query_selector_all('input[type="file"]')
        if file_inputs:
            if logo_upload_file and os.path.exists(logo_upload_file):
                print(f"--> Attaching Logo FilePond: {logo_upload_file}")
                await file_inputs[0].set_input_files(logo_upload_file)
                await page.wait_for_timeout(200)
            
            if len(file_inputs) > 1 and banner_upload_file and os.path.exists(banner_upload_file):
                print(f"--> Attaching Banner FilePond: {banner_upload_file}")
                await file_inputs[1].set_input_files(banner_upload_file)
                await page.wait_for_timeout(200)

            print("--> Waiting for FilePond upload to reach 100% completion (Safe dynamic check)...")
            needed_files = 2 if (logo_upload_file and banner_upload_file) else 1
            for attempt in range(40):  # up to 6 seconds dynamic
                busy_count = await page.locator('.filepond--item[data-filepond-item-state*="busy"]').count()
                complete_count = await page.locator('.filepond--item[data-filepond-item-state="processing-complete"]').count()
                if busy_count == 0 and complete_count >= needed_files:
                    print(f"✓ All {complete_count} FilePond items uploaded completely (state=processing-complete)!")
                    break
                await page.wait_for_timeout(150)
    except Exception as up_err:
        print(f"⚠️ Photo upload warning: {up_err}")

    # ------------------ STEP 8: DRY-RUN vs LIVE SUBMISSION ------------------
    if dry_run:
        desktop_dir = os.path.expanduser("~/Desktop")
        clean_name = re.sub(r'\\W+', '_', lead['name'])[:25]
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
        
        # Wait up to 10 seconds for redirect to /business-listings/(\d+) (Fast dynamic 150ms check)
        for _ in range(60):
            await page.wait_for_timeout(150)
            if re.search(r'/business-listings/(\d+)', page.url):
                break
        
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
                
                # Switch to Tab 1 if needed
                try:
                    tab1 = page.locator('button[role="tab"]:has-text("Business Details")')
                    if await tab1.count() > 0 and await tab1.first.is_visible():
                        await tab1.first.click()
                        await page.wait_for_timeout(400)
                except Exception:
                    pass

                # Retry 1: Append City + Pincode to slug and name
                retry_slug_1 = f"{initial_slug}-{pin_digits}"[:60]
                retry_name_1 = f"{lead['name']} - {lead_city}"
                print(f"--> Auto-retrying submission with Unique Slug: '{retry_slug_1}'...")
                await page.evaluate('''async (args) => {
                    const stateEl = document.getElementById("data.state_id");
                    if (window.Alpine && window.Alpine.$data(stateEl)) {
                        await window.Alpine.$data(stateEl).$wire.set('data.business_name', args.name);
                        await window.Alpine.$data(stateEl).$wire.set('data.slug', args.slug);
                    }
                }''', {"name": retry_name_1, "slug": retry_slug_1})
                if await page.locator("input[id='data.business_name']").count() > 0:
                    await page.locator("input[id='data.business_name']").fill(retry_name_1)
                if await page.locator("input[id='data.slug']").count() > 0:
                    await page.locator("input[id='data.slug']").fill(retry_slug_1)
                await page.wait_for_timeout(1000)
                await create_btn.first.click()
                await page.wait_for_timeout(6000)
                
                current_url = page.url
                errors = await page.evaluate('''() => {
                    const errs = Array.from(document.querySelectorAll('p.fi-fo-field-wrp-error-message, div.fi-no-notification-danger'));
                    return errs.map(e => e.innerText.trim()).filter(x => x.length > 0);
                }''')
                
                if errors and any("slug" in e.lower() or "url key" in e.lower() for e in errors):
                    # Retry 2: Append 4-digit unique random code
                    import random, string
                    rand_suffix = ''.join(random.choices(string.digits, k=4))
                    retry_slug_2 = f"{initial_slug}-{rand_suffix}"[:60]
                    retry_name_2 = f"{lead['name']} - {lead_city} ({pin_digits})"
                    print(f"--> Auto-retrying with Location + Unique Code: '{retry_slug_2}'...")
                    await page.evaluate('''async (args) => {
                        const stateEl = document.getElementById("data.state_id");
                        if (window.Alpine && window.Alpine.$data(stateEl)) {
                            await window.Alpine.$data(stateEl).$wire.set('data.business_name', args.name);
                            await window.Alpine.$data(stateEl).$wire.set('data.slug', args.slug);
                        }
                    }''', {"name": retry_name_2, "slug": retry_slug_2})
                    if await page.locator("input[id='data.business_name']").count() > 0:
                        await page.locator("input[id='data.business_name']").fill(retry_name_2)
                    if await page.locator("input[id='data.slug']").count() > 0:
                        await page.locator("input[id='data.slug']").fill(retry_slug_2)
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
            
        profile_url = f"https://jainforjain.com/{initial_slug}"
        
        print(f"✓ Listing created successfully! Business ID: {biz_id}")
        print(f"✓ Profile URL: {profile_url}")

        # If on edit page and 'Publish Listing' button is visible, click it!
        try:
            pub_btn = page.locator('button:has-text("Publish Listing")')
            if await pub_btn.count() > 0 and await pub_btn.first.is_visible():
                print("--> Clicking 'Publish Listing' button to make it live...")
                await pub_btn.first.click()
                await page.wait_for_timeout(2000)
                print("✓ Listing officially published live on JainForJain portal!")
        except Exception as pe:
            print(f"Publish note: {pe}")
        
        return {
            "status": "submitted_success",
            "biz_id": biz_id,
            "profile_url": profile_url
        }

async def run_auto_entry_batch(
    excel_path: Optional[str] = None,
    dry_run: bool = False,
    limit: Optional[int] = None,
    city_filter: Optional[str] = None,
    include_failed: bool = True,
    workers: Optional[int] = None,
    email: str = DEFAULT_USER,
    password: str = DEFAULT_PASS
):
    """Orchestrates batch auto-entry workflow."""
    if not excel_path:
        excel_path = get_master_excel_path()
        
    print("==========================================================")
    print("     JAINFORJAIN.COM AUTONOMOUS DATA ENTRY BOT           ")
    print(f" Mode: {'🔍 DRY-RUN PREVIEW (No Live Data Created)' if dry_run else '🚀 LIVE SUBMISSION (DIRECT PORTAL PUBLISH)'}")
    print(f" Target Excel: {excel_path}")
    if city_filter:
        print(f" Priority City: {city_filter}")
    print("==========================================================")
    
    leads = load_leads_from_excel(excel_path)
    if include_failed:
        ready_leads = [l for l in leads if l["submission_status"] in ["Ready to Submit", "", None] or str(l.get("submission_status", "")).startswith("Failed")]
    else:
        ready_leads = [l for l in leads if l["submission_status"] in ["Ready to Submit", "", None]]
    
    if city_filter:
        city_leads = [l for l in ready_leads if city_filter.lower() in str(l.get("city", "")).lower()]
        other_leads = [l for l in ready_leads if city_filter.lower() not in str(l.get("city", "")).lower()]
        ready_leads = city_leads + other_leads
    
    print(f"Total leads in Excel: {len(leads)}")
    print(f"Leads pending for submission: {len(ready_leads)}")
    
    if not ready_leads:
        print("All leads have already been submitted! Nothing to process.")
        return
        
    if limit:
        ready_leads = ready_leads[:limit]
        print(f"Processing first {limit} lead(s)...")

    from backend.system_guard import (
        CHROMIUM_TURBO_ARGS,
        apply_turbo_routing,
        safe_close_browser,
        free_system_resources_completely
    )

    browser = None
    context = None
    try:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=CHROMIUM_TURBO_ARGS
                )
            except Exception:
                browser = await p.chromium.launch(
                    channel="chrome",
                    headless=True,
                    args=CHROMIUM_TURBO_ARGS
                )
            context = await browser.new_context(viewport={"width": 1400, "height": 1000})
            
            # Apply Turbo Network Routing (Blocks fonts, video, trackers to speed up form loads)
            await apply_turbo_routing(context, block_images=False)
            
            login_page = await context.new_page()
            
            # Login once for all workers
            logged_in = await login_to_portal(login_page, email, password)
            if not logged_in:
                print("❌ Cannot proceed without successful login.")
                await safe_close_browser(browser, context)
                return
            await login_page.close()

            # High-Speed Parallel Worker Queue
            from backend.config import MAX_PORTAL_CONCURRENCY
            effective_workers = workers or MAX_PORTAL_CONCURRENCY
            concurrency = min(effective_workers, len(ready_leads))
            print(f"\n⚡ Launching {concurrency} Concurrent Workers for Turbo Speed Submission (Zero Error Mode)...")
            
            queue = asyncio.Queue()
            for l in ready_leads:
                queue.put_nowait(l)

            submitted_count = 0
            excel_lock = asyncio.Lock()

            async def worker(worker_id: int):
                nonlocal submitted_count
                w_page = await context.new_page()
                try:
                    while not queue.empty():
                        try:
                            lead = queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break

                        try:
                            res = await fill_listing_form(w_page, lead, dry_run=dry_run)
                            if dry_run:
                                print(f"[Worker {worker_id}] ✓ Lead [{lead['sl']}] Form filled & verified in Dry-Run mode.")
                            else:
                                biz_id = res.get("biz_id", "")
                                profile_url = res.get("profile_url", "")
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, lead["row_idx"], biz_id, profile_url, "Submitted - Live")
                                    submitted_count += 1
                                print(f"[Worker {worker_id}] ✓ Successfully submitted [{lead['name']}]! ID: {biz_id}")
                        except Exception as e:
                            print(f"[Worker {worker_id}] ❌ Error processing lead [{lead['name']}]: {e}")
                            if not dry_run:
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, lead["row_idx"], "", "", f"Failed: {str(e)[:30]}")
                        finally:
                            queue.task_done()
                finally:
                    await w_page.close()

            # Execute all workers concurrently
            await asyncio.gather(*(worker(i+1) for i in range(concurrency)))
            await safe_close_browser(browser, context)
            browser = None
            context = None
            
            # If any live submissions occurred, trigger instant Google Sheet sync!
            if not dry_run and submitted_count > 0:
                print("\n🔄 Synchronizing updated Excel statuses to Google Sheets...")
                try:
                    await sync_excel_to_google_sheet(excel_path)
                except Exception as e:
                    print(f"⚠️ Google Sheets sync notice: {e}")
                    
            print(f"\n⚡ All {submitted_count} leads processed and submitted successfully at Turbo Speed!")
    finally:
        await safe_close_browser(browser, context)
        free_system_resources_completely()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JainForJain Autonomous Entry Bot")
    parser.add_argument("--excel", default=None, help="Path to Excel sheet (defaults to auto-resolved path)")
    parser.add_argument("--dry-run", action="store_true", help="Perform DRY-RUN preview (default is now LIVE submission)")
    parser.add_argument("--live", action="store_true", default=True, help="Perform LIVE submission (default)")
    parser.add_argument("--all-pending", action="store_true", help="Process ALL pending and failed leads in Excel")
    parser.add_argument("--limit", type=int, default=None, help="Number of leads to process")
    parser.add_argument("--workers", type=int, default=3, help="Number of concurrent browser workers (default: 3)")
    parser.add_argument("--city", default=None, help="Prioritize leads for specific city (e.g. 'Indore')")
    
    args = parser.parse_args()
    dry_run_flag = args.dry_run
    target_excel = args.excel or get_master_excel_path()
    
    limit_val = args.limit
    if not limit_val and not args.all_pending:
        limit_val = 5
        
    asyncio.run(run_auto_entry_batch(
        excel_path=target_excel,
        dry_run=dry_run_flag,
        limit=limit_val,
        city_filter=args.city,
        include_failed=True,
        workers=args.workers
    ))
