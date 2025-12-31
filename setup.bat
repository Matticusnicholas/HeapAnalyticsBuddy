@echo off
title Heap Analytics Buddy - Setup
echo.
echo ============================================================
echo   HEAP ANALYTICS BUDDY - SETUP
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available.
    echo Please ensure pip is installed with Python.
    pause
    exit /b 1
)

:: Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo      Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo      Virtual environment created successfully.
)
echo.

:: Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo      Virtual environment activated.
echo.

:: Install dependencies
echo [4/5] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.

:: Install the package in development mode
echo [5/5] Installing Heap Analytics Buddy...
pip install -e .
if %errorlevel% neq 0 (
    echo [WARNING] Failed to install package in development mode.
    echo You can still run the tool using: python -m heap_buddy.cli
)
echo.

:: Create config file if it doesn't exist
if not exist heap_buddy_config.yaml (
    echo Creating configuration file...
    copy heap_buddy_config.example.yaml heap_buddy_config.yaml >nul 2>&1
    echo Configuration file created: heap_buddy_config.yaml
)

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating environment file...
    copy .env.example .env >nul 2>&1
    echo Environment file created: .env
    echo.
    echo [IMPORTANT] Edit .env file to add your Heap Analytics credentials:
    echo   HEAP_EMAIL=your-email@example.com
    echo   HEAP_PASSWORD=your-password
)

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo   1. Edit .env file with your Heap Analytics credentials
echo   2. Run 'run.bat' to generate a report
echo   3. Or run 'heap-buddy generate' in the activated environment
echo.
echo To activate the virtual environment manually:
echo   venv\Scripts\activate
echo.
pause
