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
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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

@app.get("/health")
@app.get("/api/ping")
async def health_check():
    """Lightweight 24/7 liveness check for UptimeRobot / Cron-job.org and hybrid status."""
    from backend.config import is_cloud_environment
    from backend.saturation_engine import load_progress
    prog = load_progress()
    return {
        "status": "healthy",
        "environment": "Online Cloud (Render/VPS 24/7)" if is_cloud_environment() else "Offline Local PC",
        "current_city": prog.get("current_city", "Jaipur"),
        "completed_areas_count": len(prog.get("completed_areas", [])),
        "total_mined_leads": prog.get("total_mined", 0)
    }

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

# ==================== NEXT BATCH & SEARCH TRACKER ENDPOINTS ====================
class NextBatchRequest(BaseModel):
    batch_size: int = 50
    category: str = ""
    city: str = "Indore"

@app.get("/api/search-history")
async def api_get_search_history():
    """Returns all recorded search batches and area coverage history."""
    from backend.database import get_search_history
    history = get_search_history()
    return {"history": history, "total_batches": len(history)}

@app.post("/api/extract-next-batch")
async def api_extract_next_batch(req: NextBatchRequest, background_tasks: BackgroundTasks):
    """
    Extracts next sequential batch (50, 100, 200) without skipping any area ('chhode nhi kisi ko'),
    generates Canva Pro Logo & Banner (Zero AI Credits), enforces zero empty columns,
    and updates the Search & Coverage Tracker with Google Sheets auto-sync.
    """
    from backend.saturation_engine import extract_next_batch_flow
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "running",
        "batch_size": req.batch_size,
        "city": req.city,
        "category": req.category
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
            res = await extract_next_batch_flow(
                batch_size=req.batch_size,
                category=req.category if req.category else None,
                city=req.city if req.city else None,
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
    return {"task_id": task_id, "status": "started", "batch_size": req.batch_size}

# ==================== CANVA 10-DESIGN SUITE ENDPOINTS ====================
@app.get("/canva-suite", response_class=HTMLResponse)
async def serve_canva_suite():
    """Serves the 10 commercial Canva logos & storefront banners gallery."""
    p = os.path.join(os.path.dirname(__file__), "..", "frontend", "canva_suite.html")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Canva Suite Not Found</h1>")

@app.get("/api/canva-asset/{filename}")
async def serve_canva_asset(filename: str):
    """Serves generated Canva assets from canva_storefronts or canva_10_designs."""
    root_data = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    p1 = os.path.join(root_data, "canva_storefronts", filename)
    if os.path.exists(p1):
        return FileResponse(p1, media_type="image/png")
    p2 = os.path.join(root_data, "canva_10_designs", filename)
    if os.path.exists(p2):
        return FileResponse(p2, media_type="image/png")
# ==================== 24/7 AUTOPILOT & TURBO ENGINE ====================
from backend.autopilot import (
    load_autopilot_config,
    save_autopilot_config,
    toggle_autopilot,
    calculate_next_run,
    execute_full_autonomous_cycle,
    run_autopilot_background_worker
)

@app.on_event("startup")
async def on_startup():
    """Launches the persistent 24/7 background autopilot daemon."""
    asyncio.create_task(run_autopilot_background_worker())

class TurboPipelineRequest(BaseModel):
    batch_size: int = 10
    city: str = "Indore"
    category: str = "Jewellers & All Commercial"
    source_mode: str = "full_auto"  # "full_auto", "ready_only", "fresh_only"

@app.post("/api/turbo-full-pipeline")
async def api_turbo_full_pipeline(req: TurboPipelineRequest, background_tasks: BackgroundTasks):
    """
    Zero-Delay, High-Speed Turbo Pipeline:
    Immediately extracts leads, generates Canva Pro Logos & Banners in parallel,
    syncs to 3-sheet Excel & Google Sheets, and submits to jainforjain.com
    with photo/logo uploads with 0s delay!
    """
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "running",
        "batch_size": req.batch_size,
        "city": req.city,
        "category": req.category,
        "source_mode": req.source_mode
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
            res = await execute_full_autonomous_cycle(
                batch_size=req.batch_size,
                city=req.city,
                category=req.category,
                upload_mode="instant",
                delay_seconds=0,
                source_mode=req.source_mode,
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
    return {"task_id": task_id, "status": "started", "batch_size": req.batch_size}

class AutopilotSaveRequest(BaseModel):
    is_active: bool | None = None
    daily_time: str | None = None
    frequency_hours: int | None = None
    batch_size: int | None = None
    city: str | None = None
    category: str | None = None
    upload_mode: str | None = None
    delay_seconds: int | None = None

@app.get("/api/autopilot/config")
async def api_get_autopilot_config():
    """Returns the persistent 24/7 autopilot scheduler configuration and status."""
    return load_autopilot_config()

@app.post("/api/autopilot/save")
async def api_save_autopilot_config(req: AutopilotSaveRequest):
    """Saves updated parameters for the 24/7 autopilot scheduler."""
    cfg = load_autopilot_config()
    if req.is_active is not None:
        cfg["is_active"] = req.is_active
    if req.daily_time is not None:
        cfg["daily_time"] = req.daily_time
    if req.frequency_hours is not None:
        cfg["frequency_hours"] = req.frequency_hours
    if req.batch_size is not None:
        cfg["batch_size"] = req.batch_size
    if req.city is not None:
        cfg["city"] = req.city
    if req.category is not None:
        cfg["category"] = req.category
    if req.upload_mode is not None:
        cfg["upload_mode"] = req.upload_mode
    if req.delay_seconds is not None:
        cfg["delay_seconds"] = req.delay_seconds

    if cfg.get("is_active"):
        cfg["next_run_timestamp"] = calculate_next_run(cfg.get("daily_time", "10:00"), cfg.get("frequency_hours", 24))
    else:
        cfg["next_run_timestamp"] = None

    save_autopilot_config(cfg)
    return {"success": True, "config": cfg}

class AutopilotToggleRequest(BaseModel):
    active: bool | None = None

@app.post("/api/autopilot/toggle")
async def api_toggle_autopilot(req: AutopilotToggleRequest | None = None):
    """Toggles 24/7 autopilot ON/OFF."""
    active_val = req.active if req else None
    cfg = toggle_autopilot(active=active_val)
    return {"success": True, "config": cfg}

@app.post("/api/autopilot/run-now")
async def api_autopilot_run_now(background_tasks: BackgroundTasks):
    """Manually triggers the autonomous autopilot cycle immediately."""
    cfg = load_autopilot_config()
    
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
            cfg["running_state"] = "running"
            save_autopilot_config(cfg)
            res = await execute_full_autonomous_cycle(
                batch_size=cfg.get("batch_size", 50),
                city=cfg.get("city", "Indore"),
                category=cfg.get("category", "Jewellers & All Commercial"),
                upload_mode=cfg.get("upload_mode", "instant"),
                delay_seconds=cfg.get("delay_seconds", 0),
                progress_callback=dispatch_event
            )
            c = load_autopilot_config()
            c["last_run_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c["last_run_result"] = res
            c["total_runs"] = c.get("total_runs", 0) + 1
            c["running_state"] = "idle"
            if c.get("is_active"):
                c["next_run_timestamp"] = calculate_next_run(c.get("daily_time", "10:00"), c.get("frequency_hours", 24))
            save_autopilot_config(c)
            TASKS[task_id]["status"] = "completed"
        except Exception as e:
            c = load_autopilot_config()
            c["running_state"] = "idle"
            save_autopilot_config(c)
            TASKS[task_id]["status"] = "failed"
class SaturationScanRequest(BaseModel):
    city: str = "Jaipur"
    area: Optional[str] = None
    mode: str = "auto"  # "manual" or "auto"
    count: int = 50
    entity_type: str = "all"  # "all", "mandir", "trust", "commercial"

@app.get("/api/saturation/roadmap")
async def api_saturation_roadmap(city: Optional[str] = None):
    """Returns current active area, next sequential area, and completed markets."""
    from backend.saturation_engine import get_area_roadmap
    return get_area_roadmap(city)

@app.post("/api/saturation/set-area")
async def api_saturation_set_area(req: Dict[str, str]):
    """Manually changes active area pointer."""
    from backend.saturation_engine import set_active_area
    city = req.get("city", "Jaipur")
    area = req.get("area", "")
    return set_active_area(city, area)

@app.post("/api/saturation/scan")
async def api_saturation_scan(req: SaturationScanRequest, background_tasks: BackgroundTasks):
    """Triggers either Manual Area Scan or Autonomous Auto-Advancing Saturation."""
    from backend.saturation_engine import advance_saturation_cycle, crawl_area_deep, get_area_roadmap
    
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
            dispatch_event({"type": "stage", "stage": "saturation_active", "city": req.city, "area": req.area, "mode": req.mode})
            if req.mode == "manual" and req.area:
                res = await crawl_area_deep(
                    city=req.city,
                    area=req.area,
                    category="All Sectors (Hyperlocal)",
                    target_count=req.count,
                    entity_type=req.entity_type
                )
                mined_count = len(res)
            else:
                mined_count = await advance_saturation_cycle(
                    target_leads_needed=req.count,
                    entity_type=req.entity_type,
                    city_override=req.city,
                    area_override=req.area
                )
            
            roadmap = get_area_roadmap(req.city)
            dispatch_event({
                "type": "complete",
                "mined": mined_count,
                "current_area": roadmap["current_area"],
                "next_area": roadmap["next_area"],
                "completed_areas": roadmap["completed_areas"]
            })
            TASKS[task_id]["status"] = "completed"
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            dispatch_event({"type": "error", "message": str(e)})

    background_tasks.add_task(runner)
    return {"task_id": task_id, "status": "started"}

@app.get("/api/matrix/5layer-queries")
async def api_matrix_5layer_queries(city: Optional[str] = "Indore", area: Optional[str] = ""):
    """Returns 5-layer master search queries across all 17 strategic dimensions."""
    from backend.matrix import generate_5layer_queries
    return generate_5layer_queries(city=city or "Indore", area=area or "", limit=150)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



