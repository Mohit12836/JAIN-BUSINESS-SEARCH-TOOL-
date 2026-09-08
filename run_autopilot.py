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
    print("==========================================================================")

async def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="JainBiz Auto-Pilot Pipeline")
    parser.add_argument("--mode", choices=["auto", "scrape", "submit", "manual"], default=None)
    parser.add_argument("--count", type=int, default=None, help="Number of listings to process")
    parser.add_argument("--live", action="store_true", help="Submit live to JainForJain")
    parser.add_argument("--city", default=None, help="City override for manual mode")
    parser.add_argument("--area", default=None, help="Area override for manual mode")
    parser.add_argument("--category", default=None, help="Category override for manual mode")
    
    args = parser.parse_args()
    
    mode = args.mode
    if not mode:
        print("\nChoose an option:")
        print("  [1] 🚀 Full Auto-Pilot (Scrape next market leads + Auto-fill to JainForJain)")
        print("  [2] ⛏️ Scrape Next Market Only (Exhaust current area, add to Master Excel)")
        print("  [3] 🤖 Form Auto-Entry Only (Fill ready leads from Master Excel into portal)")
        print("  [4] 🎯 Manual Target Mode (Choose specific City, Area, or Category)")
        
        try:
            choice = input("\nEnter choice [1-4] (default 1): ").strip() or "1"
        except Exception:
            choice = "1"
            
        choice_map = {"1": "auto", "2": "scrape", "3": "submit", "4": "manual"}
        mode = choice_map.get(choice, "auto")

    count = args.count
    if count is None:
        try:
            val = input("\nHow many listings do you want to process today? (default 15): ").strip()
            count = int(val) if val.isdigit() else 15
        except Exception:
            count = 15

    print(f"\n✓ Starting Pipeline in [{mode.upper()}] mode for {count} listings...\n")
    
    # Mode 1 & 2: Scrape next market in sequence
    if mode in ["auto", "scrape"]:
        print(f"--> Step 1: Deep scraping current micro-market for up to {count} leads...")
        new_mined = await advance_saturation_cycle(
            target_leads_needed=count,
            excel_path=DEFAULT_EXCEL
        )
        print(f"✓ Step 1 Complete: {new_mined} fresh leads appended to Master Excel.")

    # Mode 4: Manual target mode
    elif mode == "manual":
        city = args.city or input("Enter City (e.g. Jaipur, Surat, Ahmedabad): ").strip() or "Jaipur"
        area = args.area or input(f"Enter Market/Area in {city} (e.g. Johari Bazar, MI Road): ").strip() or "Johari Bazar"
        cat = args.category or input("Enter Category (e.g. Jewellers & Gems): ").strip() or "Jewellers & Gems"
        
        print(f"--> Deep scraping [{city}] -> [{area}] ({cat})...")
        new_mined = await advance_saturation_cycle(
            target_leads_needed=count,
            city_override=city,
            area_override=area,
            category_override=cat,
            excel_path=DEFAULT_EXCEL
        )
        print(f"✓ Manual Crawl Complete: {new_mined} leads added to Master Excel.")

    # Auto Entry to JainForJain
    if mode in ["auto", "submit"]:
        live_flag = args.live
        if not live_flag and not args.mode:
            try:
                ans = input("\nDo you want LIVE submission or DRY-RUN preview? (type 'live' or press Enter for dry-run): ").strip().lower()
                live_flag = (ans == "live")
            except Exception:
                live_flag = False
                
        print(f"\n--> Step 2: Running Data Entry Bot (Live={live_flag}) for up to {count} ready leads...")
        await run_auto_entry_batch(
            excel_path=DEFAULT_EXCEL,
            dry_run=not live_flag,
            limit=count
        )
        
    print("\n==========================================================================")
    print("🎉 Pipeline run finished successfully!")
    print(f"📁 Updated Master Excel: {DEFAULT_EXCEL}")
    print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())

