# 🚀 Step-by-Step: Auto-Start PoseAnimator Server

## Quick Setup (3 Minutes)

### Step 1: Open Startup Folder

1. **Press `Win + R`** (Windows key + R)
2. **Type:** `shell:startup`
3. **Press Enter**
4. A folder window will open - this is your Startup folder!

### Step 2: Copy Auto-Start Script

**Method A: Use the provided script**

1. **Go to your project folder:**
   - `C:\Users\kshah\Downloads\pose_animator-master`
2. **Find:** `start_server_on_boot.bat`
3. **Copy it** (Ctrl+C)
4. **Paste it** into the Startup folder window (Ctrl+V)

**Method B: Create shortcut**

1. **In the Startup folder** (from Step 1)
2. **Right-click → New → Shortcut**
3. **Browse to:** `C:\Users\kshah\Downloads\pose_animator-master\web_launcher.py`
4. **Click Next → Finish**

### Step 3: Test It!

1. **Restart your computer** (or reboot)
2. **After Windows boots**, wait 10 seconds
3. **Open browser** on any device
4. **Go to:** `http://10.129.1.193:8000`
5. **Website should load!** 🎉

## What Happens Now

✅ Every time Windows boots → Server starts automatically  
✅ Website accessible at `http://10.129.1.193:8000`  
✅ Works from any device on your network  
✅ No manual setup needed!

## Verification

**Check if server is running:**

1. Open Command Prompt (Win + R → `cmd`)
2. Type: `netstat -ano | findstr :8000`
3. If you see output → Server is running! ✅

**Check if accessible:**

1. Open browser
2. Go to: `http://localhost:8000`
3. If website loads → Working! ✅

## Troubleshooting

### Server doesn't start automatically?

**Check:**
1. File is in Startup folder? (`shell:startup`)
2. Python is in PATH? (Type `python --version` in cmd)
3. Script has correct path? (Check `start_server_on_boot.bat`)

**Fix:**
1. Edit `start_server_on_boot.bat`
2. Check the path is correct
3. Make sure Python path is correct

### Can't access from other devices?

1. **Check laptop is ON** (obviously!)
2. **Check same WiFi network**
3. **Check Windows Firewall** (may need to allow port 8000)
4. **Try:** `http://10.129.1.193:8000`

### Need to stop auto-start?

1. Open Startup folder (`shell:startup`)
2. Delete `start_server_on_boot.bat`
3. Done!

## Advanced: Run in Background

If you want the server to run silently (no window):

1. Change file extension to `.vbs`
2. Or use Task Scheduler with "Run whether user is logged on or not"

## Summary

✅ **Done!** Server now starts automatically on boot  
✅ **Access:** `http://10.129.1.193:8000` from any device  
✅ **Requirement:** Laptop must be ON

Enjoy your always-available PoseAnimator.com! 🎉

