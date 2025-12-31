@echo off
title Heap Analytics Buddy - Chrome
echo.
echo ============================================================
echo   HEAP ANALYTICS BUDDY - CHROME
echo ============================================================
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

:: Run with Chrome
echo Starting with Chrome browser...
echo.
heap-buddy generate --browser chrome --format pdf --format docx

echo.
pause
