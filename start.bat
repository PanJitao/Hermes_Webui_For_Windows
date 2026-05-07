@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Hermes Agent WebUI - Start
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

:: Search for Hermes directory
echo [2/3] Detecting Hermes directory...
echo.

set HERMES_HOME=

:: Common install paths - check one by one
if exist "%USERPROFILE%\.hermes\config.yaml" (
    set HERMES_HOME=%USERPROFILE%\.hermes
)
if exist "D:\Windows_Hermes\hermes-agent-windows\.hermes\config.yaml" (
    set HERMES_HOME=D:\Windows_Hermes\hermes-agent-windows\.hermes
)
if exist "C:\Windows_Hermes\hermes-agent-windows\.hermes\config.yaml" (
    set HERMES_HOME=C:\Windows_Hermes\hermes-agent-windows\.hermes
)

if not "%HERMES_HOME%"=="" (
    echo   Found: %HERMES_HOME%
    echo.
    set /p CONFIRM="   OK? (Y/n): "
    if /i "!CONFIRM!"=="n" goto :INPUT
    if /i "!CONFIRM!"=="no" goto :INPUT
    goto :START
)

echo   Hermes directory not found.

:INPUT
echo.
echo   Enter path to .hermes folder (must contain config.yaml)
echo   e.g. D:\Windows_Hermes\hermes-agent-windows\.hermes
echo.
:INPUT_LOOP
set /p USER_PATH="   Path: "
if "!USER_PATH!"=="" goto :INPUT_LOOP

:: Remove trailing backslash
if "!USER_PATH:~-1!"=="\" set USER_PATH=!USER_PATH:~0,-1!

if not exist "!USER_PATH!" (
    echo   Path not found, try again.
    goto :INPUT_LOOP
)
if not exist "!USER_PATH!\config.yaml" (
    echo   config.yaml not found in this folder.
    goto :INPUT_LOOP
)
set HERMES_HOME=!USER_PATH!
echo   OK: !HERMES_HOME!

:START
echo.
echo [3/3] Starting...
echo.
echo ========================================
echo   Hermes Agent WebUI
echo   URL: http://localhost:8686
echo   DATA: %HERMES_HOME%
echo   Press Ctrl+C to stop
echo ========================================
echo.

set HERMES_HOME=%HERMES_HOME%
echo Opening browser...
start http://localhost:8686
echo.
python app.py
