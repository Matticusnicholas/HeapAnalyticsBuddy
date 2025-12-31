@echo off
title Heap Analytics Buddy - Install Playwright Browsers
echo.
echo ============================================================
echo   INSTALL PLAYWRIGHT BROWSERS
echo ============================================================
echo.
echo This will download browser binaries for Playwright.
echo This is optional - only needed if you want to use Playwright
echo instead of Selenium for browser automation.
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

echo Installing Playwright browsers (Firefox, Chrome, WebKit)...
echo This may take several minutes depending on your internet speed.
echo.

playwright install

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Playwright browser installation had issues.
    echo You can still use Selenium with Firefox or Chrome.
) else (
    echo.
    echo Playwright browsers installed successfully!
    echo You can now use: playwright-firefox, playwright-chrome, playwright-webkit
)

echo.
pause
