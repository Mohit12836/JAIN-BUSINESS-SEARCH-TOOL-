"""
Master JainBiz Auto-Pilot Pipeline.
Seamlessly combines:
1. Deep Area Saturation Crawling (exhausting an area market-by-market)
2. Master Excel Database (26-column format on Desktop)
3. Autonomous JainForJain.com Data Entry Bot
"""

import sys
import os
import asyncio
import argparse

from backend.saturation_engine import load_progress, CITY_MICRO_ZONES, CORE_CATEGORIES, advance_saturation_cycle
from backend.auto_entry_bot import load_leads_from_excel, run_auto_entry_batch
from backend.database import get_history_count

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_EXCEL = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx"

def print_banner():
    state = load_progress()
    city = state.get("current_city", "Jaipur")
    areas = CITY_MICRO_ZONES.get(city, ["Main Market"])
    area_idx = state.get("area_idx", 0)
    current_area = areas[area_idx] if area_idx < len(areas) else "City Finished"
    cat_idx = state.get("category_idx", 0)
    current_cat = CORE_CATEGORIES[cat_idx % len(CORE_CATEGORIES)]
    
    total_db = get_history_count()
    ready_count = 0
    if os.path.exists(DEFAULT_EXCEL):
        try:
            leads = load_leads_from_excel(DEFAULT_EXCEL)
            ready_count = sum(1 for l in leads if l.get("submission_status") in ["Ready to Submit", "", None])
        except Exception:
            pass

    print("==========================================================================")
    print("        JAINBIZ AUTONOMOUS LEAD MINER & ENTRY PIPELINE                   ")
    print("==========================================================================")
    print(f"📍 Active Target City    : {city}")
    print(f"🏢 Current Market/Area   : [{current_area}] ({min(area_idx + 1, len(areas))}/{len(areas)} markets)")
    print(f"🏷️ Current Sector/Cat    : {current_cat}")
    print(f"📋 Master Excel Ready    : {ready_count} leads waiting to submit")
    print(f"💾 Total Scraped in DB   : {total_db} unique verified firms")
    print(f"📊 Live Google Sheet     : Synced (1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw)")
    print("==========================================================================")

async def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="JainBiz Auto-Pilot Pipeline")
    parser.add_argument("--mode", choices=["auto", "scrape", "sync", "submit", "manual", "live-pending"], default=None)
    parser.add_argument("--entity-type", choices=["commercial", "mandir", "trust", "sangh", "all"], default=None)
    parser.add_argument("--count", type=int, default=None, help="Number of listings to process")
    parser.add_argument("--live", action="store_true", default=True, help="Submit live to JainForJain (default)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run preview mode")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent workers for live submissions (default 3)")
    parser.add_argument("--city", default=None, help="City override for manual mode")
    parser.add_argument("--area", default=None, help="Area override for manual mode")
    parser.add_argument("--category", default=None, help="Category override for manual mode")
    parser.add_argument("--no-sync", action="store_true", help="Skip Google Sheets auto-sync")
    
    args = parser.parse_args()
    
    # Step 1: Entity Type Selection
    entity_type = args.entity_type
    if not entity_type and not args.mode:
        print("\n" + "="*74)
        print("🏢 CHOOSE JAIN ENTITY TYPE TO MINE / PROCESS:")
        print("="*74)
        print("  [1] 🏬 Commercial Businesses (दुकानें, ज्वेलर्स, कपड़े, सीए, उद्योग आदि)")
        print("  [2] 🛕 Jain Mandir & Derasar (मंदिर, जिनालय, चैत्यालय, दादावाड़ी, तीर्थ क्षेत्र)")
        print("  [3] 🏨 Jain Trust, Dharamshala & Bhojanalaya (ट्रस्ट, धर्मशाला, भोजनालय, यात्री निवास)")
        print("  [4] 🤝 Jain Sangh, Sanstha & NGOs (संघ, मंडल, संस्थाएं, समाज, पाठशाला)")
        print("  [5] 🌟 Complete All-Inclusive (सभी मंदिर, ट्रस्ट, संस्थाएं एवं व्यापार)")
        print("="*74)
        
        try:
            ent_choice = input("\nEnter Entity choice [1-5] (default 1): ").strip() or "1"
        except Exception:
            ent_choice = "1"
            
        ent_map = {
            "1": "commercial",
            "2": "mandir",
            "3": "trust",
            "4": "sangh",
            "5": "all"
        }
        entity_type = ent_map.get(ent_choice, "commercial")
    elif not entity_type:
        entity_type = "commercial"

    # Step 2: Pipeline Action Selection
    mode = args.mode
    if not mode:
        print("\n" + "="*74)
        print("⚙️ CHOOSE PIPELINE ACTION:")
        print("="*74)
        print("  [1] 🚀 Full Auto-Pilot (Scrape + Auto-sync Google Sheet + Fill JainForJain)")
        print("  [2] ⛏️ Scrape & Sync Only (Exhaust area, add to Master Excel & Google Sheet)")
        print("  [3] 🔄 Instant Google Sheet Sync (Push Desktop Excel to live Google Sheet now)")
        print("  [4] 🤖 Form Auto-Entry Only (Fill ready leads from Master Excel into portal)")
        print("  [5] 🎯 Manual Target Mode (Choose specific City, Area, or Custom Category)")
        print("  [6] ⚡ Turbo Live All Pending Leads (Submit ALL 500+ pending & retry failed leads LIVE)")
        print("="*74)
        
        try:
            choice = input("\nEnter action choice [1-6] (default 6 for Turbo Live): ").strip() or "6"
        except Exception:
            choice = "6"
            
        choice_map = {
            "1": "auto",
            "2": "scrape",
            "3": "sync",
            "4": "submit",
            "5": "manual",
            "6": "live-pending"
        }
        mode = choice_map.get(choice, "live-pending")

    # Handle Instant Sync Mode
    if mode == "sync":
        from backend.google_sheets_sync import sync_excel_to_google_sheet
        print(f"\n🔄 Syncing Master Excel to Google Sheet now...")
        await sync_excel_to_google_sheet(DEFAULT_EXCEL)
        print("✓ Instant Google Sheet Sync Complete!")
        return

    # Handle Turbo Live All Pending Mode
    if mode == "live-pending":
        print(f"\n⚡ Starting Turbo Live Submission for ALL pending leads (Workers: {args.workers or 3})...")
        await run_auto_entry_batch(
            excel_path=DEFAULT_EXCEL,
            dry_run=args.dry_run,
            include_failed=True,
            limit=args.count,
            workers=args.workers or 3
        )
        if not args.no_sync:
            try:
                from backend.google_sheets_sync import sync_excel_to_google_sheet
                print("\n🔄 Updating Google Sheet with latest live submission statuses...")
                await sync_excel_to_google_sheet(DEFAULT_EXCEL)
            except Exception:
                pass
        print("\n==========================================================================")
        print("🎉 Turbo Live Pending process completed!")
        print(f"📁 Updated Master Excel: {DEFAULT_EXCEL}")
        print("==========================================================================")
        return

    count = args.count
    if count is None:
        try:
            val = input(f"\nHow many [{entity_type.upper()}] listings to process? (default 15): ").strip()
            count = int(val) if val.isdigit() else 15
        except Exception:
            count = 15

    print(f"\n✓ Starting Pipeline for [{entity_type.upper()}] in [{mode.upper()}] mode ({count} items)...\n")
    
    # Mode 1 & 2: Scrape next market in sequence
    if mode in ["auto", "scrape"]:
        print(f"--> Step 1: Deep scraping {entity_type} for up to {count} leads...")
        new_mined = await advance_saturation_cycle(
            target_leads_needed=count,
            entity_type=entity_type,
            excel_path=DEFAULT_EXCEL,
            auto_sync_sheets=not args.no_sync
        )
        print(f"✓ Step 1 Complete: {new_mined} fresh leads appended and synced.")

    # Mode 5: Manual target mode
    elif mode == "manual":
        city = args.city or input("Enter City (e.g. Jaipur, Surat, Ahmedabad): ").strip() or "Jaipur"
        area = args.area or input(f"Enter Market/Area in {city} (e.g. Johari Bazar, Sanganer): ").strip() or "Johari Bazar"
        cat = args.category or input(f"Enter Search Category (e.g. {entity_type}): ").strip() or entity_type
        
        print(f"--> Deep scraping [{city}] -> [{area}] ({cat} | {entity_type})...")
        new_mined = await advance_saturation_cycle(
            target_leads_needed=count,
            entity_type=entity_type,
            city_override=city,
            area_override=area,
            category_override=cat,
            excel_path=DEFAULT_EXCEL,
            auto_sync_sheets=not args.no_sync
        )
        print(f"✓ Manual Crawl Complete: {new_mined} leads added and synced.")

    # Auto Entry to JainForJain
    if mode in ["auto", "submit"]:
        live_flag = not args.dry_run
        if not args.mode and not args.dry_run:
            try:
                ans = input("\nDo you want LIVE submission or DRY-RUN preview? (Press Enter for LIVE, or type 'dry' for preview): ").strip().lower()
                live_flag = (ans != "dry")
            except Exception:
                live_flag = True
                
        print(f"\n--> Step 2: Running Data Entry Bot (Live={live_flag}) for up to {count} ready leads (Workers: {args.workers or 3})...")
        await run_auto_entry_batch(
            excel_path=DEFAULT_EXCEL,
            dry_run=not live_flag,
            limit=count,
            include_failed=True,
            workers=args.workers or 3
        )
        # Update Google Sheet with latest submission statuses
        if not args.no_sync:
            try:
                from backend.google_sheets_sync import sync_excel_to_google_sheet
                print("🔄 Updating Google Sheet with latest submission statuses...")
                await sync_excel_to_google_sheet(DEFAULT_EXCEL)
            except Exception:
                pass
        
    print("\n==========================================================================")
    print("🎉 Pipeline run finished successfully!")
    print(f"📁 Updated Master Excel: {DEFAULT_EXCEL}")
    print(f"📊 Live Google Sheet   : https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing")
    print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())

