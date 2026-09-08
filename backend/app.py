"""
FastAPI Server for JainBiz Lead Miner.
Provides SSE (Server-Sent Events) for real-time progress streaming,
task dispatching, and 1-click Excel file downloads.
"""

import os
import uuid
import json
import asyncio
from typing import Dict, Any, List
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
    include_sacred: bool = True
    include_surnames: bool = True
    include_photos: bool = True
    max_firms: int = 100

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

@app.get("/api/download-excel/{task_id}")
async def download_excel(task_id: str):
    """Provides the generated .xlsx file for 1-click download."""
    task = TASKS.get(task_id)
    if not task or not task.get("excel_path"):
        return {"error": "Excel file not ready or task not found."}

    excel_path = task["excel_path"]
    filename = task.get("filename") or "Jain_Leads.xlsx"
    
    if not os.path.exists(excel_path):
        return {"error": "Excel file does not exist on disk."}

    return FileResponse(
        path=excel_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
