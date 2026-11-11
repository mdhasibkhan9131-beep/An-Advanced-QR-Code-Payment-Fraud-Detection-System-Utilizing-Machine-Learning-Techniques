@echo off
title QR Fraud Shield - Autonomous Payment Fraud Detection
color 0B

echo ===============================================================================
echo       QR Code Payment Fraud Detection System - 1-Click Launcher
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Auto-check setup & dependencies
set NEED_SETUP=0
if not exist ".venv\Scripts\activate.bat" (
    set NEED_SETUP=1
)

if "%NEED_SETUP%"=="1" (
    echo [INFO] Virtual environment missing. Running setup.bat...
    echo.
    call setup.bat
    if errorlevel 1 (
        echo [ERROR] Setup failed. Cannot start application.
        pause
        exit /b 1
    )
)

:: 2. Pre-clean ports 8000 and 8501 to avoid conflicts
taskkill /fi "WINDOWTITLE eq QR Fraud Shield - Backend API*" /f >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING 2^>nul') do taskkill /f /pid %%a >nul 2>&1

:: 3. Activate virtual environment
call .venv\Scripts\activate.bat

:: 4. Start FastAPI Backend in background
echo [1/2] Starting High-Performance API Backend on http://127.0.0.1:8000 ...
start "QR Fraud Shield - Backend API (Port 8000)" /min cmd /c "call .venv\Scripts\activate.bat && python -m uvicorn backend.api.server:app --host 127.0.0.1 --port 8000"

:: Quick 1-second sync before UI launch
ping 127.0.0.1 -n 2 >nul

:: 5. Start Streamlit Frontend
echo [2/2] Launching Fast AI Dashboard on http://localhost:8501 ...
echo.
echo ===============================================================================
echo    * Interactive Dashboard will open in your default web browser.
echo    * Backend API Docs:   http://127.0.0.1:8000/docs
echo    * Frontend UI:         http://localhost:8501
echo.
echo    To stop the application, simply close this window or press Ctrl+C.
echo ===============================================================================
echo.

python -m streamlit run frontend/app.py --server.port 8501 --server.headless false
if errorlevel 1 (
    echo.
    echo [ERROR] Streamlit encountered an issue or was terminated unexpectedly.
    pause
)

:: 6. Clean up backend when frontend is closed
echo.
echo [INFO] Stopping background backend server...
taskkill /fi "WINDOWTITLE eq QR Fraud Shield - Backend API*" /f >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do taskkill /f /pid %%a >nul 2>&1
echo [OK] All services stopped cleanly.
