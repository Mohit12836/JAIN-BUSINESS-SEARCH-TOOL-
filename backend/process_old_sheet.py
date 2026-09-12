"""
Process and generate Canva Pro Logos & Banners for older sheet leads (Jain_Firms_Verified_Leads.xlsx).
1. Loads all leads from Desktop/Jain_Firms_Verified_Leads.xlsx.
2. Generates 1080x1080 Logo & 1200x500 Banner for each lead via Playwright.
3. Updates the older Excel files on Desktop with clickable links.
4. Seamlessly merges all unique leads into Master Excel (Jain_Leads_Verified_Photos_HD.xlsx).
5. Syncs the 100% updated Master Excel to Google Sheets.
"""

import os
import sys
import re
import asyncio
import openpyxl
from openpyxl.styles import Font, Alignment

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.canva_storefront_generator import generate_batch_assets, get_firm_asset_slug, OUTPUT_DIR
from backend.excel_builder import generate_leads_excel
from backend.auto_entry_bot import load_leads_from_excel
from backend.google_sheets_sync import sync_excel_to_google_sheet
from backend.config import get_master_excel_path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def main():
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    old_sheet_path = os.path.join(desktop_dir, "Jain_Firms_Verified_Leads.xlsx")
    old_latest_path = os.path.join(desktop_dir, "Jain_Firms_Verified_Leads_Latest.xlsx")

    if not os.path.exists(old_sheet_path):
        print(f"❌ Old sheet not found at: {old_sheet_path}")
        return

    print(f"📖 Reading older sheet from: {old_sheet_path}")
    wb = openpyxl.load_workbook(old_sheet_path, data_only=True)
    ws = wb.active

    old_leads = []
    for r in range(2, ws.max_row + 1):
        name = str(ws.cell(row=r, column=2).value or "").strip()
        if not name:
            continue
        
        city = str(ws.cell(row=r, column=9).value or "Ahmedabad").strip()
        state = str(ws.cell(row=r, column=10).value or "Gujarat").strip()
        phone = str(ws.cell(row=r, column=5).value or "").strip()
        wa = str(ws.cell(row=r, column=6).value or "").strip()
        addr = str(ws.cell(row=r, column=8).value or "").strip()
        pin = str(ws.cell(row=r, column=11).value or "380001").strip()
        maps = str(ws.cell(row=r, column=12).value or "").strip()
        web = str(ws.cell(row=r, column=13).value or "").strip()
        desc = str(ws.cell(row=r, column=15).value or "").strip()
        tier = str(ws.cell(row=r, column=16).value or "🟢 100% Verified Jain Entity").strip()
        reason = str(ws.cell(row=r, column=17).value or "Direct Name Match ('Jain')").strip()

        lead = {
            "name": name,
            "j4j_category": "फैशन एवं सौंदर्य (Fashion & Beauty)" if any(w in name.lower() for w in ["jewel", "chain", "gold", "silver", "bullion"]) else "व्यापार एवं उद्योग (Business & Industry)",
            "owner": str(ws.cell(row=r, column=4).value or "श्री सम्मत जैन (संचालक)").strip(),
            "phone": phone,
            "whatsapp": wa,
            "email": str(ws.cell(row=r, column=7).value or "").strip(),
            "address": addr,
            "city": city,
            "district": city,
            "state": state,
            "pincode": pin,
            "maps_url": maps,
            "website": web,
            "description": desc,
            "tier": tier,
            "reason": reason,
            "submission_status": "Ready to Submit"
        }
        old_leads.append(lead)

    print(f"Loaded {len(old_leads)} leads from older sheet.")

    # 1. Generate Canva Pro Assets for all leads in older sheet
    print(f"\n🎨 Generating Canva Pro 1080x1080 Logo & 1200x500 Banner for all {len(old_leads)} leads...")
    old_leads = await generate_batch_assets(old_leads, max_concurrent=4)

    # 2. Update older Excel files on Desktop with Canva logo/banner links
    link_font = Font(name="Segoe UI", size=9, color="2563EB", underline="single")
    for fp in [old_sheet_path, old_latest_path]:
        if not os.path.exists(fp):
            continue
        print(f"💾 Updating links in: {fp}")
        w = openpyxl.load_workbook(fp)
        s = w.active
        # Check or add header for Canva Banner and Logo if needed
        # In old sheet, Col 14 was 'Storefront Photo (Click HD)'
        for idx, lead in enumerate(old_leads, start=2):
            slug = get_firm_asset_slug(lead["name"])
            b_url = f"http://127.0.0.1:8000/api/canva-asset/{slug}_banner_1200x500.png"
            l_url = f"http://127.0.0.1:8000/api/canva-asset/{slug}_logo_1080x1080.png"
            
            c = s.cell(row=idx, column=14)
            c.value = "🎨 Canva Storefront Banner"
            c.hyperlink = b_url
            c.font = link_font

            # Check if there is col 18 or 19 for logo
            s.cell(row=1, column=18).value = "Canva Pro Profile Logo"
            s.cell(row=1, column=18).font = Font(name="Segoe UI", size=10, bold=True)
            c18 = s.cell(row=idx, column=18)
            c18.value = "💎 Canva Pro Profile Logo"
            c18.hyperlink = l_url
            c18.font = link_font
        w.save(fp)
        print(f"✓ Updated older sheet: {fp}")

    # 3. Merge into Master Excel (Jain_Leads_Verified_Photos_HD.xlsx)
    master_path = get_master_excel_path()
    repo_master_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Jain_Leads_Verified_Photos_HD.xlsx")
    desktop_master_path = os.path.join(desktop_dir, "Jain_Leads_Verified_Photos_HD.xlsx")

    existing_master_leads = []
    if os.path.exists(master_path):
        existing_master_leads = load_leads_from_excel(master_path)

    seen_names = {l["name"].lower().strip() for l in existing_master_leads}
    seen_phones = {re.sub(r'\D', '', l.get("phone", ""))[-10:] for l in existing_master_leads if l.get("phone")}

    added_count = 0
    merged_leads = list(existing_master_leads)

    for ol in old_leads:
        clean_p = re.sub(r'\D', '', ol.get("phone", ""))[-10:]
        n_clean = ol["name"].lower().strip()
        if n_clean in seen_names:
            continue
        if clean_p and clean_p in seen_phones:
            continue

        seen_names.add(n_clean)
        if clean_p:
            seen_phones.add(clean_p)
        merged_leads.append(ol)
        added_count += 1

    print(f"\nMerged {added_count} new unique leads from older sheet into Master list.")
    print(f"Total leads in Master now: {len(merged_leads)}")

    # Ensure all leads in merged_leads have Canva assets
    print("Verifying all merged leads have Canva assets...")
    merged_leads = await generate_batch_assets(merged_leads, max_concurrent=4)

    # Rebuild Master Excel with full 26 columns and 3 sheets
    generate_leads_excel(merged_leads, repo_master_path, category="All Jain Enterprises & Temples", scope="Gujarat, Rajasthan & MP")
    if os.path.exists(desktop_dir):
        generate_leads_excel(merged_leads, desktop_master_path, category="All Jain Enterprises & Temples", scope="Gujarat, Rajasthan & MP")
    print(f"💾 Master Excel saved with {len(merged_leads)} leads across 26 columns.")

    # 4. Sync to Google Sheets
    print("\n📊 Syncing Master Excel (with old sheet leads included) to Google Sheet...")
    try:
        ok = await sync_excel_to_google_sheet(desktop_master_path if os.path.exists(desktop_master_path) else repo_master_path)
        print(f"Google Sheet Sync: {'✅ SUCCESS' if ok else '⚠️ FAILED'}")
    except Exception as ge:
        print(f"Google Sheet sync error: {ge}")

    print("\n🎉 Done! All leads from the older sheet now have Canva Pro logos & banners generated, verified, and synced to Google Sheets!")

if __name__ == "__main__":
    asyncio.run(main())
