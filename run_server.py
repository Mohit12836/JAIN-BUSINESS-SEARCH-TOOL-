import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    config = uvicorn.Config(
        app="backend.app:app",
        host=host,
        port=port,
        reload=False,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())

if __name__ == "__main__":
    main()
