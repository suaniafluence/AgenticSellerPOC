#!/usr/bin/env python3
"""Run the IAfluence web application."""
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print("=" * 60)
    print("  IAfluence Sales Agent - Web Application")
    print("=" * 60)
    print(f"  Server running at: http://{host}:{port}")
    print(f"  Debug mode: {debug}")
    print("=" * 60)

    uvicorn.run(
        "web.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning",
    )
