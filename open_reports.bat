@echo off
title Open Reports Folder
echo.
echo Opening reports folder...
echo.

:: Create reports folder if it doesn't exist
if not exist reports (
    mkdir reports
    echo Created 'reports' folder.
)

:: Open the reports folder in Explorer
start "" "reports"

exit
