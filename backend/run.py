#!/usr/bin/env python
"""
Entry point to run the FastAPI server.
Usage: python run.py
or use: uvicorn app.main:app --reload
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get config from environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True") == "True"
    debug = os.getenv("DEBUG", "False") == "True"

    print(f"Starting USSI Legal Document Tracker Backend")
    print(f"Server: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/docs")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
