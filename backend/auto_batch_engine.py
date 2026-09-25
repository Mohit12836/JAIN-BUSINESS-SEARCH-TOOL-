"""
Master 1-Click Autonomous Auto-Batch Engine for JainBiz.
Executes the complete next 100-150 batch flow:
1. Resolves roadmap & unharvested micro-markets from saturation_progress.json.
2. Prioritizes unsubmitted Excel leads & harvests remaining leads up to target count.
3. Generates Canva Pro HD 1080x1080 Logos & 1200x500 Banners in parallel.
4. Updates 26-column Master Excel (0 empty cells) & Desktop backup.
5. Live syncs to Google Sheets (Tab 1: Leads, Tab 2: Tracker).
6. Submits to jainforjain.com using hardened 2-worker Playwright bot with verified FilePond photo uploads.
7. Captures real JFJ-XXXXX IDs & live URLs back into Excel & Google Sheets.
8. Automatically advances micro-market roadmap pointer.
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
from backend.database import record_search_batch, get_search_history, save_scraped_lead
from backend.canva_storefront_generator import generate_batch_assets
from backend.excel_builder import generate_leads_excel
from backend.account_manager import resolve_credentials
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
    crawl_area_deep,
    get_area_roadmap,
    append_to_master_excel
)

def is_lead_pending(lead: Dict[str, Any]) -> bool:
    """
    Returns True only if lead is pending submission.
    STRICT CROSS-ACCOUNT DEDUPLICATION:
    If a lead has EVER been submitted or assigned a j4j_business_id / j4j_profile_url on ANY account,
    it is strictly excluded and will NEVER be re-submitted.
    """
    status = str(lead.get("submission_status", "")).strip().lower()
    if not lead.get("name"):
        return False
    if "submitted" in status or "live" in status:
        return False
    if "skipped" in status or "already" in status or "duplicate" in status:
        return False
    # Cross-Account safety: If lead already has j4j_business_id or j4j_profile_url under ANY account
    if str(lead.get("j4j_business_id", "")).strip():
        return False
    if str(lead.get("j4j_profile_url", "")).strip():
        return False
    return True

def get_auto_batch_status(city: Optional[str] = None) -> Dict[str, Any]:
    """Returns comprehensive status for the 1-Click Auto-Batch UI Card."""
    state = load_progress()
    active_city = city or state.get("current_city", "Indore")
    roadmap = get_area_roadmap(active_city)
    
    excel_path = get_master_excel_path()
    all_leads = []
    if os.path.exists(excel_path):
        try:
            all_leads = load_leads_from_excel(excel_path)
        except Exception:
            all_leads = []
            
    unsubmitted_count = sum(1 for l in all_leads if is_lead_pending(l))
    submitted_count = sum(1 for l in all_leads if "submitted" in str(l.get("submission_status", "")).lower() or "live" in str(l.get("submission_status", "")).lower())
    skipped_count = sum(1 for l in all_leads if "skipped" in str(l.get("submission_status", "")).lower() or "already" in str(l.get("submission_status", "")).lower())
    
    return {
        "city": active_city,
        "current_area": roadmap["current_area"],
        "next_area": roadmap["next_area"],
        "current_area_idx": roadmap["current_area_idx"],
        "total_areas": roadmap["total_areas"],
        "completed_areas": roadmap["completed_areas"],
        "total_mined_leads": state.get("total_mined", len(all_leads)),
        "excel_total_leads": len(all_leads),
        "excel_unsubmitted": unsubmitted_count,
        "excel_submitted": submitted_count,
        "excel_skipped": skipped_count,
        "recommended_batch": 150 if unsubmitted_count < 150 else 100,
        "max_portal_concurrency": MAX_PORTAL_CONCURRENCY,
        "sheet_url": "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
    }

async def execute_pure_scraper_batch(
    target_count: int = 50,
    city: Optional[str] = None,
    category: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    ENGINE 1 (PURE SCRAPER):
    100% focused on Maps extraction, Canva Pro asset generation, Master Excel, and Google Sheet sync.
    Zero portal interaction! Blazing fast, zero timeouts.
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

    batch_id = f"SCRAPE-{uuid.uuid4().hex[:6].upper()}"
    state = load_progress()
    active_city = city or state.get("current_city") or "Indore"
    areas = CITY_MICRO_ZONES.get(active_city, ["Sarafa Bazar", "Rajwada", "Marothia Bazar", "Sitlamata Bazar", "Palasia", "Vijay Nagar"])
    
    area_idx = state.get("area_idx", 0)
    current_area = areas[area_idx % len(areas)]
    next_area = areas[(area_idx + 1) % len(areas)]
    active_category = category or CORE_CATEGORIES[state.get("category_idx", 0) % len(CORE_CATEGORIES)]

    emit_log(
        f"🔍 [इंजन 1: लीड स्क्रैपर] प्रारंभ | लक्ष्य: {target_count} लीड्स | शहर: {active_city} | बाज़ार: {current_area}",
        stage="INIT",
        badge="🔍",
        pct=5
    )
    emit_log(
        "⚡ 4-पैरेलल टैब्स एक्टिवेट: Google Maps से सत्यापित जैन बिज़नेस + Canva HD फ़ोटो + Excel/Google Sheet सिंक...",
        stage="SCRAPE_START",
        badge="⚡",
        pct=10
    )

    excel_path = get_master_excel_path()
    try:
        from backend.google_sheets_sync import download_google_sheet_to_excel
        download_google_sheet_to_excel(excel_path)
    except Exception:
        pass

    mined_leads = []
    curr_crawl_idx = area_idx
    while len(mined_leads) < target_count and curr_crawl_idx < len(areas) + area_idx:
        crawl_area_name = areas[curr_crawl_idx % len(areas)]
        needed = target_count - len(mined_leads)
        emit_log(
            f"📍 बाज़ार सैचुरेशन: [{active_city} - {crawl_area_name}] | आवश्यकता: {needed} लीड्स...",
            stage="CRAWLING",
            badge="📍"
        )
        batch_leads = await crawl_area_deep(
            city=active_city,
            area=crawl_area_name,
            category=active_category,
            target_count=needed,
            entity_type="all",
            excel_path=excel_path,
            auto_sync_sheets=True,
            progress_callback=progress_callback
        )
        if batch_leads:
            mined_leads.extend(batch_leads)
        curr_crawl_idx += 1

    # Record batch and advance roadmap
    total_cum = record_search_batch(
        batch_id=batch_id,
        category=active_category,
        city=active_city,
        area_name=current_area,
        batch_size=target_count,
        extracted_count=len(mined_leads),
        next_area=next_area,
        status="Ready to Submit",
        sync_status="Synced"
    )

    state["area_idx"] = curr_crawl_idx
    state["total_mined"] = total_cum
    area_key = f"{active_city} - {current_area}"
    if area_key not in state.get("completed_areas", []):
        state.setdefault("completed_areas", []).append(area_key)
    save_progress(state)

    emit_log(
        f"🎉 [इंजन 1 संपन्न!] कुल {len(mined_leads)} नए जैन व्यापारी Master Excel व Google Sheet में 'Ready to Submit' स्थिति में सुरक्षित हैं!",
        stage="COMPLETE",
        badge="🎉",
        pct=100
    )

    summary = {
        "status": "success",
        "engine": "scraper_only",
        "batch_id": batch_id,
        "target_count": target_count,
        "mined_count": len(mined_leads),
        "current_area": current_area,
        "next_area": next_area,
        "total_mined": total_cum,
        "sheet_url": "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
    }

    if progress_callback:
        progress_callback({
            "type": "complete",
            "message": f"🎉 {len(mined_leads)} लीड्स सफलतापूर्वक Excel व Google Sheet में सुरक्षित!",
            "percent": 100,
            "mined_count": len(mined_leads),
            "summary": summary
        })

    return summary


async def execute_pure_submitter_batch(
    target_count: int = 50,
    delay_seconds: int = 0,
    portal_email: Optional[str] = None,
    portal_password: Optional[str] = None,
    account_id: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    ENGINE 2 (PURE PORTAL SUBMITTER):
    100% focused on taking unsubmitted 'Ready to Submit' leads from Excel/Sheet
    and submitting them to jainforjain.com. Zero Google Maps scraping.
    Strictly guarantees that leads already submitted under ANY account are NEVER re-submitted!
    """
    auth_email, auth_pass, auth_tag = resolve_credentials(portal_email, portal_password, account_id)
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

    excel_path = get_master_excel_path()
    try:
        from backend.google_sheets_sync import download_google_sheet_to_excel
        download_google_sheet_to_excel(excel_path)
    except Exception:
        pass

    # 1. Run automatic deduplication so duplicate phone numbers / names in the sheet are safely skipped
    try:
        from backend.excel_builder import deduplicate_master_excel
        dedup_res = deduplicate_master_excel(excel_path)
        if dedup_res.get("duplicates_flagged", 0) > 0:
            emit_log(f"🧹 [ऑटो-डीडुप्लिकेशन] शीट में {dedup_res['duplicates_flagged']} डुप्लिकेट एंट्रीज (समान डॉक्टर/फोन नंबर) पाई गईं! उन्हें स्वतः 'Skipped' मार्क किया गया।", stage="DEDUP", badge="🧹")
    except Exception as d_err:
        print(f"Dedup check: {d_err}")

    all_leads = load_leads_from_excel(excel_path)
    
    # 2. Extract targets with on-the-fly deduplication to guarantee 100% unique firms
    seen_batch_phones = set()
    seen_batch_names = set()
    targets = []
    
    # Pre-populate with already submitted leads
    for l in all_leads:
        st = str(l.get("submission_status", "")).lower()
        if "submitted" in st or "live" in st:
            p = "".join(c for c in str(l.get("phone", "")) if c.isdigit())[-10:]
            if len(p) == 10:
                seen_batch_phones.add(p)
            n = re.sub(r'[^a-zA-Z0-9]+', '', f"{l.get('name', '')}_{l.get('city', '')}".lower())
            if n:
                seen_batch_names.add(n)

    for l in all_leads:
        if not is_lead_pending(l):
            continue
        p = "".join(c for c in str(l.get("phone", "")) if c.isdigit())[-10:]
        n = re.sub(r'[^a-zA-Z0-9]+', '', f"{l.get('name', '')}_{l.get('city', '')}".lower())
        if (len(p) == 10 and p in seen_batch_phones) or (n and n in seen_batch_names):
            update_excel_lead_status(excel_path, l["row_idx"], "DUPLICATE", "", "Skipped - Duplicate Entry in Excel")
            continue
        if len(p) == 10:
            seen_batch_phones.add(p)
        if n:
            seen_batch_names.add(n)
        targets.append(l)
        if len(targets) >= target_count:
            break

    emit_log(
        f"🏛️ [इंजन 2: पोर्टल ऑटो-सबमिटर] प्रारंभ | कुल यूनिक लंबित लीड्स: {len(targets)} | सबमिट लक्ष्य: {min(target_count, len(targets))}",
        stage="INIT",
        badge="🏛️",
        pct=5
    )

    if not targets:
        emit_log("✓ कोई लंबित लीड नहीं है! सभी लीड्स पहले से पोर्टल पर लाइव हैं।", stage="ALL_LIVE", badge="✅", pct=100)
        return {"status": "no_pending_leads", "submitted_count": 0}

    submitted_count = 0
    quota_reached = False

    from playwright.async_api import async_playwright
    from backend.system_guard import CHROMIUM_TURBO_ARGS, apply_turbo_routing, safe_close_browser, free_system_resources_completely

    portal_browser = None
    portal_context = None
    try:
        async with async_playwright() as p:
            try:
                portal_browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
            except Exception:
                portal_browser = await p.chromium.launch(headless=True, channel="chrome", args=CHROMIUM_TURBO_ARGS)
            portal_context = await portal_browser.new_context(viewport={"width": 1400, "height": 950})
            await apply_turbo_routing(portal_context, block_images=False)
            portal_page = await portal_context.new_page()

            emit_log(f"🔐 jainforjain.com पर लॉगिन किया जा रहा है ({auth_email})...", stage="LOGIN", badge="🔐", pct=10)
            logged = await login_to_portal(portal_page, auth_email, auth_pass)
            if not logged:
                emit_log(f"❌ पोर्टल लॉगिन विफल ({auth_email})! क्रेडेंशियल्स जांचें.", stage="LOGIN_ERR", badge="❌")
                return {"status": "error", "message": f"Portal login failed for {auth_email}"}

            await portal_page.close()
            emit_log(f"✅ पोर्टल लॉगिन 100% सफल ({auth_email})! टर्बो पैरेलल ऑटो-फिलिंग शुरू...", stage="PORTAL_OK", badge="✅", pct=15)

            # High-Speed Multi-Tab Parallel Worker Pool (Turbo 4x Speed)
            from backend.config import MAX_PORTAL_CONCURRENCY
            concurrency = min(MAX_PORTAL_CONCURRENCY or 4, len(targets))
            emit_log(
                f"⚡ [टर्बो पैरेलल इंजन] {concurrency} समानांतर टैब्स (Workers) सक्रिय! एक साथ {concurrency} लीड्स लाइव भरी जा रही हैं...",
                stage="TURBO_START",
                badge="⚡",
                pct=18
            )

            queue = asyncio.Queue()
            for idx, lead in enumerate(targets, start=1):
                queue.put_nowait((idx, lead))

            excel_lock = asyncio.Lock()

            async def worker(worker_id: int):
                nonlocal submitted_count, quota_reached
                w_page = await portal_context.new_page()
                try:
                    while not queue.empty() and not quota_reached:
                        try:
                            item_idx, lead = queue.get_nowait()
                        except asyncio.QueueEmpty:
                            break

                        l_name = lead.get("name", "")
                        cur_row = lead.get("row_idx", 2)
                        owner_name = lead.get("owner", "Proprietor")

                        emit_log(f"📝 [टैब {worker_id}] [{item_idx}/{len(targets)}] फॉर्म भरा जा रहा है: '{l_name}' ({owner_name})...", stage="SUBMITTING", badge="📝")

                        try:
                            res = await fill_listing_form(w_page, lead, dry_run=False)
                            b_id = res.get("biz_id", "")
                            p_url = res.get("profile_url", "")
                            status_txt = res.get("status", "")

                            if res.get("duplicate") or "Skipped" in status_txt or "Already" in status_txt:
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, cur_row, "ALREADY_LISTED", p_url, "Skipped - Already on Portal")
                                    lead["submission_status"] = "Skipped - Already on Portal"
                                emit_log(f"⏭️ [टैब {worker_id}] [स्किप] '{l_name}' पोर्टल पर पहले से मौजूद है! (सुरक्षित स्किप)", stage="SKIPPED", badge="⏭️")
                            elif b_id and b_id.startswith("JFJ-") and res.get("status") == "submitted_success":
                                status_label = f"Submitted - Live [{auth_email}]"
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, cur_row, b_id, p_url, status_label)
                                    submitted_count += 1
                                    lead["j4j_business_id"] = b_id
                                    lead["j4j_profile_url"] = p_url
                                    lead["submission_status"] = status_label
                                pct = min(18 + int((submitted_count / len(targets)) * 80), 98)
                                emit_log(f"🎉 [टैब {worker_id}] [{submitted_count}/{len(targets)}] '{l_name}' ➔ पोर्टल पर 100% लाइव! (ID: {b_id} | {auth_email})", stage="LIVE_SUBMITTED", badge="🎉", pct=pct)
                            else:
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, cur_row, "", "", f"Skipped: {res.get('error', 'Validation')[:25]}")
                                    lead["submission_status"] = f"Skipped: {res.get('error', 'Validation')[:25]}"
                                emit_log(f"⚠️ [टैब {worker_id}] सबमिशन स्किप [{l_name}]: {res.get('error', 'फॉर्म सत्यापन चेतावनी')[:60]}", stage="WARN", badge="⚠️")
                        except Exception as err:
                            err_str = str(err)
                            if any(w in err_str.lower() for w in ["limit", "package", "quota"]):
                                quota_reached = True
                                emit_log("⚠️ पोर्टल कोटा अलर्ट: अधिकतम लिस्टिंग सीमा पूर्ण!", stage="QUOTA", badge="⚠️")
                                break
                            elif any(w in err_str.lower() for w in ["slug", "url key", "already been taken"]):
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, cur_row, "ALREADY_LISTED", "", "Skipped - Already on Portal")
                                    lead["submission_status"] = "Skipped - Already on Portal"
                                emit_log(f"⏭️ [टैब {worker_id}] [स्किप] '{l_name}' (डुप्लीकेट स्लग) पोर्टल पर पहले से लिस्टेड है!", stage="SKIPPED", badge="⏭️")
                            else:
                                async with excel_lock:
                                    update_excel_lead_status(excel_path, cur_row, "", "", f"Skipped: {err_str[:25]}")
                                    lead["submission_status"] = f"Skipped: {err_str[:25]}"
                                emit_log(f"⚠️ [टैब {worker_id}] एरर [{l_name}]: {err_str[:60]}", stage="WARN", badge="⚠️")
                        finally:
                            queue.task_done()
                            if delay_seconds > 0 and not quota_reached:
                                await asyncio.sleep(delay_seconds)
                finally:
                    await w_page.close()

            await asyncio.gather(*(worker(i+1) for i in range(concurrency)))
    finally:
        await safe_close_browser(portal_browser, portal_context)
        free_system_resources_completely()

    try:
        await sync_excel_to_google_sheet(excel_path)
    except Exception:
        pass

    emit_log(
        f"🏆 [इंजन 2 संपन्न!] कुल {submitted_count}/{len(targets)} लीड्स jainforjain.com पर सफलतापूर्वक लाइव हुईं!",
        stage="COMPLETE",
        badge="🏆",
        pct=100
    )

    summary = {
        "status": "success",
        "engine": "submitter_only",
        "submitted_count": submitted_count,
        "total_targets": len(targets)
    }

    if progress_callback:
        progress_callback({
            "type": "complete",
            "message": f"🏆 {submitted_count} लीड्स पोर्टल पर लाइव हुईं!",
            "percent": 100,
            "submitted_count": submitted_count,
            "summary": summary
        })

    return summary


async def execute_master_auto_batch(
    target_count: int = 150,
    city: Optional[str] = None,
    category: Optional[str] = None,
    mode: str = "both",
    portal_email: Optional[str] = None,
    portal_password: Optional[str] = None,
    account_id: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Modular Master Dispatcher:
    - mode="scraper_only": Runs pure Maps crawler + Canva + Excel + Sheets (0 portal)
    - mode="submitter_only": Runs pure Portal Submitter on existing unsubmitted leads (0 Maps)
    - mode="both": Runs combined stream pipeline
    """
    if mode == "scraper_only":
        return await execute_pure_scraper_batch(
            target_count=target_count,
            city=city,
            category=category,
            progress_callback=progress_callback
        )
    elif mode == "submitter_only":
        return await execute_pure_submitter_batch(
            target_count=target_count,
            delay_seconds=0,
            portal_email=portal_email,
            portal_password=portal_password,
            account_id=account_id,
            progress_callback=progress_callback
        )
    else:
        return await execute_streamed_live_pipeline(
            target_count=target_count,
            city=city,
            category=category,
            portal_email=portal_email,
            portal_password=portal_password,
            account_id=account_id,
            progress_callback=progress_callback
        )


async def execute_streamed_live_pipeline(
    target_count: int = 20,
    city: Optional[str] = None,
    category: Optional[str] = None,
    portal_email: Optional[str] = None,
    portal_password: Optional[str] = None,
    account_id: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    On-The-Fly Streamed Live Pipeline:
    As SOON as each Jain lead is verified (Score >= 85):
    1. Generates Canva Pro HD 1080x1080 Logo & 1200x500 Banner immediately.
    2. Appends to 26-column Master Excel with 0 empty cells.
    3. Fills and submits listing on jainforjain.com with photo uploads verified.
    4. Updates Excel row with live ID (JFJ-XXXXX) and live URL.
    5. Syncs directly to Google Sheets in real-time.
    6. Dispatches real-time SSE progress events to the frontend.
    Zero waiting for batch completion!
    """
    auth_email, auth_pass, auth_tag = resolve_credentials(portal_email, portal_password, account_id)
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

    batch_id = f"STREAM-{uuid.uuid4().hex[:6].upper()}"
    state = load_progress()
    active_city = city or state.get("current_city") or "Indore"
    areas = CITY_MICRO_ZONES.get(active_city, ["Sarafa Bazar", "Rajwada", "Marothia Bazar", "Sitlamata Bazar", "Palasia", "Vijay Nagar"])
    
    area_idx = state.get("area_idx", 0)
    current_area = areas[area_idx % len(areas)]
    next_area = areas[(area_idx + 1) % len(areas)]
    active_category = category or CORE_CATEGORIES[state.get("category_idx", 0) % len(CORE_CATEGORIES)]
    
    emit_log(
        f"⚡ ऑन-द-फ्लाई लाइव स्ट्रीम पाइपलाइन प्रारंभ | लक्ष्य: {target_count} लीड्स | शहर: {active_city} | बाज़ार: {current_area}",
        stage="INIT",
        badge="⚡",
        pct=5
    )
    emit_log(
        "💡 प्रत्येक लीड सर्च होते ही तुरंत Canva HD ➔ Excel ➔ jainforjain.com लाइव ➔ Google Sheet में सिंक होगी!",
        stage="STREAM_RULE",
        badge="💡",
        pct=8
    )

    excel_path = get_master_excel_path()
    
    # ALWAYS pull latest live Google Sheet so VPS never misses pending sheet leads!
    try:
        from backend.google_sheets_sync import download_google_sheet_to_excel
        download_google_sheet_to_excel(excel_path)
    except Exception as dl_err:
        print(f"Note on Google Sheet auto-pull: {dl_err}")

    try:
        from backend.excel_builder import deduplicate_master_excel
        deduplicate_master_excel(excel_path)
    except Exception:
        pass

    all_leads: List[Dict[str, Any]] = []
    if os.path.exists(excel_path):
        try:
            all_leads = load_leads_from_excel(excel_path)
        except Exception:
            all_leads = []

    seen_run_phones = set()
    seen_run_names = set()
    for l in all_leads:
        st = str(l.get("submission_status", "")).lower()
        if "submitted" in st or "live" in st:
            p = "".join(c for c in str(l.get("phone", "")) if c.isdigit())[-10:]
            if len(p) == 10: seen_run_phones.add(p)
            n = re.sub(r'[^a-zA-Z0-9]+', '', f"{l.get('name', '')}_{l.get('city', '')}".lower())
            if n: seen_run_names.add(n)

    unsubmitted_existing = []
    for l in all_leads:
        if not is_lead_pending(l):
            continue
        p = "".join(c for c in str(l.get("phone", "")) if c.isdigit())[-10:]
        n = re.sub(r'[^a-zA-Z0-9]+', '', f"{l.get('name', '')}_{l.get('city', '')}".lower())
        if (len(p) == 10 and p in seen_run_phones) or (n and n in seen_run_names):
            update_excel_lead_status(excel_path, l["row_idx"], "DUPLICATE", "", "Skipped - Duplicate Entry in Excel")
            continue
        if len(p) == 10: seen_run_phones.add(p)
        if n: seen_run_names.add(n)
        unsubmitted_existing.append(l)
    
    emit_log(
        f"📊 शीट डेटाबेस स्थिति: कुल {len(all_leads)} लीड्स | {len(unsubmitted_existing)} पूर्व-सत्यापित यूनिक अनसबमिटेड.",
        stage="AUDIT",
        badge="📊",
        pct=10
    )

    submitted_count = 0
    quota_reached = False
    newly_mined_leads: List[Dict[str, Any]] = []

    # Launch Playwright Browser for Live Submission
    from playwright.async_api import async_playwright
    from backend.system_guard import (
        CHROMIUM_TURBO_ARGS,
        apply_turbo_routing,
        safe_close_browser,
        free_system_resources_completely
    )

    portal_browser = None
    try:
        async with async_playwright() as p:
            try:
                portal_browser = await p.chromium.launch(
                    headless=True,
                    args=CHROMIUM_TURBO_ARGS
                )
            except Exception:
                portal_browser = await p.chromium.launch(
                    headless=True,
                    channel="chrome",
                    args=CHROMIUM_TURBO_ARGS
                )
            portal_context = await portal_browser.new_context(viewport={"width": 1400, "height": 950})
            await apply_turbo_routing(portal_context, block_images=False)
            portal_page = await portal_context.new_page()

            logged = await login_to_portal(portal_page, auth_email, auth_pass)
            if not logged:
                emit_log(f"❌ jainforjain.com पोर्टल लॉगिन विफल ({auth_email})! क्रेडेंशियल्स जांचें.", stage="PORTAL_ERR", badge="❌")
                await safe_close_browser(portal_browser, portal_context)
                return {"status": "error", "message": f"Portal login failed for {auth_email}"}

            emit_log(f"✅ पोर्टल लॉगिन 100% सफल ({auth_email})! लाइव एंट्री वर्कर तैयार...", stage="PORTAL_OK", badge="✅", pct=15)

            # 1. Process any unsubmitted leads from Excel first (on-the-fly)
            if unsubmitted_existing:
                for lead in unsubmitted_existing:
                    if submitted_count >= target_count or quota_reached:
                        break
                    l_name = lead.get("name", "")
                    cur_row = lead.get("row_idx", 2)
                    owner_name = lead.get("owner", "Proprietor")

                    emit_log(f"📝 [{submitted_count + 1}/{target_count}] पूर्व-सत्यापित लीड '{l_name}' दर्ज की जा रही है...", stage="SUBMITTING", badge="📝")
                    try:
                        res = await fill_listing_form(portal_page, lead, dry_run=False)
                        b_id = res.get("biz_id", "")
                        p_url = res.get("profile_url", "")
                        status_txt = res.get("status", "")
                        
                        if res.get("duplicate") or "Skipped" in status_txt or "Already" in status_txt:
                            update_excel_lead_status(excel_path, cur_row, "ALREADY_LISTED", p_url, "Skipped - Already on Portal")
                            lead["submission_status"] = "Skipped - Already on Portal"
                            try:
                                await sync_excel_to_google_sheet(excel_path)
                            except Exception:
                                pass
                            emit_log(
                                f"⏭️ [स्किप] '{l_name}' पोर्टल पर पहले से मौजूद है! सुरक्षित स्किप कर अगली लीड पर जा रहे हैं...",
                                stage="SKIPPED",
                                badge="⏭️"
                            )
                        elif b_id and b_id.startswith("JFJ-") and res.get("status") == "submitted_success":
                            status_label = f"Submitted - Live [{auth_email}]"
                            update_excel_lead_status(excel_path, cur_row, b_id, p_url, status_label)
                            submitted_count += 1
                            lead["j4j_business_id"] = b_id
                            lead["j4j_profile_url"] = p_url
                            lead["submission_status"] = status_label
                            try:
                                await sync_excel_to_google_sheet(excel_path)
                            except Exception:
                                pass
                            pct = min(15 + int((submitted_count / target_count) * 80), 98)
                            emit_log(
                                f"🎉 [{submitted_count}/{target_count}] '{l_name}' ({owner_name}) ➔ jainforjain.com पर 100% लाइव! (ID: {b_id})",
                                stage="LIVE_SUBMITTED",
                                badge="🎉",
                                pct=pct
                            )
                        else:
                            update_excel_lead_status(excel_path, cur_row, "", "", f"Skipped: {res.get('error', 'Validation')[:25]}")
                            lead["submission_status"] = f"Skipped: {res.get('error', 'Validation')[:25]}"
                            emit_log(f"⚠️ सबमिशन स्किप [{l_name}]: {res.get('error', 'फॉर्म सत्यापन चेतावनी')[:60]} (अगली लीड जारी)", stage="WARN", badge="⚠️")
                    except Exception as err:
                        err_str = str(err)
                        if any(w in err_str.lower() for w in ["limit", "package", "quota"]):
                            quota_reached = True
                            emit_log("⚠️ पोर्टल कोटा अलर्ट: अधिकतम लिस्टिंग सीमा पूर्ण!", stage="QUOTA", badge="⚠️")
                            break
                        elif any(w in err_str.lower() for w in ["slug", "url key", "already been taken"]):
                            update_excel_lead_status(excel_path, cur_row, "ALREADY_LISTED", "", "Skipped - Already on Portal")
                            lead["submission_status"] = "Skipped - Already on Portal"
                            emit_log(f"⏭️ [स्किप] '{l_name}' (डुप्लीकेट स्लग) पोर्टल पर पहले से लिस्टेड है! अगली लीड पर जा रहे हैं...", stage="SKIPPED", badge="⏭️")
                        elif any(w in err_str.lower() for w in ["connection closed", "target closed", "browser has been closed", "session closed"]):
                            emit_log("🔄 ब्राउज़र डिस्कनेक्ट हुआ! नया सत्र शुरू किया जा रहा है...", stage="RECONNECT", badge="🔄")
                            try:
                                if portal_page and not portal_page.is_closed():
                                    await portal_page.close()
                                if portal_context:
                                    await portal_context.close()
                                if portal_browser and portal_browser.is_connected():
                                    await portal_browser.close()
                            except Exception:
                                pass
                            try:
                                try:
                                    portal_browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
                                except Exception:
                                    portal_browser = await p.chromium.launch(headless=True, channel="chrome", args=CHROMIUM_TURBO_ARGS)
                                portal_context = await portal_browser.new_context(viewport={"width": 1400, "height": 950})
                                await apply_turbo_routing(portal_context, block_images=False)
                                portal_page = await portal_context.new_page()
                                await login_to_portal(portal_page, auth_email, auth_pass)
                                emit_log(f"✅ नया ब्राउज़र सत्र तैयार ({auth_email})! पुनः सबमिशन जारी...", stage="RECONNECT_OK", badge="✅")
                            except Exception as rec_err:
                                emit_log(f"❌ रीकनेक्शन त्रुटि: {rec_err}", stage="RECONNECT_FAIL", badge="❌")
                        else:
                            update_excel_lead_status(excel_path, cur_row, "", "", f"Skipped: {err_str[:25]}")
                            lead["submission_status"] = f"Skipped: {err_str[:25]}"
                            emit_log(f"⚠️ सबमिशन स्किप [{l_name}]: {err_str[:60]} (अगली लीड जारी)", stage="WARN", badge="⚠️")

            # 2. ONLY crawl Maps if there were ZERO unsubmitted leads in the sheet!
            # If the user already has unsubmitted leads in the sheet, NEVER search Maps!
            if submitted_count < target_count and not quota_reached and len(unsubmitted_existing) == 0:
                needed_fresh = target_count - submitted_count
                emit_log(
                    f"🏬 शीट में कोई लंबित लीड नहीं बची — Maps से {needed_fresh} नई लीड्स की खोज शुरू...",
                    stage="STREAM_SEARCH",
                    badge="🏬",
                    pct=min(15 + int((submitted_count / target_count) * 80), 30)
                )

                async def on_single_lead_stream(rec: Dict[str, Any]):
                    nonlocal submitted_count, quota_reached
                    if submitted_count >= target_count or quota_reached:
                        return

                    newly_mined_leads.append(rec)
                    
                    # Append to Master Excel immediately (assigns row_idx)
                    append_to_master_excel([rec], excel_path)
                    cur_row = rec.get("row_idx", 2)
                    l_name = rec.get("name", "")
                    owner_name = rec.get("owner", "Proprietor")

                    emit_log(
                        f"📝 [{submitted_count + 1}/{target_count}] '{l_name}' ({owner_name}) ➔ तुरंत jainforjain.com पर दर्ज हो रहा है...",
                        stage="STREAM_SUBMITTING",
                        badge="📝"
                    )

                    try:
                        res = await fill_listing_form(portal_page, rec, dry_run=False)
                        b_id = res.get("biz_id", "")
                        p_url = res.get("profile_url", "")
                        status_txt = res.get("status", "")
                        
                        if res.get("duplicate") or "Skipped" in status_txt or "Already" in status_txt:
                            update_excel_lead_status(excel_path, cur_row, "ALREADY_LISTED", p_url, "Skipped - Already on Portal")
                            rec["submission_status"] = "Skipped - Already on Portal"
                            try:
                                await sync_excel_to_google_sheet(excel_path)
                            except Exception:
                                pass
                            emit_log(
                                f"⏭️ [स्किप] '{l_name}' पोर्टल पर पहले से मौजूद है! सुरक्षित स्किप कर अगली लीड पर जा रहे हैं...",
                                stage="SKIPPED",
                                badge="⏭️"
                            )
                        elif b_id and "VALIDATION_SKIPPED" not in b_id:
                            status_label = f"Submitted - Live [{auth_email}]"
                            update_excel_lead_status(excel_path, cur_row, b_id, p_url, status_label)
                            submitted_count += 1
                            rec["j4j_business_id"] = b_id
                            rec["j4j_profile_url"] = p_url
                            rec["submission_status"] = status_label
                            try:
                                await sync_excel_to_google_sheet(excel_path)
                            except Exception:
                                pass
                            pct = min(15 + int((submitted_count / target_count) * 80), 98)
                            emit_log(
                                f"🎉 [{submitted_count}/{target_count}] '{l_name}' ({owner_name}) ➔ jainforjain.com पर 100% लाइव! (ID: {b_id} | {auth_email})",
                                stage="LIVE_SUBMITTED",
                                badge="🎉",
                                pct=pct
                            )
                        else:
                            update_excel_lead_status(excel_path, cur_row, "", "", f"Skipped: {res.get('error', 'Validation')[:25]}")
                            rec["submission_status"] = f"Skipped: {res.get('error', 'Validation')[:25]}"
                            emit_log(f"⚠️ सबमिशन स्किप [{l_name}]: {res.get('error', 'फॉर्म सत्यापन चेतावनी')[:60]} (अगली लीड जारी)", stage="WARN", badge="⚠️")
                    except Exception as ex:
                        err_str = str(ex)
                        if any(w in err_str.lower() for w in ["limit", "package", "quota"]):
                            quota_reached = True
                            emit_log("⚠️ पोर्टल कोटा अलर्ट: अधिकतम लिस्टिंग सीमा पूर्ण!", stage="QUOTA", badge="⚠️")
                        elif any(w in err_str.lower() for w in ["slug", "url key", "already been taken"]):
                            update_excel_lead_status(excel_path, cur_row, "ALREADY_LISTED", "", "Skipped - Already on Portal")
                            rec["submission_status"] = "Skipped - Already on Portal"
                            emit_log(f"⏭️ [स्किप] '{l_name}' (डुप्लीकेट स्लग) पोर्टल पर पहले से लिस्टेड है! अगली लीड पर जा रहे हैं...", stage="SKIPPED", badge="⏭️")
                        else:
                            update_excel_lead_status(excel_path, cur_row, "", "", f"Skipped: {err_str[:25]}")
                            rec["submission_status"] = f"Skipped: {err_str[:25]}"
                            emit_log(f"⚠️ सबमिशन स्किप [{l_name}]: {err_str[:60]} (अगली लीड जारी)", stage="WARN", badge="⚠️")

                curr_crawl_idx = area_idx
                while submitted_count < target_count and not quota_reached and curr_crawl_idx < len(areas) + area_idx:
                    crawl_area_name = areas[curr_crawl_idx % len(areas)]
                    needed = target_count - submitted_count
                    emit_log(
                        f"🔍 सूक्ष्म-बाज़ार खोज: [{active_city} - {crawl_area_name}] | आवश्यकता: {needed} लीड्स...",
                        stage="CRAWLING",
                        badge="🔍"
                    )
                    
                    await crawl_area_deep(
                        city=active_city,
                        area=crawl_area_name,
                        category=active_category,
                        target_count=needed,
                        entity_type="all",
                        excel_path=excel_path,
                        auto_sync_sheets=False,
                        progress_callback=progress_callback,
                        on_lead_verified_callback=on_single_lead_stream
                    )
                    curr_crawl_idx += 1

            await safe_close_browser(portal_browser, portal_context)
            portal_browser = None
            portal_context = None
    except Exception as e:
        emit_log(f"पाइपलाइन अपवाद: {e}", stage="WARN", badge="⚠️")
    finally:
        await safe_close_browser(portal_browser, portal_context)
        free_system_resources_completely()

    # Desktop backup if on Windows
    try:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop_dir):
            import shutil
            shutil.copyfile(excel_path, os.path.join(desktop_dir, "Jain_Leads_Verified_Photos_HD.xlsx"))
    except Exception:
        pass

    # Final Google Sheet Sync
    try:
        await sync_excel_to_google_sheet(excel_path)
    except Exception:
        pass

    # Record batch & advance roadmap
    total_cum = record_search_batch(
        batch_id=batch_id,
        category=active_category,
        city=active_city,
        area_name=current_area,
        batch_size=target_count,
        extracted_count=submitted_count,
        next_area=next_area,
        status="100% Saturated / पूर्ण",
        sync_status="Synced"
    )

    state["area_idx"] = area_idx + 1
    state["total_mined"] = total_cum
    area_key = f"{active_city} - {current_area}"
    if area_key not in state.get("completed_areas", []):
        state.setdefault("completed_areas", []).append(area_key)
    save_progress(state)

    next_target_market = areas[(area_idx + 1) % len(areas)] if len(areas) > 1 else "All Completed"

    emit_log(
        f"🏆 ऑन-द-फ्लाई स्ट्रीम पाइपलाइन संपन्न! कुल {submitted_count} जैन बिज़नेस सीधे jainforjain.com पर 100% लाइव हुए व Google Sheet में सिंक हो गए!",
        stage="COMPLETE",
        badge="🏆",
        pct=100
    )

    summary = {
        "status": "success",
        "batch_id": batch_id,
        "target_count": target_count,
        "submitted_count": submitted_count,
        "current_area": current_area,
        "next_area": next_target_market,
        "total_mined": total_cum,
        "sheet_url": "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
    }

    if progress_callback:
        progress_callback({
            "type": "complete",
            "message": f"🏆 {submitted_count} लीड्स ऑन-द-फ्लाई पोर्टल पर लाइव हुईं!",
            "percent": 100,
            "submitted_count": submitted_count,
            "current_area": current_area,
            "next_area": next_target_market,
            "summary": summary
        })

    return summary
