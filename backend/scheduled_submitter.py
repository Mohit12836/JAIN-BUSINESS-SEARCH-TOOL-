"""
Scheduled Auto-Submitter for jainforjain.com.
Submits ready leads one-by-one with a configurable timer delay (e.g., 1 min, 2 min, 5 min),
uploads photos, updates the Master Excel and Google Sheets with JFJ IDs,
and streams countdown & progress to the UI.
"""

import os
import sys
import asyncio
import datetime
from typing import Dict, Any, List, Optional, Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import get_master_excel_path
from backend.auto_entry_bot import (
    login_to_portal,
    fill_listing_form,
    load_leads_from_excel,
    update_excel_lead_status,
    DEFAULT_USER,
    DEFAULT_PASS
)
from backend.google_sheets_sync import sync_excel_to_google_sheet
from playwright.async_api import async_playwright

# Global control flag to allow pausing/stopping the submitter
SUBMISSION_CONTROLS = {
    "is_running": False,
    "stop_requested": False,
    "current_lead": "",
    "seconds_remaining": 0
}

def stop_scheduled_submission():
    """Signals the running submitter to stop after the current step."""
    SUBMISSION_CONTROLS["stop_requested"] = True

async def run_scheduled_submission(
    delay_seconds: int = 60,
    limit: int = 5,
    city_filter: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Submits leads with a real-time timer delay between each submission.
    """
    excel_path = get_master_excel_path()
    SUBMISSION_CONTROLS["is_running"] = True
    SUBMISSION_CONTROLS["stop_requested"] = False

    def emit_event(event_type: str, data: Dict[str, Any]):
        if progress_callback:
            payload = {"type": event_type, "timestamp": datetime.datetime.now().strftime("%H:%M:%S")}
            payload.update(data)
            progress_callback(payload)

    def emit_log(msg: str, stage: str = "INFO", badge: str = "ℹ️"):
        emit_event("log", {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "stage": stage,
            "badge": badge,
            "message": msg
        })

    emit_log(f"🚀 शेड्यूल्ड ऑटो-सबमिशन प्रारंभ: टाइमर = {delay_seconds} सेकंड | सीमा = {limit} लीड्स", stage="SUBMIT_START", badge="🚀")

    leads = load_leads_from_excel(excel_path)
    ready_leads = [l for l in leads if l.get("submission_status") in ["Ready to Submit", "", None]]

    if city_filter:
        city_leads = [l for l in ready_leads if city_filter.lower() in str(l.get("city", "")).lower()]
        other_leads = [l for l in ready_leads if city_filter.lower() not in str(l.get("city", "")).lower()]
        ready_leads = city_leads + other_leads

    if not ready_leads:
        emit_log("✓ कोई भी लीड सबमिशन के लिए लंबित नहीं है। सभी लीड्स पहले ही सबमिट हो चुकी हैं!", stage="INFO", badge="✓")
        SUBMISSION_CONTROLS["is_running"] = False
        return {"status": "no_ready_leads", "submitted": 0}

    targets = ready_leads[:limit]
    emit_log(f"📋 कुल {len(targets)} तैयार लीड्स सबमिशन के लिए कतार में हैं...", stage="INFO", badge="📋")

    submitted_count = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        emit_log("🔐 jainforjain.com पोर्टल पर लॉगिन किया जा रहा है...", stage="PORTAL_AUTH", badge="🔐")
        logged_in = await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        if not logged_in:
            emit_log("❌ पोर्टल लॉगिन विफल। कृपया क्रेडेंशियल्स जांचें।", stage="PORTAL_ERR", badge="❌")
            await browser.close()
            SUBMISSION_CONTROLS["is_running"] = False
            return {"status": "login_failed", "submitted": 0}

        emit_log("✅ पोर्टल लॉगिन सफल! टाइमर के अनुसार 1-by-1 फॉर्म सबमिशन शुरू...", stage="PORTAL_OK", badge="✅")

        for idx, lead in enumerate(targets, start=1):
            if SUBMISSION_CONTROLS["stop_requested"]:
                emit_log("⏹️ यूज़र द्वारा टाइमर रोक दिया गया (Stop Requested).", stage="STOPPED", badge="⏹️")
                break

            lead_name = lead.get("name", "")
            lead_row = lead.get("row_idx", 0)
            SUBMISSION_CONTROLS["current_lead"] = lead_name

            emit_log(f"📝 [{idx}/{len(targets)}] फॉर्म भरा जा रहा है: '{lead_name}' (फ़ोटो व विवरण सहित)...", stage="PORTAL_FILL", badge="📝")
            emit_event("progress", {
                "percent": int((idx - 1) / len(targets) * 90),
                "message": f"[{idx}/{len(targets)}] {lead_name} फॉर्म सबमिट हो रहा है..."
            })

            try:
                res = await fill_listing_form(page, lead, dry_run=False)
                biz_id = res.get("biz_id", "")
                profile_url = res.get("profile_url", "")

                if biz_id:
                    update_excel_lead_status(excel_path, lead_row, biz_id, profile_url, "Submitted - Live")
                    submitted_count += 1
                    
                    emit_log(f"🎉 [{idx}/{len(targets)}] सबमिट सफल! ID: {biz_id} | 🔗 {profile_url}", stage="PORTAL_SUBMITTED", badge="🎉")
                    
                    # Real-time lead update event
                    lead["j4j_business_id"] = biz_id
                    lead["j4j_profile_url"] = profile_url
                    lead["submission_status"] = "Submitted - Live"
                    emit_event("lead_updated", {
                        "row_idx": lead_row,
                        "biz_id": biz_id,
                        "profile_url": profile_url,
                        "name": lead_name
                    })

                    # Trigger instant Google Sheet sync for this updated row
                    try:
                        await sync_excel_to_google_sheet(excel_path)
                        emit_log(f"📊 Google Sheet में ID {biz_id} तुरंत अपडेट हो गई!", stage="SHEET_OK", badge="📊")
                    except Exception as s_err:
                        emit_log(f"⚠️ Google Sheet सिंक सूचना: {s_err}", stage="SHEET_WARN", badge="⚠️")

            except Exception as sub_err:
                err_str = str(sub_err)
                if any(w in err_str.lower() for w in ["limit", "package", "maximum listing", "quota"]):
                    emit_log("⚠️ पोर्टल अलर्ट: फ़्री पैकेज लिस्टिंग कोटा पूरा हो चुका है (अधिकतम 5 लिस्टिंग्स)।", stage="QUOTA_LIMIT", badge="⚠️")
                    emit_log("💡 बाकी लीड्स Excel और Google Sheet में 'Ready to Submit' स्थिति में सुरक्षित हैं।", stage="INFO", badge="💡")
                    break
                else:
                    emit_log(f"⚠️ सबमिशन त्रुटि [{lead_name}]: {err_str[:90]}", stage="PORTAL_WARN", badge="⚠️")

            # TIMER DELAY: If more leads remain and not stopped, wait delay_seconds with live countdown!
            if idx < len(targets) and not SUBMISSION_CONTROLS["stop_requested"] and delay_seconds > 0:
                next_name = targets[idx].get("name", "")
                emit_log(f"⏱️ टाइमर सक्रिय: अगली लीड '{next_name}' {delay_seconds} सेकंड में भरी जाएगी...", stage="TIMER_WAIT", badge="⏱️")
                
                for remaining in range(delay_seconds, 0, -1):
                    if SUBMISSION_CONTROLS["stop_requested"]:
                        break
                    SUBMISSION_CONTROLS["seconds_remaining"] = remaining
                    emit_event("countdown", {
                        "seconds_remaining": remaining,
                        "next_lead": next_name,
                        "completed": idx,
                        "total": len(targets)
                    })
                    await asyncio.sleep(1.0)

                SUBMISSION_CONTROLS["seconds_remaining"] = 0

        await browser.close()

    SUBMISSION_CONTROLS["is_running"] = False
    SUBMISSION_CONTROLS["stop_requested"] = False

    emit_log(
        f"🏁 शेड्यूल्ड सबमिशन पूर्ण! कुल सबमिट: {submitted_count}/{len(targets)} लीड्स। Google Sheet अपडेट हो चुकी है।",
        stage="COMPLETE",
        badge="🏆"
    )
    emit_event("complete", {
        "message": f"✓ सबमिशन पूर्ण! कुल {submitted_count} लीड्स पोर्टल पर सबमिट हुईं और Google Sheet में ID अपडेट हो गई।",
        "submitted_count": submitted_count
    })

    return {
        "status": "completed",
        "submitted_count": submitted_count
    }

