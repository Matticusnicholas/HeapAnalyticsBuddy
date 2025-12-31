@echo off
title Heap Analytics Buddy
echo.
echo ============================================================
echo   HEAP ANALYTICS BUDDY
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
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Load environment variables from .env if it exists
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
)

:: Run the CLI
echo Starting Heap Analytics Buddy...
echo.

:: Check for command line arguments
if "%1"=="" (
    :: No arguments - run interactive mode
    heap-buddy generate --interactive
) else if "%1"=="--help" (
    heap-buddy --help
) else if "%1"=="setup" (
    heap-buddy setup
) else if "%1"=="browsers" (
    heap-buddy browsers
) else if "%1"=="generate" (
    :: Pass all arguments to generate command
    heap-buddy %*
) else (
    :: Pass all arguments directly
    heap-buddy %*
)

echo.
pause
