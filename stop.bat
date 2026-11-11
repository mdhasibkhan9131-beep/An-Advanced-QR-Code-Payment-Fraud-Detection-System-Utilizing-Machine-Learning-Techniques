@echo off
title Stop - QR Fraud Shield Services
color 0C

echo ===============================================================================
echo       Stopping QR Fraud Shield Services (Ports 8000 and 8501)
echo ===============================================================================
echo.

:: 1. Kill by window title
taskkill /fi "WINDOWTITLE eq QR Fraud Shield - Backend API*" /f >nul 2>&1

:: 2. Kill any processes holding port 8000 (uvicorn/fastapi)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 3. Kill any processes holding port 8501 (streamlit)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING 2^>nul') do (
    taskkill /f /pid %%a >nul 2>&1
)

color 0A
echo [OK] All QR Fraud Shield services on ports 8000 and 8501 have been stopped.
echo.
ping 127.0.0.1 -n 3 >nul
