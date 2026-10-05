#!/usr/bin/env python3
"""
SkyGuard AI - Unified System Launcher
=====================================
Launches and orchestrates SkyGuard AI Automatic Weather Station (AWS) components:
  1. Backend (FastAPI on port 8000 with PyTorch ML Engine & SSE Stream)
  2. Edge Simulator (Physical weather simulation with fault injection)
  3. Frontend (Next.js Dashboard on port 3000)

Usage:
  python start_skyguard.py --all           # Launch backend and edge simulator concurrently
  python start_skyguard.py --backend       # Launch FastAPI backend only
  python start_skyguard.py --simulator     # Launch interactive TUI Edge Simulator only
  python start_skyguard.py --headless      # Launch headless Edge Simulator (background stream)
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def run_backend():
    print("[+] Launching SkyGuard FastAPI Backend on http://localhost:8000...")
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    return subprocess.Popen(cmd, cwd=str(ROOT_DIR))

def run_frontend():
    print("[+] Launching SkyGuard Next.js Frontend on http://localhost:3000...")
    frontend_dir = ROOT_DIR / "frontend"
    # Use cmd /c on Windows to bypass PowerShell ExecutionPolicy restrictions on npm.ps1
    if sys.platform.startswith("win"):
        cmd = ["cmd", "/c", "npm", "run", "dev"]
    else:
        cmd = ["npm", "run", "dev"]
    return subprocess.Popen(cmd, cwd=str(frontend_dir))

def run_simulator(interactive: bool = True, auto_chaos: bool = False, chaos_duration: float = 35.0):
    sim_dir = ROOT_DIR / "SKYGUARD EDGE SIMULATOR"
    cmd = [sys.executable, "run_simulator.py"]
    if auto_chaos:
        cmd.extend(["--auto-chaos", "--chaos-duration", str(chaos_duration)])
    if not interactive:
        cmd.extend(["--endpoint-url", "http://localhost:8000/api/v1/telemetry"])
    mode_str = "Interactive TUI Mode" if interactive else "Headless Mode"
    if auto_chaos:
        mode_str += f" [Auto-Chaos active, {chaos_duration:.0f}s dwell]"
    print(f"[+] Launching SkyGuard Edge Simulator in {mode_str}...")
    return subprocess.Popen(cmd, cwd=str(sim_dir))

def main():
    parser = argparse.ArgumentParser(description="SkyGuard AI Unified Launcher")
    parser.add_argument("--backend", action="store_true", help="Launch FastAPI backend only")
    parser.add_argument("--frontend", action="store_true", help="Launch Next.js frontend only")
    parser.add_argument("--simulator", action="store_true", help="Launch interactive Edge Simulator TUI only")
    parser.add_argument("-c", "--auto-chaos", action="store_true", help="Enable automatic random cycling through nominal and fault states in simulator")
    parser.add_argument("--chaos-duration", type=float, default=35.0, help="Dwell time in seconds per chaos state (default: 35.0s)")
    parser.add_argument("--stream", type=str, default=None, help="Stream a specific CSV file via simulator")
    parser.add_argument("--keep-db", action="store_true", help="Retain existing SQLite database records")
    args = parser.parse_args()

    # Reset database for clean demo run by default unless --keep-db is set
    if not args.keep_db:
        try:
            from backend.database import db
            db.reset_database()
            print("[+] Initialized pristine SQLite database (clean state for video demo).")
        except Exception as e:
            print(f"[!] Note: Database reset skipped ({e})")

    procs = []
    try:
        if args.frontend:
            p_front = run_frontend()
            procs.append(p_front)
        elif args.simulator:
            p_sim = run_simulator(interactive=True, auto_chaos=args.auto_chaos, chaos_duration=args.chaos_duration)
            procs.append(p_sim)
        else:
            # Default: Always launch backend
            p_back = run_backend()
            procs.append(p_back)
            time.sleep(1.5)  # Allow backend to bind port 8000

            # Also launch frontend unless --backend only flag is passed
            if not args.backend:
                p_front = run_frontend()
                procs.append(p_front)
                time.sleep(1.0)

        if args.stream:
            sim_dir = ROOT_DIR / "SKYGUARD EDGE SIMULATOR"
            print(f"[+] Streaming CSV dataset: {args.stream}")
            cmd = [sys.executable, "run_simulator.py", "--csv", args.stream]
            p_sim = subprocess.Popen(cmd, cwd=str(sim_dir))
            procs.append(p_sim)

        print("\n" + "=" * 70)
        print("  SKYGUARD AI - AUTOMATIC WEATHER STATION MONITORING (STANDBY)")
        print("=" * 70)
        print("  [OK] Backend online:     http://localhost:8000/api/v1/health")
        print("  [OK] Telemetry stream:   http://localhost:8000/api/v1/telemetry/stream")
        print("  [OK] Frontend dashboard: http://localhost:3000")
        print("\n  >>> DEMO WORKFLOW (NO STREAMING UNTIL YOU RUN):")
        print("  Step 1: Generate authentic Indian climate CSV:")
        print('          python "SKYGUARD EDGE SIMULATOR\\generate_dataset.py" --region mumbai_monsoon --rows 120 --output demo.csv')
        print("  Step 2: Stream CSV through Edge Simulator:")
        print('          python "SKYGUARD EDGE SIMULATOR\\run_simulator.py" --csv demo.csv')
        print("=" * 70 + "\n")

        for p in procs:
            p.wait()

    except KeyboardInterrupt:
        print("\n[*] Terminating all SkyGuard processes...")
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        print("[OK] Stopped cleanly.")

if __name__ == "__main__":
    main()
