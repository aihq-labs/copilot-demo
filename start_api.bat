@echo off
REM ============================================================
REM Copilot Studio Agent REST API Startup Script
REM Copyright 2025 AIHQ.ie
REM Licensed under the Apache License, Version 2.0
REM ============================================================

echo ============================================================
echo   Copilot Studio Agent REST API
echo   Developed by AIHQ.ie
echo ============================================================
echo.

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please create .env file from .env.example
    echo.
    if exist .env.example (
        echo You can copy it with:
        echo   copy .env.example .env
        echo.
    )
    echo Continuing anyway, but configuration may be incomplete...
    echo.
)

REM Check if uvicorn is installed
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo [ERROR] uvicorn is not installed!
    echo Please install dependencies:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if api.py exists
if not exist api.py (
    echo [ERROR] api.py not found!
    echo Please make sure you're in the correct directory.
    echo.
    pause
    exit /b 1
)

echo Starting API server...
echo.
echo API will be available at:
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc:      http://localhost:8000/redoc
echo   - API Root:   http://localhost:8000/
echo   - Health:     http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the API server with auto-reload
uvicorn api:app --reload --host 0.0.0.0 --port 8000

REM If uvicorn fails, show error    
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start API server
    echo.
    echo Troubleshooting:
    echo 1. Check that all dependencies are installed: pip install -r requirements.txt
    echo 2. Verify your .env file is configured correctly
    echo 3. Check that port 8000 is not already in use
    echo.
    pause
    exit /b 1
)
