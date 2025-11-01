@echo off
title PoseAnimator.com Web Launcher
color 0B
echo.
echo ================================================
echo   PoseAnimator.com Web Launcher
echo   AI-Powered Real-Time Animation Studio
echo ================================================
echo.
echo Opening browser...
echo.
echo The server will display network addresses after starting
echo Press Ctrl+C to stop the server
echo.
timeout /t 1 /nobreak >nul
start http://localhost:8000
python web_launcher.py
pause

