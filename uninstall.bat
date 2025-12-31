@echo off
title Heap Analytics Buddy - Uninstall
echo.
echo ============================================================
echo   HEAP ANALYTICS BUDDY - UNINSTALL
echo ============================================================
echo.
echo This will remove the virtual environment and cached files.
echo Your reports and configuration files will NOT be deleted.
echo.

set /p confirm="Are you sure you want to uninstall? (y/N): "
if /i not "%confirm%"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo Removing virtual environment...
if exist venv (
    rmdir /s /q venv
    echo Virtual environment removed.
) else (
    echo Virtual environment not found.
)

echo.
echo Removing Python cache files...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r %%f in (*.pyc) do @if exist "%%f" del "%%f"
echo Cache files removed.

echo.
echo Removing egg-info...
if exist src\heap_buddy.egg-info (
    rmdir /s /q src\heap_buddy.egg-info
    echo Egg-info removed.
)

echo.
echo ============================================================
echo   UNINSTALL COMPLETE
echo ============================================================
echo.
echo The following files were preserved:
echo   - reports\ (your generated reports)
echo   - .env (your credentials)
echo   - heap_buddy_config.yaml (your configuration)
echo.
echo To reinstall, run setup.bat
echo.
pause
