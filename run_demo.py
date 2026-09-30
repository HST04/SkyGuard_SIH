#!/usr/bin/env python3
"""
SkyGuard AI — One-Button Full Stack Demo Launcher & Live Edge Runner
===================================================================
Launches:
  1. FastAPI Backend (http://localhost:8000)
  2. Next.js Frontend (http://localhost:3000)
  3. Automatically opens default browser to the 3D Digital Twin
  4. Runs the interactive Live Edge Station Console in this terminal!

Usage:
  python run_demo.py
"""

import os
import sys
import time
import socket
import subprocess
import webbrowser
import atexit
import signal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

backend_proc = None
frontend_proc = None

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

def kill_proc(proc):
    if proc and proc.poll() is None:
        try:
            if sys.platform == "win32":
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            pass

def cleanup():
    print("\n\033[93m[SkyGuard Launcher] Shutting down background services...\033[0m")
    kill_proc(backend_proc)
    kill_proc(frontend_proc)
    print("\033[92m[SkyGuard Launcher] All services stopped cleanly. Goodbye!\033[0m")

atexit.register(cleanup)

def wait_for_url(url: str, timeout_sec: int = 30) -> bool:
    import urllib.request
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status in (200, 304):
                    return True
        except Exception:
            time.sleep(0.8)
    return False

def main():
    global backend_proc, frontend_proc

    print("\033[1m\033[96m" + "=" * 78 + "\033[0m")
    print("\033[1m\033[97m   SkyGuard AI — One-Button Full Stack Demo Launcher   \033[0m")
    print("\033[2m   AI/ML Anomaly Detection for Automatic Weather Stations (AWS) \033[0m")
    print("\033[1m\033[96m" + "=" * 78 + "\033[0m\n")

    # 1. Start Backend if not already running
    if is_port_in_use(8000):
        print("\033[92m[Backend] Found existing service on port 8000. Reusing.\033[0m")
    else:
        print("\033[94m[Backend] Starting FastAPI Backend on port 8000...\033[0m")
        backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(BACKEND_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        print("\033[94m[Backend] Waiting for API readiness...\033[0m")
        if not wait_for_url("http://127.0.0.1:8000/api/v1/telemetry/overview", timeout_sec=25):
            print("\033[91m[Error] Backend failed to start on port 8000.\033[0m")
            sys.exit(1)
        print("\033[92m[Backend] Online & Healthy at http://localhost:8000\033[0m")

    # 2. Start Frontend if not already running
    if is_port_in_use(3000):
        print("\033[92m[Frontend] Found existing service on port 3000. Reusing.\033[0m")
    else:
        print("\033[94m[Frontend] Starting Next.js Digital Twin Dashboard on port 3000...\033[0m")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        print("\033[94m[Frontend] Compiling Next.js application...\033[0m")
        if not wait_for_url("http://localhost:3000", timeout_sec=40):
            print("\033[93m[Frontend] Next.js is still compiling, proceeding to browser launch...\033[0m")
        else:
            print("\033[92m[Frontend] Online at http://localhost:3000\033[0m")

    # 3. Open Web Browser
    print("\033[96m[Browser] Launching SkyGuard AI Dashboard (http://localhost:3000)...\033[0m")
    webbrowser.open("http://localhost:3000")

    time.sleep(2.0)

    # 4. Hand over control to interactive Edge Telemetry Runner
    print("\n\033[92m[System Ready] Handing terminal over to Interactive Edge Station Streamer...\033[0m")
    from edge_runner import EdgeStationRunner

    runner = EdgeStationRunner(
        endpoint="http://localhost:8000/api/v1/telemetry/ingest",
        station_id="AGRA-01",
        mode="nominal"
    )

    try:
        runner.run()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()
