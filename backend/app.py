"""
FastAPI Server for JainBiz Lead Miner.
Provides SSE (Server-Sent Events) for real-time progress streaming,
task dispatching, and 1-click Excel file downloads.
"""

import os
import sys
import uuid
import json
import asyncio
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.scraper import scrape_google_maps_task
from backend.matrix import INDIA_HUBS
from backend.config import get_master_excel_path

app = FastAPI(title="JainBiz Lead Miner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Task Store
TASKS: Dict[str, Dict[str, Any]] = {}
TASK_LISTENERS: Dict[str, List[asyncio.Queue]] = {}

class ScanRequest(BaseModel):
    category: str = "Jewellers"
    location: str = "Gujarat"
    entity_type: str = "commercial"
    include_sacred: bool = True
    include_surnames: bool = True
    include_photos: bool = True
    max_firms: int = 100

@app.post("/api/sync-google-sheets")
async def api_sync_google_sheets():
    """Manually triggers instant synchronization to the user's live Google Sheet."""
    from backend.google_sheets_sync import sync_excel_to_google_sheet
    excel_path = get_master_excel_path()
    success = await sync_excel_to_google_sheet(excel_path)
    return {
        "success": success,
        "sheet_url": "https://docs.google.com/spreadsheets/d/1QjY6a_D64dGWAn0VApB8xgqwsygqXHctOQaa7AFAjQw/edit?usp=sharing"
    }

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the main frontend dashboard."""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(frontend_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/hubs")
async def get_geography_hubs():
    """Returns available Indian states and cities."""
    return INDIA_HUBS

@app.post("/api/start-scan")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """Initializes and runs a background lead mining task."""
    task_id = str(uuid.uuid4())
    
    TASKS[task_id] = {
        "status": "running",
        "category": req.category,
        "location": req.location,
        "excel_path": None,
        "filename": None,
        "records": []
    }
    TASK_LISTENERS[task_id] = []

    def dispatch_event(event_data: Dict[str, Any]):
        listeners = TASK_LISTENERS.get(task_id, [])
        for q in listeners:
            try:
                q.put_nowait(event_data)
            except Exception:
                pass

    async def runner():
        try:
            result = await scrape_google_maps_task(
                task_id=task_id,
                category=req.category,
                location_scope=req.location,
                include_sacred=req.include_sacred,
                include_surnames=req.include_surnames,
                include_photos=req.include_photos,
                max_firms_target=req.max_firms,
                progress_callback=dispatch_event
            )
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["excel_path"] = result.get("excel_path")
            TASKS[task_id]["filename"] = result.get("filename")
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            dispatch_event({
                "type": "error",
                "message": str(e)
            })

    background_tasks.add_task(runner)
    return {"task_id": task_id, "status": "started"}

class Pipeline10xRequest(BaseModel):
    city: str = "Indore"
    category: str = "Jewellers"
    count: int = 10
    live_submit: bool = True

@app.post("/api/start-pipeline-10x")
async def start_pipeline_10x(req: Pipeline10xRequest, background_tasks: BackgroundTasks):
    """Initializes and runs the autonomous 10X pipeline with live event dispatching."""
    from backend.pipeline import run_autonomous_10x_pipeline
    task_id = str(uuid.uuid4())
    
    TASKS[task_id] = {
        "status": "running",
        "city": req.city,
        "category": req.category,
        "count": req.count,
        "records": []
    }
    TASK_LISTENERS[task_id] = []

    def dispatch_event(event_data: Dict[str, Any]):
        listeners = TASK_LISTENERS.get(task_id, [])
        for q in listeners:
            try:
                q.put_nowait(event_data)
            except Exception:
                pass

    async def pipeline_runner():
        try:
            res = await run_autonomous_10x_pipeline(
                task_id=task_id,
                city=req.city,
                category=req.category,
                count=req.count,
                live_submit=req.live_submit,
                progress_callback=dispatch_event
            )
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["result"] = res
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            dispatch_event({
                "type": "error",
                "message": str(e)
            })

    background_tasks.add_task(pipeline_runner)
    return {"task_id": task_id, "status": "started"}

@app.get("/api/stream-progress/{task_id}")
async def stream_progress(task_id: str, request: Request):
    """Server-Sent Events (SSE) stream for live scan progress."""
    queue = asyncio.Queue()
    
    if task_id not in TASK_LISTENERS:
        TASK_LISTENERS[task_id] = []
    TASK_LISTENERS[task_id].append(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait up to 25s for next event or heartbeat
                    data = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    if data.get("type") in ["complete", "error"]:
                        break
                except asyncio.TimeoutError:
                    # Heartbeat ping to keep SSE connection active
                    yield ": ping\n\n"
        finally:
            if task_id in TASK_LISTENERS and queue in TASK_LISTENERS[task_id]:
                TASK_LISTENERS[task_id].remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/current-status")
async def get_current_status():
    """Returns current saturation and submission statistics."""
    from backend.saturation_engine import load_progress
    from backend.auto_entry_bot import load_leads_from_excel
    excel_path = get_master_excel_path()
    
    progress = load_progress()
    leads = []
    if os.path.exists(excel_path):
        try:
            leads = load_leads_from_excel(excel_path)
        except Exception:
            pass
            
    submitted = [l for l in leads if "Submitted" in l.get("submission_status", "")]
    ready = [l for l in leads if l.get("submission_status") in ["Ready to Submit", "", None]]
    
    return {
        "city": progress.get("current_city", "Indore"),
        "area_idx": progress.get("area_idx", 0),
        "total_leads": len(leads),
        "submitted_leads": len(submitted),
        "ready_leads": len(ready),
        "completed_areas": progress.get("completed_areas", [])
    }

@app.get("/api/leads")
async def get_master_leads():
    """Returns all leads from the master Excel workbook."""
    from backend.auto_entry_bot import load_leads_from_excel
    excel_path = get_master_excel_path()
    leads = []
    if os.path.exists(excel_path):
        try:
            leads = load_leads_from_excel(excel_path)
        except Exception:
            pass
    return {"leads": leads, "total": len(leads)}

class ExtractLeadsRequest(BaseModel):
    city: str = "Indore"
    category: str = "Jewellers"
    count: int = 10

@app.post("/api/extract-leads")
async def extract_leads(req: ExtractLeadsRequest, background_tasks: BackgroundTasks):
    """Step 1: 1-Click extraction of leads, saves to Excel, syncs to Google Sheets, streams progress."""
    from backend.pipeline import run_autonomous_10x_pipeline
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "running",
        "city": req.city,
        "category": req.category,
        "count": req.count,
        "records": []
    }
    TASK_LISTENERS[task_id] = []

    def dispatch_event(event_data: Dict[str, Any]):
        listeners = TASK_LISTENERS.get(task_id, [])
        for q in listeners:
            try:
                q.put_nowait(event_data)
            except Exception:
                pass

    async def runner():
        try:
            res = await run_autonomous_10x_pipeline(
                task_id=task_id,
                city=req.city,
                category=req.category,
                count=req.count,
                live_submit=False,
                progress_callback=dispatch_event
            )
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["result"] = res
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            dispatch_event({
                "type": "error",
                "message": str(e)
            })

    background_tasks.add_task(runner)
    return {"task_id": task_id, "status": "started"}

class TimerSubmitRequest(BaseModel):
    delay_seconds: int = 60
    limit: int = 5
    city_filter: str = ""

@app.post("/api/start-timer-submit")
async def start_timer_submit(req: TimerSubmitRequest, background_tasks: BackgroundTasks):
    """Step 2: 1-Click scheduled submit with configurable timer, photo uploads, live sheet sync."""
    from backend.scheduled_submitter import run_scheduled_submission, SUBMISSION_CONTROLS
    if SUBMISSION_CONTROLS.get("is_running"):
        return {"status": "already_running", "message": "टाइमर सबमिशन पहले से चल रहा है"}
    
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {"status": "running"}
    TASK_LISTENERS[task_id] = []

    def dispatch_event(event_data: Dict[str, Any]):
        listeners = TASK_LISTENERS.get(task_id, [])
        for q in listeners:
            try:
                q.put_nowait(event_data)
            except Exception:
                pass

    async def runner():
        try:
            res = await run_scheduled_submission(
                delay_seconds=req.delay_seconds,
                limit=req.limit,
                city_filter=req.city_filter if req.city_filter else None,
                progress_callback=dispatch_event
            )
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["result"] = res
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            dispatch_event({
                "type": "error",
                "message": str(e)
            })

    background_tasks.add_task(runner)
    return {"task_id": task_id, "status": "started"}

@app.post("/api/stop-timer-submit")
async def stop_timer():
    """Stops the running scheduled submitter."""
    from backend.scheduled_submitter import stop_scheduled_submission
    stop_scheduled_submission()
    return {"status": "stopped", "message": "टाइमर रोकने का निर्देश दे दिया गया है"}

@app.get("/api/timer-status")
async def get_timer_status():
    """Returns the live state and countdown of the scheduled submitter."""
    from backend.scheduled_submitter import SUBMISSION_CONTROLS
    return SUBMISSION_CONTROLS

@app.get("/api/inspect-portal")
async def inspect_portal():
    """Step 3: 1-Click inspect portal listings, approval status and live screenshot without manual login."""
    from backend.portal_inspector import inspect_portal_account
    result = await inspect_portal_account()
    return result

@app.get("/api/portal-screenshot")
async def get_portal_screenshot():
    """Returns the live full-page screenshot of jainforjain.com member portal."""
    from backend.portal_inspector import SCREENSHOT_PATH
    if os.path.exists(SCREENSHOT_PATH):
        return FileResponse(SCREENSHOT_PATH, media_type="image/png")
    return {"error": "Screenshot not yet generated"}

class EntryRequest(BaseModel):
    limit: int = 5
    live: bool = True

@app.post("/api/start-portal-entry")
async def start_portal_entry(req: EntryRequest, background_tasks: BackgroundTasks):
    """Triggers autonomous entry into jainforjain.com."""
    from backend.auto_entry_bot import run_auto_entry_batch
    from backend.saturation_engine import load_progress
    excel_path = get_master_excel_path()
    prog = load_progress()
    active_city = prog.get("current_city", "Indore")
    
    async def entry_runner():
        await run_auto_entry_batch(
            excel_path=excel_path,
            dry_run=not req.live,
            limit=req.limit,
            city_filter=active_city
        )
        
    background_tasks.add_task(entry_runner)
    return {
        "status": "started",
        "mode": "LIVE" if req.live else "DRY-RUN",
        "limit": req.limit
    }

# ==================== CANVA CONNECTOR & MARKETING SUITE ====================
from backend.canva_connector import CanvaConnector
canva_conn = CanvaConnector()

@app.get("/api/canva/templates")
async def get_canva_templates():
    """Returns available Canva marketing templates for Indian & Jain businesses."""
    return {
        "templates": [
            {"id": "visiting_card", "title": "Digital Visiting Card (vCard)", "size": "1050x600", "desc": "व्यक्तिगत व व्यावसायिक विजिटिंग कार्ड"},
            {"id": "whatsapp_flyer", "title": "WhatsApp Story / Flyer", "size": "1080x1920", "desc": "फुल-स्क्रीन स्टेटस व स्टोरी पोस्टर"},
            {"id": "festival_greeting", "title": "Festival Greeting Card", "size": "1080x1080", "desc": "पर्युषण, महावीर जयंती, नववर्ष बधाई"},
            {"id": "social_banner", "title": "Social Header Banner", "size": "1200x400", "desc": "फेसबुक व वेबसाइट बैनर"},
        ]
    }

@app.get("/api/canva/flyer/{filename}")
async def serve_canva_flyer(filename: str):
    """Serves generated Canva marketing flyer image."""
    flyer_path = os.path.join(canva_conn.output_dir, filename)
    if os.path.exists(flyer_path):
        return FileResponse(flyer_path, media_type="image/png")
    return {"error": "Flyer not found"}

@app.get("/api/canva/all-flyers")
async def get_all_canva_flyers():
    """Returns all generated Canva flyers with metadata and deep Canva links."""
    defaults = [
        {"id": "252", "name": "श्री पार्श्वनाथ दिगंबर जैन मंदिर", "cat": "धार्मिक एवं सांस्कृतिक केंद्र", "loc": "राजवाड़ा, इंदौर", "phone": "+91 94250 55555"},
        {"id": "253", "name": "कांच मंदिर (Glass Temple)", "cat": "ऐतिहासिक धरोहर एवं धार्मिक स्थल", "loc": "इतवारिया बाज़ार, इंदौर", "phone": "+91 98260 12345"},
        {"id": "254", "name": "श्री दिगंबर जैन मारवाड़ी बड़ा मंदिर", "cat": "धार्मिक एवं सामाजिक केंद्र", "loc": "छत्रीबाग, इंदौर", "phone": "+91 98260 34567"},
        {"id": "255", "name": "दादा बाड़ी जैन धर्मशाला", "cat": "तीर्थयात्री सेवा एवं धर्मशाला", "loc": "साउथ तुकोगंज, इंदौर", "phone": "+91 98260 45678"},
        {"id": "256", "name": "लाल मंदिर (Lal Mandir)", "cat": "धार्मिक एवं ऐतिहासिक धरोहर", "loc": "मल्हारगंज, इंदौर", "phone": "+91 98260 56789"}
    ]
    
    items = []
    for d in defaults:
        fn = f"flyer_{d['id']}.png"
        fp = os.path.join(canva_conn.output_dir, fn)
        clinks = canva_conn.get_canva_template_links(d["name"], d["cat"])
        items.append({
            "listing_id": d["id"],
            "business_name": d["name"],
            "category": d["cat"],
            "location": d["loc"],
            "phone": d["phone"],
            "filename": fn,
            "url": f"/api/canva/flyer/{fn}" if os.path.exists(fp) else None,
            "canva_links": clinks
        })
    return {"flyers": items}

class GenerateFlyerRequest(BaseModel):
    listing_id: str
    business_name: str
    category: str = "Business"
    location: str = "Indore"
    phone: str = ""
    tagline: str = "जैन समुदाय का प्रतिष्ठित एवं प्रमाणित प्रतिष्ठान"

@app.post("/api/canva/generate-flyer")
async def generate_canva_flyer_api(req: GenerateFlyerRequest):
    """Generates an HD Canva marketing flyer on demand for any business."""
    photos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "indore_photos")
    photo_path = os.path.join(photos_dir, f"{req.listing_id}_photo.jpg")
    if not os.path.exists(photo_path):
        photo_path = None
    
    res = await canva_conn.generate_branded_marketing_flyer_async(
        listing_id=req.listing_id,
        business_name=req.business_name,
        category=req.category,
        location=req.location,
        phone=req.phone,
        photo_path=photo_path,
        tagline=req.tagline
    )
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

