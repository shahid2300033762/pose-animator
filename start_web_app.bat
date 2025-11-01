@echo off
title Pose Animator - Web Version
color 0B
echo.
echo ================================================
echo   Pose Animator - Web Version
echo   Runs in your browser window!
echo ================================================
echo.
echo Starting web server on port 8001...
echo.
echo The app will open in your browser window
echo Works on any device - laptop, phone, tablet!
echo.
echo Press Ctrl+C to stop the server
echo.
timeout /t 2 /nobreak >nul
start http://localhost:8001
python web_pose_animator.py
pause

