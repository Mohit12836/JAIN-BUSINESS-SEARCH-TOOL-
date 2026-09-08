import asyncio
import sys
import os
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, r"C:\Users\hp\.gemini\antigravity\scratch\jain-lead-extractor")

from backend.scraper import scrape_google_maps_task

async def generate_real_file():
    print("Starting extraction for Jain Firms with Owner details...")
    
    def log_cb(data):
        if data.get("type") == "new_record":
            r = data["record"]
            print(f"  [+] {r['name']} | Owner: {r.get('owner')} | Phone: {r.get('phone')} | {r['tier']}")
        elif data.get("type") == "progress":
            print(f"  --> {data['percent']}%: {data['message']}")

    result = await scrape_google_maps_task(
        task_id="master_leads_live",
        category="Jewellers & Bullion",
        location_scope="Ahmedabad",
        include_sacred=True,
        include_surnames=True,
        include_photos=True,
        max_firms_target=10,
        progress_callback=log_cb
    )

    excel_path = result["excel_path"]
    print(f"\nExcel generated at: {excel_path}")

    # Copy to Desktop for immediate 1-click access
    desktop_dest = os.path.expanduser(r"~\Desktop\Jain_Firms_Verified_Leads.xlsx")
    shutil.copy(excel_path, desktop_dest)
    print(f"Copied directly to Desktop: {desktop_dest}")

if __name__ == "__main__":
    asyncio.run(generate_real_file())
