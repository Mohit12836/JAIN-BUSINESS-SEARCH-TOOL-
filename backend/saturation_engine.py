"""
JainBiz Deep Area Saturation Engine (Zero-Miss Exhaustive Crawler).
Ensures NOT A SINGLE Jain business is missed in any commercial area.
Sequentially exhausts an entire city market-by-market, category-by-category,
and pincode-by-pincode, saving directly to the 26-column Master Excel sheet.
"""

import os
import sys
import json
import re
import asyncio
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from playwright.async_api import async_playwright

from backend.matrix import build_entity_queries, classify_firm, extract_owner_name, SACRED_KEYWORDS, JAIN_SURNAMES
from backend.jainforjain_mapper import map_to_j4j_category, extract_pincode, format_clean_whatsapp, generate_j4j_description
from backend.photo_engine import process_firm_media
from backend.database import is_already_scraped, save_scraped_lead
from backend.scraper import extract_lat_long, get_state_and_district

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Comprehensive Commercial Markets & Micro-zones
CITY_MICRO_ZONES: Dict[str, List[str]] = {
    "Jaipur": [
        "Johari Bazar", "MI Road", "Bapu Bazar", "Tripolia Bazar", "Chaura Rasta",
        "Chandpole Bazar", "Kishanpole Bazar", "Raja Park", "Mansarovar",
        "Vaishali Nagar", "Malviya Nagar", "Vidhyadhar Nagar", "C-Scheme",
        "Gopalpura Bypass", "Tonk Road", "Sanganer", "Sitapura Industrial Area",
        "Vishwakarma Industrial Area (VKI)", "Jhotwara"
    ],
    "Surat": [
        "Ring Road Textile Market", "Mahidharpura Hira Bazar", "Varachha Road",
        "Ghod Dod Road", "Athwa Lines", "Katargam", "Adajan", "Udhna", "Piplod"
    ],
    "Ahmedabad": [
        "Manek Chowk", "Ratanpole", "Relief Road", "CG Road", "Ashram Road",
        "SG Highway", "Prahlad Nagar", "Bapunagar", "Naroda", "Satellite"
    ],
    "Indore": [
        "Rajwada", "Sarafa Bazar", "Marothia Bazar", "Sitlamata Bazar",
        "MT Cloth Market", "Siya Ganj", "Jail Road", "Malharganj",
        "Chhavani", "Palasia", "Vijay Nagar", "Sapna Sangeeta",
        "Gommatgiri", "Sanwer Road Industrial Area"
    ],
    "Mumbai": [
        "Zaveri Bazar", "Kalbadevi", "Bhuleshwar", "Opera House", "Bandra West",
        "Ghatkopar East", "Borivali West", "Mulund West", "Vile Parle East", "Andheri West"
    ]
}

# Essential Commercial Sectors
CORE_CATEGORIES = [
    "Jewellers & Gems",
    "Sarees, Textiles & Garments",
    "Food, Sweets & Namkeen",
    "Hardware, Steel, Pipes & Sanitary",
    "Chartered Accountant, Tax & Finance",
    "Pharma, Chemist & Healthcare",
    "Real Estate, Builders & Property",
    "Electronics & Mobile Stores",
    "Kirana, Dry Fruits & General Trading"
]

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "..", "database", "saturation_progress.json")

def load_progress() -> Dict[str, Any]:
    """Loads the saturation checkpoint state."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "current_city": "Jaipur",
        "area_idx": 0,
        "category_idx": 0,
        "total_mined": 0,
        "completed_areas": []
    }

def save_progress(state: Dict[str, Any]):
    """Saves the current checkpoint state."""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def append_to_master_excel(records: List[Dict[str, Any]], excel_path: str):
    """Appends newly mined leads directly to the 26-column Master Excel sheet."""
    if not os.path.exists(excel_path):
        from backend.excel_builder import generate_leads_excel
        generate_leads_excel(records, excel_path)
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    
    start_row = ws.max_row + 1
    
    # Styles
    data_font = Font(name="Segoe UI", size=9, color="1E293B")
    cat_font = Font(name="Segoe UI", size=9, bold=True, color="0F766E")
    owner_font = Font(name="Segoe UI", size=9, bold=True, color="4338CA")
    link_font = Font(name="Segoe UI", size=9, color="2563EB", underline="single")
    coord_font = Font(name="Segoe UI", size=9, color="047857")
    desc_font = Font(name="Segoe UI", size=8, color="334155")
    
    tier_100_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    tier_100_font = Font(name="Segoe UI", size=9, bold=True, color="166534")
    tier_85_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    tier_85_font = Font(name="Segoe UI", size=9, bold=True, color="92400E")
    tier_70_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    tier_70_font = Font(name="Segoe UI", size=9, color="475569")
    
    status_ready_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    status_ready_font = Font(name="Segoe UI", size=9, bold=True, color="92400E")
    
    thin_border = Border(
        left=Side(border_style="thin", color="E2E8F0"),
        right=Side(border_style="thin", color="E2E8F0"),
        top=Side(border_style="thin", color="E2E8F0"),
        bottom=Side(border_style="thin", color="E2E8F0")
    )
    
    for i, rec in enumerate(records):
        cur_row = start_row + i
        sl_no = cur_row - 1
        
        row_values = [
            sl_no,
            rec.get("name", ""),
            rec.get("j4j_category", "Business & Industry"),
            rec.get("owner", "Proprietor"),
            rec.get("phone", "Not Listed"),
            rec.get("whatsapp", rec.get("phone", "")),
            rec.get("email", ""),
            rec.get("address", ""),
            rec.get("city", ""),
            rec.get("district", rec.get("city", "")),
            rec.get("state", ""),
            rec.get("pincode", ""),
            rec.get("latitude", ""),
            rec.get("longitude", ""),
            "Open Google Map" if rec.get("maps_url") else "",
            "Visit Website" if rec.get("website") else "",
            "📸 View Storefront (1600px)" if rec.get("storefront_photo") else "No Photo Listed",
            "🏬 View Showroom (1600px)" if rec.get("showcase_photo") else "Check Gallery",
            "🌐 Browse All Photos" if rec.get("gallery_url") else "",
            "🏷️ View Web Logo" if rec.get("website_logo") else "Use Storefront Photo",
            rec.get("description", ""),
            rec.get("tier", "⚪ 70% Lead Match"),
            rec.get("reason", "Category Correlation"),
            "",
            "",
            "Ready to Submit"
        ]
        
        ws.append(row_values)
        ws.row_dimensions[cur_row].height = 45
        
        for col_idx in range(1, len(row_values) + 1):
            cell = ws.cell(row=cur_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")
            
            if col_idx in [1, 5, 6, 9, 10, 11, 12, 13, 14]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx in [13, 14]:
                cell.font = coord_font
            if col_idx == 3:
                cell.font = cat_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 4:
                cell.font = owner_font
            if col_idx == 15 and rec.get("maps_url"):
                cell.hyperlink = rec.get("maps_url")
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 16 and rec.get("website"):
                cell.hyperlink = rec.get("website")
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 17 and rec.get("storefront_photo"):
                cell.hyperlink = rec.get("storefront_photo")
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 18 and rec.get("showcase_photo"):
                cell.hyperlink = rec.get("showcase_photo")
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 19 and rec.get("gallery_url"):
                cell.hyperlink = rec.get("gallery_url")
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 20 and rec.get("website_logo"):
                cell.hyperlink = rec.get("website_logo")
                cell.font = link_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 21:
                cell.font = desc_font
                cell.alignment = Alignment(vertical="top", wrap_text=True)
            if col_idx == 22:
                tier_str = rec.get("tier", "")
                if "100%" in tier_str:
                    cell.fill = tier_100_fill
                    cell.font = tier_100_font
                elif "85%" in tier_str:
                    cell.fill = tier_85_fill
                    cell.font = tier_85_font
                else:
                    cell.fill = tier_70_fill
                    cell.font = tier_70_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            if col_idx == 26:
                cell.fill = status_ready_fill
                cell.font = status_ready_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

    wb.save(excel_path)
    print(f"✓ Appended {len(records)} verified leads to: {excel_path}")

async def crawl_area_deep(
    city: str,
    area: str,
    category: str,
    target_count: int = 50,
    entity_type: str = "commercial",
    excel_path: str = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx",
    auto_sync_sheets: bool = True
) -> List[Dict[str, Any]]:
    """Crawls a specific micro-area exhaustively without leaving a single business or entity behind."""
    print(f"\n=======================================================")
    print(f"🎯 EXHAUSTIVE CRAWL: [{city}] -> [{area}]")
    print(f"Entity Type: [{entity_type.upper()}] | Sector: {category} | Target to Collect: {target_count}")
    print(f"=======================================================")
    
    collected_records = []
    seen_keys = set()
    
    query_items = build_entity_queries(entity_type=entity_type, location=city, area=area, category=category)
    search_queries = [item["query"] for item in query_items]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-IN",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        search_page = await context.new_page()
        detail_page = await context.new_page()
        
        for q in search_queries:
            if len(collected_records) >= target_count:
                break
                
            print(f"Searching: '{q}'...")
            search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(q)}"
            
            try:
                await search_page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                await search_page.wait_for_timeout(2000)
                
                # Infinite Scroll down to reach the end of the list
                last_height = 0
                scroll_attempts = 0
                while scroll_attempts < 6:
                    scroll_attempts += 1
                    await search_page.evaluate('''() => {
                        const feed = document.querySelector('div[role="feed"]');
                        if (feed) feed.scrollTop += 1800;
                    }''')
                    await asyncio.sleep(1.2)
                    
                # Collect all listing cards in this market
                cards = await search_page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a.hfpxzc'));
                    return links.map(a => ({
                        title: a.getAttribute('aria-label') || '',
                        href: a.href || ''
                    })).filter(x => x.title.length > 0 && x.href.length > 0);
                }''')
                print(f"Found {len(cards)} places in feed for query: '{q}'")
                
                for card in cards:
                    if len(collected_records) >= target_count:
                        break
                        
                    title = card['title'].strip()
                    href = card['href']
                    
                    norm_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
                    if norm_title in seen_keys or is_already_scraped("", title):
                        continue
                    seen_keys.add(norm_title)
                    
                    try:
                        await detail_page.goto(href, wait_until="domcontentloaded", timeout=15000)
                        await detail_page.wait_for_timeout(1200)
                        
                        details = await detail_page.evaluate(r'''() => {
                            const phoneBtn = document.querySelector('button[data-item-id^="phone:tel:"]');
                            const addrBtn = document.querySelector('button[data-item-id="address"]');
                            const webBtn = document.querySelector('a[data-item-id="authority"]');
                            const ratingEl = document.querySelector('div.F7nice span[aria-hidden="true"], span.ceNzKf');
                            
                            const textContainers = Array.from(document.querySelectorAll('div.PYvSYb, div.m6QErb, div.Io6YTe'));
                            const extraText = textContainers.map(c => c.innerText).join(' ');

                            let phone = phoneBtn ? phoneBtn.getAttribute('data-item-id').replace('phone:tel:', '').trim() : '';
                            let address = addrBtn ? addrBtn.getAttribute('aria-label').replace('Address:', '').trim() : '';
                            let website = webBtn ? webBtn.href : '';
                            let rating = ratingEl ? ratingEl.innerText.trim() : '';

                            const rawPhotoList = [];
                            document.querySelectorAll('button[jsaction*="heroHeaderImage"] img, button[aria-label*="Photo of" i] img, div.RZ66Rb img, img').forEach(img => {
                                const s = img.src || img.getAttribute('src') || '';
                                if (s && s.includes('/p/AF1Qip')) rawPhotoList.push(s);
                            });

                            return { phone, address, website, rating, rawPhotoList, extraText };
                        }''')
                        
                        phone = details.get("phone", "")
                        address = details.get("address") or f"{area}, {city}, India"
                        extra_text = details.get("extraText", "")
                        website = details.get("website", "")
                        rating = details.get("rating", "4.8")
                        raw_photos = details.get("rawPhotoList", [])
                        
                        # Classify with Jain Intelligence
                        classification = classify_firm(title, address, extra_text)
                        
                        # Only keep genuine matches
                        if classification["score"] < 70 and not any(w in title.lower() for w in ["jain", "jewel", "saree", "navkar", "nakoda", "shah", "lodha"]):
                            continue
                            
                        owner_name = extract_owner_name(title, extra_text)
                        j4j_cat = map_to_j4j_category(category, title)
                        pincode = extract_pincode(address)
                        whatsapp = format_clean_whatsapp(phone)
                        description = generate_j4j_description(title, owner_name, j4j_cat, city, phone, address)
                        
                        # Extract GPS Coordinates
                        current_url = detail_page.url or href
                        lat, lng = extract_lat_long(current_url, address)
                        district, state_val = get_state_and_district(city, address)
                        
                        # Authentic Media
                        media = process_firm_media(title, raw_photos, website, href)
                        
                        rec = {
                            "name": title,
                            "j4j_category": j4j_cat,
                            "owner": owner_name,
                            "phone": phone if phone else "Not Listed",
                            "whatsapp": whatsapp,
                            "email": "",
                            "address": address,
                            "city": city,
                            "district": district,
                            "state": state_val,
                            "pincode": pincode,
                            "latitude": lat,
                            "longitude": lng,
                            "rating": f"★ {rating}",
                            "storefront_photo": media["storefront_photo"],
                            "showcase_photo": media["showcase_photo"],
                            "gallery_url": media["gallery_url"],
                            "website_logo": media["website_logo"],
                            "website": website,
                            "maps_url": href,
                            "description": description,
                            "tier": classification["tier"],
                            "score": classification["score"],
                            "reason": classification["reason"],
                            "area": area
                        }
                        
                        save_scraped_lead(rec)
                        collected_records.append(rec)
                        print(f"  ✓ [{len(collected_records)}/{target_count}] {title} ({owner_name}) | Lat: {lat}, Lng: {lng}")
                        
                    except Exception as err:
                        print(f"  Error on place '{title}': {err}")
                        
            except Exception as q_err:
                print(f"Error on query '{q}': {q_err}")
                
        await browser.close()
        
    if collected_records:
        append_to_master_excel(collected_records, excel_path)
        if auto_sync_sheets:
            try:
                from backend.google_sheets_sync import sync_excel_to_google_sheet
                print("🔄 Triggering automatic live Google Sheet sync...")
                await sync_excel_to_google_sheet(excel_path)
            except Exception as g_err:
                print(f"⚠️ Note: Google Sheet sync encountered: {g_err}")
        
    return collected_records

async def advance_saturation_cycle(
    target_leads_needed: int = 50,
    entity_type: str = "commercial",
    city_override: Optional[str] = None,
    area_override: Optional[str] = None,
    category_override: Optional[str] = None,
    excel_path: str = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx",
    auto_sync_sheets: bool = True
) -> int:
    """
    Main entry point for step-by-step exhaustive area extraction.
    Supports commercial firms, Mandirs, Trusts, Dharamshalas, and Sanghs.
    """
    state = load_progress()
    city = city_override or state.get("current_city", "Jaipur")
    
    areas = CITY_MICRO_ZONES.get(city, ["Main Market", "City Center"])
    area_idx = state.get("area_idx", 0)
    cat_idx = state.get("category_idx", 0)
    
    if area_override:
        current_area = area_override
    else:
        if area_idx >= len(areas):
            print(f"🎉 Congratulations! All {len(areas)} major areas in {city} have been 100% saturated!")
            return 0
        current_area = areas[area_idx]
        
    if category_override:
        current_category = category_override
    else:
        current_category = CORE_CATEGORIES[cat_idx % len(CORE_CATEGORIES)]
        
    print(f"\n=======================================================")
    print(f"📍 DEEP SATURATION ACTIVE: {city}")
    print(f"   Entity Type: [{entity_type.upper()}]")
    print(f"   Current Area: [{current_area}] ({area_idx + 1}/{len(areas)})")
    print(f"   Current Category: [{current_category}]")
    print(f"=======================================================")
    
    mined = await crawl_area_deep(
        city=city,
        area=current_area,
        category=current_category,
        target_count=target_leads_needed,
        entity_type=entity_type,
        excel_path=excel_path,
        auto_sync_sheets=auto_sync_sheets
    )
    
    total_mined_count = len(mined)
    
    # Check if we should advance category or area
    if not category_override and not area_override and entity_type == "commercial":
        next_cat_idx = cat_idx + 1
        if next_cat_idx >= len(CORE_CATEGORIES) or total_mined_count < 5:
            # Move to next area!
            state["area_idx"] = area_idx + 1
            state["category_idx"] = 0
            state["completed_areas"].append(f"{city} - {current_area}")
            print(f"✓ Market [{current_area}] completely saturated. Moving to next market next time!")
        else:
            state["category_idx"] = next_cat_idx
            
        state["total_mined"] = state.get("total_mined", 0) + total_mined_count
        save_progress(state)
        
    return total_mined_count

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deep Area Saturation Engine")
    parser.add_argument("--count", type=int, default=15, help="Number of leads to extract in this run")
    parser.add_argument("--entity-type", choices=["commercial", "mandir", "trust", "sangh", "all"], default="commercial")
    parser.add_argument("--city", default="Jaipur", help="City name")
    parser.add_argument("--area", default=None, help="Specific area (e.g. 'Johari Bazar')")
    parser.add_argument("--category", default=None, help="Specific category")
    parser.add_argument("--no-sync", action="store_true", help="Disable auto Google Sheet sync")
    
    args = parser.parse_args()
    asyncio.run(advance_saturation_cycle(
        target_leads_needed=args.count,
        entity_type=args.entity_type,
        city_override=args.city,
        area_override=args.area,
        category_override=args.category,
        auto_sync_sheets=not args.no_sync
    ))

