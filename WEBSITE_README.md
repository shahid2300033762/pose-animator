# 🌐 PoseAnimator.com - Web Launcher

Welcome to the PoseAnimator web launcher! This provides a beautiful, modern web interface to launch your Pose Animator desktop application.

## ✨ Features

- 🎨 **Modern, Beautiful UI** - Stunning gradient design with animations
- 🚀 **Auto-Launch** - Automatically launches the app when you visit the page
- 📊 **Real-Time Status** - Shows if the app is running or stopped
- 🎯 **One-Click Launch** - Simple button to start your animation studio
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Windows
Double-click `start_website.bat` or run:
```bash
python web_launcher.py
```

### Mac/Linux
```bash
chmod +x start_website.sh
./start_website.sh
```

Or directly:
```bash
python3 web_launcher.py
```

Then open your browser to: **http://localhost:8000**

## 📝 How It Works

1. The web server starts on port 8000
2. Visit http://localhost:8000 in your browser
3. The page automatically launches `run_app.py` after 1 second
4. The Pose Animator desktop app opens with login screen
5. You can click the button again anytime to re-launch

## 🎨 Customization

### Change Port
Edit `web_launcher.py`:
```python
port = int(os.environ.get('PORT', '8000'))  # Change 8000 to your desired port
```

### Disable Auto-Launch
Add `?auto=0` to the URL:
```
http://localhost:8000/?auto=0
```

### Change Auto-Launch Delay
Edit `static/index.html` around line 431:
```javascript
setTimeout(() => {
    if (launchCount === 0) {
        launchCount++;
        launchApp();
    }
}, 1000);  // Change 1000ms to your desired delay
```

## 🔧 Technical Details

- **Backend**: Python HTTP Server with threading
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Launch**: Subprocess spawns `run_app.py`
- **Status**: HTTP polling every 3 seconds

## 🌍 Deployment

To make this accessible over the internet, you would need:

1. **Hosting**: Deploy the web server to a VPS (AWS, DigitalOcean, etc.)
2. **Domain**: Point `poseanimator.com` to your server IP
3. **Security**: Add authentication and HTTPS
4. **Firewall**: Configure ports and access rules

**Note**: Currently, this only works locally because the desktop app needs to run on your machine with camera access.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Can't Launch App
- Make sure `run_app.py` exists in the same directory
- Check Python is in your PATH
- Verify all dependencies are installed

### Browser Not Opening
Manually navigate to: http://localhost:8000

## 📄 License

Part of the Pose Animator project.

## 🆘 Support

For issues, check the main README.md or open an issue on GitHub.


