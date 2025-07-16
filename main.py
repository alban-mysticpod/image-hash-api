#!/usr/bin/env python3
"""
Main entry point for the Image Hash API.
This file imports the FastAPI app from the api module and exposes it for deployment.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 