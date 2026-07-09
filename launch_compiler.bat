@echo off
title Study Organizer Compiler Launcher

echo ===================================================
echo   Study Organizer Compiler - Starting System
echo ===================================================
echo.

cd /d "c:\Users\kaiy2\OneDrive\ƒhƒLƒ…ƒƒ“ƒg\class materials compiler"

:: Check if HTTP server (8502) is already running
netstat -ano | findstr 0.0.0.0:8502 > nul
if %errorlevel% neq 0 (
    netstat -ano | findstr 127.0.0.1:8502 > nul
    if %errorlevel% neq 0 (
        echo [1/2] Starting local web server on port 8502...
        start /min "Web Server" python -m http.server 8502
        timeout /t 1 > nul
    ) else (
        echo [1/2] Web server is already running.
    )
) else (
    echo [1/2] Web server is already running.
)

:: Check if Streamlit server (8501) is already running
netstat -ano | findstr 0.0.0.0:8501 > nul
if %errorlevel% neq 0 (
    netstat -ano | findstr 127.0.0.1:8501 > nul
    if %errorlevel% neq 0 (
        echo [2/2] Starting Streamlit application on port 8501...
        streamlit run streamlit_app.py --browser.gatherUsageStats false
        goto end
    )
)

echo [2/2] Streamlit is already running. Opening browser...
start http://localhost:8501

:end
echo.
echo Startup process completed.
echo Close this window to stop the Streamlit server.
