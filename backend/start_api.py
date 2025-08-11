#!/usr/bin/env python3
"""
Startup script for SpecWeaver API
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Also try adding the parent directory (for Docker volume mount)
parent_dir = backend_dir.parent / "backend"
if parent_dir.exists():
    sys.path.insert(0, str(parent_dir))

# Import and run the API
try:
    from api.api.app import app
    import uvicorn
    
    print("✅ Starting SpecWeaver API on 0.0.0.0:8080")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")  # Show first 3 entries
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")
    print(f"📂 Contents of {backend_dir}:")
    for item in backend_dir.iterdir():
        print(f"  📄 {item}")
    if parent_dir.exists():
        print(f"📂 Contents of {parent_dir}:")
        for item in parent_dir.iterdir():
            print(f"  📄 {item}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
