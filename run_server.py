import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

def main():
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"Starting JainBiz server on {host}:{port}...")
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
