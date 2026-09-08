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
        location_scope="Jaipur",
        include_sacred=True,
        include_surnames=True,
        include_photos=True,
        max_firms_target=10,
        progress_callback=log_cb
    )

    excel_path = result["excel_path"]
    print(f"\nExcel generated at: {excel_path}")

    # Copy to Desktop with robust fallback if existing files are locked in Excel
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    targets = [
        os.path.expanduser(r"~\Desktop\Jain_Leads_Verified_Photos_HD.xlsx"),
        os.path.expanduser(r"~\Desktop\Jain_Firms_Verified_Leads.xlsx"),
        os.path.expanduser(f"~\\Desktop\\Jain_Leads_Verified_{timestamp}.xlsx")
    ]
    for target in targets:
        try:
            shutil.copy(excel_path, target)
            print(f"Copied directly to Desktop: {target}")
            break
        except PermissionError:
            continue

if __name__ == "__main__":
    asyncio.run(generate_real_file())
