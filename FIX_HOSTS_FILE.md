# 🔧 Fix: "This Site Can't Be Reached"

## Problem
The hosts file entry might not be working. Here's how to fix it:

## Solution 1: Use IP Address Directly (Easiest)

**Just use this URL in your browser:**
```
http://10.129.1.193:8000
```

This works on ANY device on your network!

## Solution 2: Fix Hosts File Entry

If you want to use `poseanimator.com:8000`:

1. **Open hosts file as Administrator:**
   - Press `Win + R`
   - Type: `notepad`
   - Right-click Notepad → Run as Administrator
   - Open: `C:\Windows\System32\drivers\etc\hosts`

2. **Add this EXACT line (with TAB between IP and domain):**
   ```
   10.129.1.193	poseanimator.com
   ```
   **Important:** Use a TAB, not spaces!

3. **Save the file** (Ctrl+S)

4. **Flush DNS again:**
   ```
   ipconfig /flushdns
   ```

5. **Close and reopen your browser completely**

6. **Try:** `http://poseanimator.com:8000`

## Solution 3: Check Server is Running

Run this to check:
```bash
netstat -ano | findstr :8000
```

If nothing shows, start the server:
```bash
python web_launcher.py
```

## Quick Test

Try these URLs in order:

1. ✅ **http://localhost:8000** (should always work)
2. ✅ **http://10.129.1.193:8000** (works from any device on network)
3. ⚠️ **http://poseanimator.com:8000** (only if hosts file is set up)

## Recommended Solution

**Just use the IP address:**
- **http://10.129.1.193:8000**

This works immediately on all devices without any setup!


