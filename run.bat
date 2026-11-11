@echo off
title QR Fraud Shield - Autonomous Payment Fraud Detection
color 0B

echo ===============================================================================
echo       QR Code Payment Fraud Detection System - 1-Click Launcher
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Auto-check setup
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] First-time setup detected. Running setup.bat automatically...
    echo.
    call setup.bat
    if %errorlevel% neq 0 (
        echo [ERROR] Setup failed. Cannot start application.
        pause
        exit /b 1
    )
)

:: 2. Activate virtual environment
call .venv\Scripts\activate.bat

:: 3. Start FastAPI Backend in background
echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "QR Fraud Shield - Backend API (Port 8000)" /min cmd /c "call .venv\Scripts\activate.bat && python -m uvicorn backend.api.server:app --host 127.0.0.1 --port 8000"

echo [2/3] Initializing dual-tier ML engines (LightGBM + Isolation Forest)...
ping 127.0.0.1 -n 4 >nul

:: 4. Start Streamlit Frontend
echo [3/3] Launching Modern Streamlit UI on http://localhost:8501 ...
echo.
echo ===============================================================================
echo    * Interactive Dashboard will open in your default web browser.
echo    * Backend API Docs:   http://127.0.0.1:8000/docs
echo    * Frontend UI:         http://localhost:8501
echo.
echo    To stop both servers, simply close this window or run stop.bat.
echo ===============================================================================
echo.

python -m streamlit run frontend/app.py --server.port 8501 --server.headless false

:: Clean up backend when frontend is closed
echo.
echo [INFO] Stopping backend server...
taskkill /fi "WINDOWTITLE eq QR Fraud Shield - Backend API*" /f >nul 2>&1
echo [OK] All services stopped cleanly.
