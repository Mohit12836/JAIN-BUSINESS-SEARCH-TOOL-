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
    excel_path = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx"
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
    excel_path = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx"
    
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

class EntryRequest(BaseModel):
    limit: int = 5
    live: bool = True

@app.post("/api/start-portal-entry")
async def start_portal_entry(req: EntryRequest, background_tasks: BackgroundTasks):
    """Triggers autonomous entry into jainforjain.com."""
    from backend.auto_entry_bot import run_auto_entry_batch
    excel_path = r"C:\Users\hp\Desktop\Jain_Leads_Verified_Photos_HD.xlsx"
    
    async def entry_runner():
        await run_auto_entry_batch(
            excel_path=excel_path,
            dry_run=not req.live,
            limit=req.limit
        )
        
    background_tasks.add_task(entry_runner)
    return {
        "status": "started",
        "mode": "LIVE" if req.live else "DRY-RUN",
        "limit": req.limit
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

