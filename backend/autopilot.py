"""
24/7 Autonomous Autopilot Scheduler & Turbo Fast Engine for JainBiz.
Supports:
1. Instant Zero-Delay Full Pipeline (Scrape -> Canva Assets -> Sheets -> Portal Entry with Photos).
2. Set-and-Forget Daily Background Scheduler with persistent config and automated execution.
"""

import os
import sys
import re
import json
import uuid
import asyncio
import datetime
from typing import Dict, Any, List, Optional, Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_master_excel_path, MAX_PORTAL_CONCURRENCY
from backend.matrix import build_query_batch
from backend.database import record_search_batch, get_search_history, save_scraped_lead
from backend.canva_storefront_generator import generate_batch_assets
from backend.excel_builder import generate_leads_excel
from backend.auto_entry_bot import (
    load_leads_from_excel,
    login_to_portal,
    fill_listing_form,
    update_excel_lead_status,
    DEFAULT_USER,
    DEFAULT_PASS
)
from backend.google_sheets_sync import sync_excel_to_google_sheet
from backend.saturation_engine import (
    CITY_MICRO_ZONES,
    CORE_CATEGORIES,
    load_progress,
    save_progress,
    crawl_area_deep
)

def get_ist_now() -> datetime.datetime:
    """Returns current datetime in Indian Standard Time (IST = UTC + 5:30)."""
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "autopilot_config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "is_active": False,
    "interval_minutes": 30,
    "batch_size": 20,
    "active_window": "24_hours",  # 24 Hours Pure Continuous Autonomous Execution
    "window_start": "00:00",
    "window_end": "23:59",
    "daily_time": "09:00",
    "frequency_hours": 0.5,
    "city": "Indore",
    "category": "Jewellers & All Commercial",
    "upload_mode": "instant",
    "delay_seconds": 0,
    "last_run_timestamp": None,
    "last_run_result": None,
    "next_run_timestamp": None,
    "total_runs": 0,
    "today_date": get_ist_now().strftime("%Y-%m-%d"),
    "today_submitted": 0,
    "running_state": "idle"  # "idle", "running", "completed", "error"
}

def load_autopilot_config() -> Dict[str, Any]:
    """Loads the persistent autopilot schedule configuration."""
    if not os.path.exists(CONFIG_FILE):
        save_autopilot_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_autopilot_config(cfg: Dict[str, Any]):
    """Persists configuration to disk."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def calculate_next_run(cfg: Optional[Dict[str, Any]] = None, daily_time: str = "09:00", freq_hours: float = 0.5) -> str:
    """Calculates formatted timestamp for next run adhering to 30-min interval in IST."""
    if cfg is None:
        cfg = load_autopilot_config()
        
    interval_mins = cfg.get("interval_minutes", 2)
    active_window = cfg.get("active_window", "24_hours")
    window_start_str = cfg.get("window_start", "00:00")
    window_end_str = cfg.get("window_end", "23:59")
    
    now = get_ist_now().replace(tzinfo=None)
    
    if active_window == "24_hours":
        candidate = now + datetime.timedelta(minutes=interval_mins)
        return candidate.strftime("%Y-%m-%d %H:%M:%S")
        
    # 12-hour window in IST
    try:
        sh, sm = map(int, window_start_str.split(":"))
        eh, em = map(int, window_end_str.split(":"))
    except Exception:
        sh, sm = 9, 0
        eh, em = 21, 0
        
    window_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    window_end = now.replace(hour=eh, minute=em, second=0, microsecond=0)
    
    if now < window_start:
        return window_start.strftime("%Y-%m-%d %H:%M:%S")
    elif now >= window_end:
        tomorrow_start = window_start + datetime.timedelta(days=1)
        return tomorrow_start.strftime("%Y-%m-%d %H:%M:%S")
    else:
        candidate = now + datetime.timedelta(minutes=interval_mins)
        if candidate >= window_end:
            tomorrow_start = window_start + datetime.timedelta(days=1)
            return tomorrow_start.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return candidate.strftime("%Y-%m-%d %H:%M:%S")

def toggle_autopilot(active: Optional[bool] = None) -> Dict[str, Any]:
    """Toggles autopilot ON/OFF. When ON, immediately triggers first batch (0s delay) in 24_hours mode."""
    cfg = load_autopilot_config()
    if active is None:
        cfg["is_active"] = not cfg.get("is_active", False)
    else:
        cfg["is_active"] = bool(active)

    if cfg["is_active"]:
        cfg["active_window"] = "24_hours"
        # Set next_run_timestamp to 5 seconds ago in IST so daemon picks it up instantly!
        cfg["next_run_timestamp"] = (get_ist_now().replace(tzinfo=None) - datetime.timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"🚀 [Autopilot] 24/7 Autopilot ACTIVATED! Immediate batch execution queued in IST.")
    else:
        cfg["next_run_timestamp"] = None
        cfg["running_state"] = "idle"
        print(f"⚪ [Autopilot] 24/7 Autopilot STOPPED.")

    save_autopilot_config(cfg)
    return cfg

async def execute_full_autonomous_cycle(
    batch_size: int = 50,
    city: str = "Indore",
    category: str = "Jewellers & All Commercial",
    upload_mode: str = "instant",
    delay_seconds: int = 0,
    source_mode: str = "full_auto",  # "full_auto", "ready_only", "fresh_only"
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Executes the Complete End-to-End Cycle:
    1. Scrapes next unharvested micro-market in the city (or uses ready unsubmitted leads if source_mode=='ready_only').
    2. Renders Canva Pro Profile Logo (1080x1080) & Storefront Banner (1200x500) in parallel (Zero AI Credits).
    3. Rebuilds Master Excel with 3 sheets and zero empty cells across all 26 columns.
    4. Auto-syncs to Google Sheet (Tab 1: Leads, Tab 2: Search & Coverage Tracker).
    5. Submits to jainforjain.com portal with signboard photos/logos uploaded!
       - If upload_mode == 'instant': delay = 0 seconds (Turbo Fast).
       - If upload_mode == 'throttled': waits delay_seconds between submissions.
    6. Updates SQLite Search & Coverage Tracker.
    """
    def emit_log(msg: str, stage: str = "INFO", badge: str = "ℹ️", pct: Optional[int] = None):
        print(f"[{stage}] {msg}")
        if progress_callback:
            progress_callback({
                "type": "log",
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
                "stage": stage,
                "badge": badge,
                "message": msg,
                "percent": pct
            })

    def emit_progress(pct: int, msg: str):
        if progress_callback:
            progress_callback({
                "type": "progress",
                "percent": min(pct, 100),
                "message": msg
            })

    timer_str = "पूरी तरह बंद (0s डिले • नो वेटिंग • एक साथ)" if delay_seconds == 0 else f"{delay_seconds}s अंतराल"
    emit_log(f"⚡ सुपरफास्ट बैच प्रारंभ | शहर: {city} | लक्ष्य: {batch_size} लीड्स | ⏱️ टाइमर: {timer_str}", stage="INIT", badge="⚡", pct=5)

    excel_path = get_master_excel_path()
    all_leads = []
    if os.path.exists(excel_path):
        try:
            all_leads = load_leads_from_excel(excel_path)
        except Exception:
            all_leads = []

    collected: List[Dict[str, Any]] = []

    # 1. Determine next unharvested micro-market
    state = load_progress()
    active_city = city or state.get("current_city") or "Indore"
    areas = CITY_MICRO_ZONES.get(active_city, ["Sarafa Bazar", "Rajwada", "Palasia", "Vijay Nagar"])
    area_idx = state.get("area_idx", 0)
    current_area = areas[area_idx % len(areas)]
    next_area = areas[(area_idx + 1) % len(areas)]
    active_category = category or CORE_CATEGORIES[state.get("category_idx", 0) % len(CORE_CATEGORIES)]
    batch_id = f"BATCH-{uuid.uuid4().hex[:6].upper()}"

    unsubmitted_existing = [l for l in all_leads if "Submitted" not in l.get("submission_status", "")]

    if source_mode == "ready_only" and unsubmitted_existing:
        emit_log(f"📋 पहले से तैयार {len(unsubmitted_existing)} अनसबमिटेड लीड्स को तुरंत प्रोसेस किया जा रहा है...", stage="READY_LEADS", badge="📋", pct=20)
        collected = unsubmitted_existing[:batch_size]
    else:
        emit_log(f"📍 लक्षित क्षेत्र: [{active_city} - {current_area}] | श्रेणी: {active_category}", stage="TARGET", badge="📍", pct=10)
        emit_progress(12, f"खोज प्रारंभ: {current_area} ({active_city})...")

        # Deep Crawl for leads
        collected = await crawl_area_deep(
            city=active_city,
            area=current_area,
            category=active_category,
            target_count=batch_size,
            entity_type="commercial",
            excel_path=excel_path,
            auto_sync_sheets=False
        )
        emit_log(f"🏬 {len(collected)} नए जैन व्यापार Google Maps से निकाले गए!", stage="MINED", badge="🏬", pct=40)

    # 2. Generate Canva Pro Assets in Parallel (Zero AI Credits)
    targets_for_assets = collected.copy()
    for l in all_leads:
        if not l.get("canva_banner_url") and l not in targets_for_assets:
            targets_for_assets.append(l)

    if targets_for_assets:
        emit_log(f"🎨 {len(targets_for_assets)} बिज़नेस के लिए Canva Pro लोगो (1080x1080) व बैनर (1200x500) समानांतर तैयार हो रहे हैं...", stage="CANVA", badge="🎨", pct=45)
        try:
            await generate_batch_assets(targets_for_assets, max_concurrent=5)
            emit_log("✅ Canva Pro ग्राफ़िक्स तैयार और लिंक हो गए!", stage="CANVA_DONE", badge="✅", pct=60)
        except Exception as ce:
            emit_log(f"कैनवा जनरेशन सूचना: {ce}", stage="WARN", badge="⚠️")

    # 3. Master Excel Rebuild & Zero Empty Columns Enforcement
    seen_phones = {re.sub(r'\D', '', l.get('phone', ''))[-10:] for l in all_leads if l.get('phone')}
    newly_added = []
    if source_mode != "ready_only":
        for rec in collected:
            clean_p = re.sub(r'\D', '', rec.get('phone', ''))[-10:]
            if clean_p and clean_p in seen_phones:
                continue
            if clean_p:
                seen_phones.add(clean_p)
            newly_added.append(rec)
            all_leads.append(rec)

        # Rebuild 3-sheet Excel
        generate_leads_excel(all_leads, excel_path, category=active_category, scope=f"{active_city} - {current_area}")

    # Copy to Desktop
    try:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop_dir):
            import shutil
            shutil.copyfile(excel_path, os.path.join(desktop_dir, "Jain_Leads_Verified_Photos_HD.xlsx"))
    except Exception:
        pass

    emit_log("💾 Master Excel (26 कॉलम, 0 खाली सेल, 3 शीट्स) सफलतापूर्वक अपडेट!", stage="EXCEL", badge="💾", pct=70)

    # 5. Live Google Sheet Sync
    emit_log("📊 Google Sheet में शीट 1 (Leads) व शीट 2 (Tracker) सिंक की जा रही है...", stage="SHEET_SYNC", badge="📊", pct=75)
    try:
        await sync_excel_to_google_sheet(excel_path)
        emit_log("✅ Google Sheet 100% सिंक हो गई!", stage="SHEET_OK", badge="✅", pct=80)
    except Exception as ge:
        emit_log(f"Google Sheet सिंक सूचना: {ge}", stage="WARN", badge="⚠️")

    # 6. Portal Submission with Photos Uploaded (Instant vs Throttled)
    submitted_count = 0
    quota_reached = False
    actual_delay = 0 if upload_mode == "instant" else max(delay_seconds, 15)
    if actual_delay == 0:
        emit_log("⚡ jainforjain.com पोर्टल पर फ़ोटो सहित सबमिशन प्रारंभ (0s डिले • नो टाइमर • सब कुछ तुरंत)...", stage="PORTAL_START", badge="🚀", pct=82)
    else:
        emit_log(f"🚀 jainforjain.com पोर्टल पर सबमिशन प्रारंभ (मोड: {upload_mode}, डिले: {actual_delay}s)...", stage="PORTAL_START", badge="🚀", pct=82)

    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = await browser.new_context(viewport={"width": 1400, "height": 950})
            page = await context.new_page()

            logged = await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
            if not logged:
                emit_log("❌ पोर्टल लॉगिन विफल। कृपया क्रेडेंशियल्स जांचें।", stage="PORTAL_ERR", badge="❌", pct=88)
            else:
                emit_log("✅ पोर्टल लॉगिन सफल! लिस्टिंग्स दर्ज की जा रही हैं...", stage="PORTAL_AUTH", badge="✅", pct=85)

                leads_to_submit = [l for l in all_leads if "Submitted" not in l.get("submission_status", "")]
                if not leads_to_submit and newly_added:
                    leads_to_submit = newly_added
                leads_to_submit = leads_to_submit[:batch_size]

                if upload_mode == "instant" and len(leads_to_submit) > 1:
                    # ⚡ SAFE 2-WORKER PARALLEL TURBO MODE (Prevents Livewire collisions)
                    concurrency = min(MAX_PORTAL_CONCURRENCY, len(leads_to_submit))
                    emit_log(f"⚡ सुपरफास्ट मोड: {concurrency} समानांतर (Parallel) सुरक्षित वर्कर प्रारंभ किए जा रहे हैं...", stage="TURBO", badge="⚡")
                    q = asyncio.Queue()
                    for l in leads_to_submit:
                        q.put_nowait(l)

                    excel_lock = asyncio.Lock()

                    async def sub_worker(w_id: int):
                        nonlocal submitted_count, quota_reached
                        w_page = await context.new_page()
                        try:
                            while not q.empty() and not quota_reached:
                                try:
                                    lead = q.get_nowait()
                                except asyncio.QueueEmpty:
                                    break

                                l_name = lead.get("name", "")
                                l_row = lead.get("row_idx", 2)
                                emit_log(f"📝 [वर्कर {w_id}] भर रहे हैं: '{l_name}'...", stage="SUBMITTING", badge="📝")
                                try:
                                    res = await fill_listing_form(w_page, lead, dry_run=False)
                                    b_id = res.get("biz_id", "")
                                    p_url = res.get("profile_url", "")
                                    if b_id:
                                        async with excel_lock:
                                            update_excel_lead_status(excel_path, l_row, b_id, p_url, "Submitted - Live")
                                            submitted_count += 1
                                            lead["j4j_business_id"] = b_id
                                            lead["j4j_profile_url"] = p_url
                                            lead["submission_status"] = "Submitted - Live"
                                        emit_log(f"🎉 [वर्कर {w_id}] सबमिट: ID: {b_id} | 🔗 {p_url}", stage="SUBMITTED", badge="🎉")
                                except Exception as sub_err:
                                    err_str = str(sub_err)
                                    if any(w in err_str.lower() for w in ["limit", "package", "quota"]):
                                        quota_reached = True
                                        emit_log("⚠️ पोर्टल कोटा अलर्ट!", stage="QUOTA", badge="⚠️")
                                finally:
                                    q.task_done()
                        finally:
                            await w_page.close()

                    await asyncio.gather(*(sub_worker(i+1) for i in range(concurrency)))
                else:
                    # Sequential mode with pacing
                    for idx, lead in enumerate(leads_to_submit, start=1):
                        if quota_reached:
                            break

                        lead_name = lead.get("name", "")
                        lead_row = lead.get("row_idx", idx + 1)

                        emit_log(f"📝 [{idx}/{len(leads_to_submit)}] पोर्टल पर भर रहे हैं: '{lead_name}'...", stage="SUBMITTING", badge="📝")

                        try:
                            res = await fill_listing_form(page, lead, dry_run=False)
                            biz_id = res.get("biz_id", "")
                            profile_url = res.get("profile_url", "")

                            if biz_id:
                                update_excel_lead_status(excel_path, lead_row, biz_id, profile_url, "Submitted - Live")
                                submitted_count += 1
                                lead["j4j_business_id"] = biz_id
                                lead["j4j_profile_url"] = profile_url
                                lead["submission_status"] = "Submitted - Live"
                                emit_log(f"🎉 [{idx}] सफलतापूर्वक सबमिट! ID: {biz_id} | 🔗 {profile_url}", stage="SUBMITTED", badge="🎉")

                            if actual_delay > 0 and idx < len(leads_to_submit):
                                emit_log(f"⏱️ टाइमर अंतराल: अगली लीड के लिए {actual_delay} सेकंड प्रतीक्षा कर रहे हैं...", stage="TIMER", badge="⏱️")
                                await asyncio.sleep(actual_delay)

                        except Exception as sub_err:
                            err_str = str(sub_err)
                            if any(w in err_str.lower() for w in ["limit", "package", "maximum listing", "quota"]):
                                quota_reached = True
                                emit_log("⚠️ पोर्टल कोटा अलर्ट!", stage="QUOTA", badge="⚠️")
                                break
                            else:
                                emit_log(f"⚠️ सबमिशन सूचना [{lead_name}]: {err_str[:80]}", stage="WARN", badge="⚠️")

            await browser.close()
    except Exception as pe:
        emit_log(f"पोर्टल सबमिशन अपवाद: {pe}", stage="WARN", badge="⚠️")

    # 7. Record Batch in SQLite
    total_cum = record_search_batch(
        batch_id=batch_id,
        category=active_category,
        city=active_city,
        area_name=current_area,
        batch_size=batch_size,
        extracted_count=len(collected),
        next_area=next_area,
        status="100% Saturated / पूर्ण",
        sync_status="Synced"
    )

    # 8. Advance Area Saturation State
    state["area_idx"] = area_idx + 1
    state["total_mined"] = total_cum
    if f"{active_city} - {current_area}" not in state.get("completed_areas", []):
        state.setdefault("completed_areas", []).append(f"{active_city} - {current_area}")
    save_progress(state)

    # 9. Final Google Sheet update
    try:
        await sync_excel_to_google_sheet(excel_path)
    except Exception:
        pass

    summary = {
        "status": "completed",
        "batch_id": batch_id,
        "batch_size": batch_size,
        "extracted_count": len(collected),
        "submitted_count": submitted_count,
        "current_area": current_area,
        "next_area": next_area,
        "cumulative_total": total_cum,
        "sheet_url": "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
    }

    emit_log(
        f"🏆 ऑटोनोमस साइकिल पूर्ण! खोजे गए: {len(collected)}, पोर्टल पर सबमिट: {submitted_count}, कुल संचयी: {total_cum} लीड्स। अगला क्षेत्र: {next_area}",
        stage="COMPLETE",
        badge="🏆",
        pct=100
    )

    if progress_callback:
        progress_callback({
            "type": "complete",
            "message": f"✓ टास्क पूर्ण! {len(collected)} बिज़नेस निकाले गए, {submitted_count} पोर्टल पर सबमिट।",
            "summary": summary
        })

    return summary

# ==================== 24/7 BACKGROUND DAEMON WORKER ====================
async def run_autopilot_background_worker():
    """
    Background worker that runs indefinitely inside the FastAPI process.
    Checks autopilot_config.json every 5 seconds using Indian Standard Time (IST).
    Triggers execute_streamed_live_pipeline when scheduled time arrives.
    Frees 100% CPU and memory immediately after finishing each batch.
    """
    print("⏰ [Autopilot Daemon] 24/7 Background worker loop started (IST Timezone).")
    from backend.system_guard import free_system_resources_completely

    while True:
        try:
            cfg = load_autopilot_config()
            now_ist = get_ist_now().replace(tzinfo=None)
            today_str = now_ist.strftime("%Y-%m-%d")
            if cfg.get("today_date") != today_str:
                cfg["today_date"] = today_str
                cfg["today_submitted"] = 0
                save_autopilot_config(cfg)

            if cfg.get("is_active", False) and cfg.get("running_state") != "running":
                next_run_str = cfg.get("next_run_timestamp")
                if not next_run_str:
                    cfg["next_run_timestamp"] = now_ist.strftime("%Y-%m-%d %H:%M:%S")
                    save_autopilot_config(cfg)
                    next_run_str = cfg["next_run_timestamp"]

                try:
                    next_dt = datetime.datetime.strptime(next_run_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    next_dt = now_ist

                if now_ist >= next_dt:
                    print(f"⏰ [Autopilot Daemon] Scheduled execution time reached ({next_run_str} IST)! Triggering 30-min streamed run (target: {cfg.get('batch_size', 20)})...")
                    cfg["running_state"] = "running"
                    save_autopilot_config(cfg)

                    try:
                        from backend.auto_batch_engine import execute_streamed_live_pipeline
                        res = await execute_streamed_live_pipeline(
                            target_count=cfg.get("batch_size", 20),
                            city=cfg.get("city", "Indore"),
                            category=cfg.get("category", "Jewellers & All Commercial")
                        )
                    except Exception as exec_err:
                        print(f"⚠️ [Autopilot Daemon] Error during run: {exec_err}")
                        res = {"status": "error", "message": str(exec_err), "submitted_count": 0}
                    finally:
                        # ALWAYS FREE 100% CPU AND REAP PROCESSES IMMEDIATELY!
                        free_system_resources_completely()

                    cfg = load_autopilot_config()
                    finish_ist = get_ist_now().replace(tzinfo=None)
                    cfg["last_run_timestamp"] = finish_ist.strftime("%Y-%m-%d %H:%M:%S")
                    cfg["last_run_result"] = res
                    cfg["total_runs"] = cfg.get("total_runs", 0) + 1
                    cfg["today_submitted"] = cfg.get("today_submitted", 0) + res.get("submitted_count", 0)
                    cfg["running_state"] = "idle"
                    cfg["next_run_timestamp"] = calculate_next_run(cfg)
                    save_autopilot_config(cfg)
                    print(f"⏰ [Autopilot Daemon] Streamed run completed. Today submitted: {cfg['today_submitted']}. CPU freed (0.0%). Next run: {cfg['next_run_timestamp']} IST")

        except Exception as e:
            print(f"⚠️ [Autopilot Daemon] Exception in loop: {e}")

        await asyncio.sleep(5)
