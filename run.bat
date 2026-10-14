@echo off
chcp 65001 >nul
title BOM BADO Timekeeping Automation - Safety Shield Active

cd /d "%~dp0"

:: Launch automated timekeeping directly with safety protection (no confusing menus)
python schedule_timekeeping.py %*

if %errorlevel% neq 0 (
    echo.
    echo Process exited with an error. Please check debug.log.
    pause
)
