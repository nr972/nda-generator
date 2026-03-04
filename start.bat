@echo off
REM NDA Generator — One-command startup (Windows)
REM Launches both the API server and the web frontend.
REM Usage: start.bat

cd /d "%~dp0"

set API_PORT=8000
set FRONTEND_PORT=8501

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3 is required but not found.
    echo Install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies if needed
python -c "import fastapi" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing dependencies (first run only^)...
    python -m pip install -e ".[dev]" --quiet
)

REM Create data directories
if not exist data\generated mkdir data\generated

REM Start API server in background
echo Starting API server on port %API_PORT%...
start /b python -m uvicorn nda_app.main:app --host 127.0.0.1 --port %API_PORT%

REM Wait for API to be ready
echo Waiting for API...
set /a TRIES=0
:wait_loop
set /a TRIES+=1
if %TRIES% gtr 30 (
    echo Error: API failed to start.
    exit /b 1
)
timeout /t 1 /nobreak >nul
curl -s "http://127.0.0.1:%API_PORT%/health" >nul 2>&1
if %ERRORLEVEL% neq 0 goto wait_loop
echo API is ready.

REM Start Streamlit frontend
echo.
echo ============================================
echo   NDA Generator is running!
echo   Frontend: http://localhost:%FRONTEND_PORT%
echo   API docs: http://localhost:%API_PORT%/docs
echo   Close this window to stop
echo ============================================
echo.

python -m streamlit run nda_frontend/app.py --server.port %FRONTEND_PORT% --server.address 127.0.0.1
