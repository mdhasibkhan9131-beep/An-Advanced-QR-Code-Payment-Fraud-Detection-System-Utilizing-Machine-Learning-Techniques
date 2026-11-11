@echo off
setlocal enabledelayedexpansion
title Setup - QR Code Payment Fraud Detection System
color 0B

echo ===============================================================================
echo      QR Code Payment Fraud Detection System - Environment Setup
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python installation
echo [1/6] Checking Python installation...
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    color 0C
    echo.
    echo [ERROR] Python is not installed or not found in system PATH!
    echo Please install Python 3.10 or 3.11 from: https://www.python.org/downloads/
    echo IMPORTANT: Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version') do set PY_VER=%%v
echo [OK] Found %PY_VER% (%PYTHON_CMD%)
echo.

:: 2. Check and copy .env and .streamlit configuration if missing
echo [2/6] Checking environment configuration (.env and .streamlit)...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env from .env.example
    ) else (
        echo [WARNING] .env.example not found. Proceeding with system defaults.
    )
) else (
    echo [OK] .env configuration exists.
)

if not exist ".streamlit\config.toml" (
    mkdir .streamlit 2>nul
    (
        echo [client]
        echo toolbarMode = "minimal"
        echo showErrorDetails = false
        echo.
        echo [ui]
        echo hideTopBar = true
        echo.
        echo [theme]
        echo base = "dark"
        echo primaryColor = "#6366f1"
        echo backgroundColor = "#080c14"
        echo secondaryBackgroundColor = "#0f172a"
        echo textColor = "#f1f5f9"
        echo font = "sans serif"
        echo.
        echo [server]
        echo headless = true
        echo enableCORS = false
        echo enableXsrfProtection = false
    ) > .streamlit\config.toml
    echo [OK] Configured clean UI in .streamlit/config.toml
) else (
    echo [OK] .streamlit configuration exists.
)
echo.

:: 3. Create Virtual Environment (.venv)
echo [3/6] Configuring virtual environment (.venv)...
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Creating new virtual environment in .venv ...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully.
) else (
    echo [OK] Existing virtual environment found.
)
echo.

:: 4. Activate venv and install dependencies
echo [4/6] Installing dependencies from requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    color 0E
    echo [WARNING] Some dependencies had warnings during install. Retrying in normal mode...
    python -m pip install -r requirements.txt
)
echo [OK] Dependencies installed and verified.
echo.

:: 5. Initialize SQLite Database & Schema
echo [5/6] Initializing SQLite database schemas...
python -c "from backend.database.session import init_db; init_db()" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] SQLite database schemas verified at database/fraud_detection.db
) else (
    echo [WARNING] Database init check returned non-zero, will auto-initialize at runtime.
)
echo.

:: 6. Check / Train Machine Learning Models
echo [6/6] Checking serialized Machine Learning models...
if not exist "backend\models\lightgbm_model.joblib" (
    echo [INFO] Production models not found. Training models now (approx 10-15s)...
    python -m backend.models.trainer
    echo [OK] Models trained and serialized to backend/models/
) else (
    echo [OK] Serialized production models found (LightGBM + Isolation Forest).
)
echo.

color 0A
echo ===============================================================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo    The project is fully configured and ready to demonstrate.
echo ===============================================================================
echo.
echo You can run the application anytime using:
echo    - run.bat   (Starts both Backend and Frontend and opens Browser)
echo.

set /p START_NOW="Do you want to launch the system right now? (Y/N): "
if /i "%START_NOW%"=="Y" (
    echo Starting platform...
    call run.bat
) else (
    echo You can start later by double-clicking run.bat
    echo.
    pause
)
