# 🚀 Auto-Start Web Server on Boot

## Problem
When you shut down your laptop, the web server stops and links don't work.

## ⚠️ Important Note
**The laptop needs to be ON for the website to work.** This is because:
1. The web server runs on your laptop
2. The Pose Animator app needs to run locally (for camera access)

## Solution: Auto-Start Server

### Option 1: Keep Laptop On (Easiest)
Instead of shutting down:
- **Sleep/Hibernate** - Website stays accessible when you wake it
- **Don't shut down** - Keep laptop on when you need access

### Option 2: Auto-Start Server on Boot

**Windows:**

1. **Press Win + R**
2. **Type:** `shell:startup`
3. **Press Enter**
4. **Copy `start_server_on_boot.bat`** to this folder
5. **Done!** Server will start automatically when Windows boots

**Alternative - Task Scheduler:**
1. Open Task Scheduler (Win + R → `taskschd.msc`)
2. Create Basic Task
3. Trigger: When computer starts
4. Action: Start program
5. Program: `python.exe`
6. Arguments: `C:\Users\kshah\Downloads\pose_animator-master\web_launcher.py`
7. Start in: `C:\Users\kshah\Downloads\pose_animator-master`

### Option 3: Always-On Setup

For 24/7 access, you need:
- **Laptop always on** (or desktop computer)
- **Keep it plugged in**
- **Disable sleep/hibernate**

## 🌐 Better Solution: Cloud Hosting

To make it work from anywhere (even when laptop is off):

### Option A: Host Website Only
1. Deploy website to cloud (AWS, Heroku, etc.)
2. Website loads from anywhere
3. **BUT:** Launch button won't work (app needs to run locally)

### Option B: Full Remote Solution
1. Set up Remote Desktop/VNC on laptop
2. Access laptop remotely
3. Run the app remotely
4. More complex setup

## 📋 Recommended Setup

**For Local Network Access:**
1. ✅ Keep laptop on when you need it
2. ✅ Use Sleep instead of Shutdown
3. ✅ Auto-start server on boot (see Option 2 above)

**For Remote Access:**
1. Deploy website to cloud hosting
2. Use Remote Desktop to access laptop
3. Or keep laptop on 24/7 with remote access

## ⚙️ Current Limitations

- **Website needs laptop ON** to be accessible
- **App needs laptop** to run (camera access)
- **Can't work if laptop is off**

## 💡 Pro Tips

1. **Use Sleep Mode** - Faster wake, less battery
2. **Plug in laptop** - Keep it powered
3. **Auto-start server** - See Option 2
4. **Bookmark the IP** - `http://10.129.1.193:8000`

## 🎯 Quick Fix

**Right now, to access from other devices:**
1. Make sure laptop is ON
2. Run: `python web_launcher.py`
3. Access from any device: `http://10.129.1.193:8000`

**To make it permanent:**
- Set up auto-start (Option 2 above)
- Keep laptop on or use Sleep mode

## ✅ Summary

**The laptop must be ON for this to work.** The website and app both run on your laptop, so shutting it down stops everything.

**Best approach:** Keep laptop on (or in Sleep mode) and auto-start the server on boot!

