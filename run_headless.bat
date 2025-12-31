@echo off
title Heap Analytics Buddy - Headless Mode
echo.
echo ============================================================
echo   HEAP ANALYTICS BUDDY - HEADLESS MODE
echo ============================================================
echo.
echo Running in headless mode (no browser window)...
echo Note: You must have valid credentials in .env file
echo.

:: Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found.
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Load environment variables from .env if it exists
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
)

:: Run in headless mode with default settings
heap-buddy generate --headless --no-interactive --browser firefox --format pdf --format docx --days 30

echo.
echo Report generation complete!
echo Check the 'reports' folder for your files.
echo.
pause
