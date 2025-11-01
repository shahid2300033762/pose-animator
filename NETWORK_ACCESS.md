# 🌐 PoseAnimator.com Network Access Setup

## How to Access on Any Device on Your Network

### Your Current Setup

**Your Computer IP:** `10.129.1.193`  
**Port:** `8000`

### Access Methods

#### Option 1: Direct IP Access (Easiest)
1. Run the web launcher: `start_website.bat`
2. On any device on your network, open a browser
3. Go to: **`http://10.129.1.193:8000`**

#### Option 2: Make It Look Like poseanimator.com (Advanced)

To make it so you can type `poseanimator.com` in any browser on your network:

### Windows:
1. Open Notepad as Administrator
2. Go to: `C:\Windows\System32\drivers\etc\hosts`
3. Add this line at the bottom:
   ```
   10.129.1.193    poseanimator.com
   ```
4. Save and close
5. Now you can visit **`http://poseanimator.com:8000`** from ANY device on your network!

### Mac/Linux:
1. Open terminal
2. Run: `sudo nano /etc/hosts`
3. Add this line:
   ```
   10.129.1.193    poseanimator.com
   ```
4. Save (Ctrl+X, then Y, then Enter)
5. Visit **`http://poseanimator.com:8000`** on ANY device!

### Option 3: Full Internet Setup (Requires Hosting)

To make `poseanimator.com` work from anywhere on the internet:

1. **Get a VPS Server** (AWS, DigitalOcean, etc.)
2. **Buy a Domain** (Namecheap, GoDaddy) - `poseanimator.com`
3. **Point DNS** from poseanimator.com → Your server IP
4. **Deploy the web launcher** to the server
5. **Add HTTPS** with Let's Encrypt

**Note**: This won't work fully because your app needs to run on the user's computer with camera access. You'd need to create a web-based version or installer.

## Quick Start

1. **Start the server:**
   ```
   python web_launcher.py
   ```

2. **On any device on your WiFi:**
   - Phone, tablet, laptop, etc.
   - Open browser
   - Go to: `http://10.129.1.193:8000`
   - The beautiful website will load!

3. **If you added hosts file:**
   - Go to: `http://poseanimator.com:8000`
   - Works on ALL devices on your network!

## Troubleshooting

### Can't access from other device?
- Make sure both devices are on the **same WiFi network**
- Check Windows Firewall allows port 8000
- Try temporarily disabling Windows Firewall to test

### Firewall Setup:
1. Windows Security → Firewall
2. Allow an app through firewall
3. Add Python or port 8000

### Still not working?
Use the direct IP: `http://10.129.1.193:8000`

## Your Network Info

- **Your IP:** 10.129.1.193
- **Port:** 8000
- **Local:** http://localhost:8000
- **Network:** http://10.129.1.193:8000
- **Domain:** http://poseanimator.com:8000 (after hosts setup)

## Summary

✅ **Currently working:** http://localhost:8000 (your computer only)  
✅ **After setup:** http://10.129.1.193:8000 (any device on WiFi)  
✅ **Ultimate:** http://poseanimator.com:8000 (after hosts file setup)

Enjoy your professional PoseAnimator.com website! 🎉


