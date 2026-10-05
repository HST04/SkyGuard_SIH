#!/usr/bin/env python3
"""
SkyGuard AI - Multi-Suite Test Runner
====================================
Runs all unit and integration test suites:
  1. End-to-End System Integration Tests (FastAPI + Pipeline + SSE)
  2. AWS Edge Simulator Physics & Chaos Tests
  3. SkyGuard Anomaly Detection Engine & Models Tests
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def run_suite(name: str, cwd: Path, args: list) -> bool:
    print(f"\n{'='*70}")
    print(f" RUNNING SUITE: {name}")
    print(f" Working Directory: {cwd}")
    print(f"{'='*70}")
    cmd = [sys.executable, "-m", "pytest"] + args
    res = subprocess.run(cmd, cwd=str(cwd))
    return res.returncode == 0

def main():
    results = {}

    # 1. Integration Tests
    results["Integration (End-to-End Wiring)"] = run_suite(
        name="End-to-End Integration Tests",
        cwd=ROOT,
        args=["tests/test_end_to_end_wiring.py", "-v"]
    )

    # 2. Edge Simulator Tests
    results["AWS Edge Simulator (Physics & Chaos)"] = run_suite(
        name="Edge Simulator Physics & Faults",
        cwd=ROOT / "SKYGUARD EDGE SIMULATOR",
        args=["tests", "-v"]
    )

    # 3. Data Model Tests
    results["Data Model & Anomaly Detection Pipeline"] = run_suite(
        name="Data Model & ML Pipeline",
        cwd=ROOT / "skyguard_data_model",
        args=["tests", "-v"]
    )

    print(f"\n{'='*70}")
    print(" SKYGUARD AI TEST EXECUTION SUMMARY")
    print(f"{'='*70}")
    all_passed = True
    for name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        if not passed:
            all_passed = False
        print(f"  {status:<10} | {name}")
    print(f"{'='*70}\n")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
