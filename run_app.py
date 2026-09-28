"""
MARINE-SHIELD Unified Web Application Launcher
Launches both the FastAPI backend and Streamlit frontend in a single process,
and automatically opens the default web browser.
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def check_prerequisites():
    """Ensure database, vectorstore, and model are initialized."""
    print("==================================================")
    print("🛡️  MARINE-SHIELD: Initializing Application...")
    print("==================================================")

    # 1. Initialize DB
    from database.database import init_db
    init_db()
    print("[1/3] Database: Initialized.")

    # 2. Check Vectorstore
    from rag.retriever import is_vectorstore_available
    if not is_vectorstore_available():
        print("[2/3] Vector Store: Ingesting knowledge documents into FAISS...")
        from rag.ingest import ingest_knowledge_base
        ingest_knowledge_base(force_rebuild=False)
    else:
        print("[2/3] Vector Store: Ready.")

    # 3. Check Production Model
    from ml.predict import is_production_model_available
    if not is_production_model_available():
        print("[3/3] Model: No checkpoint found. Starting in DEMO MODE (or run ml/train.py to train).")
    else:
        print("[3/3] Model: Production MobileNetV3 Checkpoint Loaded.")


def main():
    check_prerequisites()

    python_executable = sys.executable

    print("\n[Starting Servers]")
    # 1. Launch FastAPI Backend
    backend_cmd = [
        python_executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    print("  -> Starting FastAPI backend on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(BASE_DIR))

    # Give backend a moment to bind port
    time.sleep(2)

    # 2. Launch Streamlit Frontend
    frontend_cmd = [
        python_executable, "-m", "streamlit", "run",
        "frontend/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ]
    print("  -> Starting Streamlit frontend on http://localhost:8501 ...")
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(BASE_DIR))

    # Give Streamlit a moment to start, then open browser
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

    print("\n==================================================")
    print("✅ MARINE-SHIELD is Live!")
    print("   Web App URL:       http://localhost:8501")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check:      http://localhost:8000/api/health")
    print("==================================================")
    print("Press Ctrl+C in this terminal to stop both servers.\n")

    try:
        # Keep launcher running while child processes are active
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n[Stopping MARINE-SHIELD] Shutting down servers...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")


if __name__ == "__main__":
    main()
