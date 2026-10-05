@echo off
title SkyGuard AI - Multi-Component Launcher
echo ==========================================================
echo          SkyGuard AI - Multi-Component Launcher
echo ==========================================================
echo Starting FastAPI Backend (Port 8000) and Next.js Frontend (Port 3000)...
cd /d "%~dp0"
python start_skyguard.py
pause
