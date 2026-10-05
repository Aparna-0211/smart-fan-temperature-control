@echo off
title ESP32 Smart Fan Dashboard
echo.
echo ============================================
echo      ESP32 SMART FAN MONITOR
echo ============================================
echo.
set /p PORT=Enter ESP32 COM port (example COM5): 
echo.
py app.py --port %PORT%
pause
