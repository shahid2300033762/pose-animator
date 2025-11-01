@echo off
REM Auto-start PoseAnimator web server on Windows startup
REM Place this file in Windows Startup folder: C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

REM Change to the project directory
cd /d "C:\Users\kshah\Downloads\pose_animator-master"

REM Start the web server
python web_launcher.py

