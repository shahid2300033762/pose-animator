"""
Web-based Pose Animator - Runs entirely in browser window
"""
import os
import sys
import cv2
import base64
import mediapipe as mp
import numpy as np
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib.parse
import json

# Add utils path for camera helper
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
utils_path = os.path.join(ROOT_DIR, "utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)

try:
    from camera_helper import initialize_camera, set_camera_properties
    CAMERA_HELPER_AVAILABLE = True
except ImportError:
    CAMERA_HELPER_AVAILABLE = False

# Global camera and pose detector
camera = None
pose_detector = None
is_camera_running = False
camera_lock = threading.Lock()

def init_camera():
    """Initialize camera"""
    global camera, is_camera_running
    with camera_lock:
        if camera is not None:
            return True
        
        try:
            if CAMERA_HELPER_AVAILABLE:
                camera, _ = initialize_camera(preferred_index=0, max_retries=3, max_indices=3)
                if camera is not None:
                    set_camera_properties(camera, width=640, height=480, fps=30)
            else:
                # Fallback initialization
                for idx in range(3):
                    camera = cv2.VideoCapture(idx)
                    if camera.isOpened():
                        ret, frame = camera.read()
                        if ret and frame is not None:
                            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            break
                        camera.release()
                        camera = None
            
            if camera is not None and camera.isOpened():
                is_camera_running = True
                return True
        except Exception as e:
            print(f"Camera init error: {e}")
        
        return False

def init_pose_detector():
    """Initialize MediaPipe pose detector"""
    global pose_detector
    if pose_detector is None:
        mp_pose = mp.solutions.pose
        pose_detector = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    return pose_detector

def get_frame():
    """Get current frame from camera"""
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            return None
        
        ret, frame = camera.read()
        if not ret or frame is None:
            return None
        
        return frame

def release_camera():
    """Release camera resources"""
    global camera, is_camera_running
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
        is_camera_running = False

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def _send_text(self, code, text, content_type='text/plain; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))
    
    def _send_json(self, code, data):
        self._send_text(code, json.dumps(data), 'application/json')
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == '/' or path == '/index.html':
            self._send_text(200, get_web_html(), 'text/html')
            return
        
        if path == '/start':
            if init_camera():
                init_pose_detector()
                self._send_json(200, {'ok': True, 'message': 'Camera started'})
            else:
                self._send_json(500, {'ok': False, 'error': 'Failed to start camera'})
            return
        
        if path == '/stop':
            release_camera()
            self._send_json(200, {'ok': True, 'message': 'Camera stopped'})
            return
        
        if path == '/frame':
            frame = get_frame()
            if frame is None:
                self._send_json(404, {'error': 'No frame available'})
                return
            
            # Process with pose detection
            pose_det = init_pose_detector()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose_det.process(frame_rgb)
            
            # Draw pose landmarks if detected
            if results.pose_landmarks:
                mp_drawing = mp.solutions.drawing_utils
                mp_pose = mp.solutions.pose
                mp_drawing.draw_landmarks(
                    frame_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            self._send_json(200, {
                'frame': f'data:image/jpeg;base64,{frame_base64}',
                'has_pose': results.pose_landmarks is not None
            })
            return
        
        if path == '/status':
            self._send_json(200, {'running': is_camera_running})
            return
        
        self._send_text(404, 'Not Found')
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def get_web_html():
    """Return the HTML for web-based pose animator"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pose Animator - Web Version</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0E0F1A 0%, #1a1b2e 100%);
            color: white;
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: rgba(0, 0, 0, 0.5);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 194, 255, 0.3);
        }
        .header h1 {
            font-size: 24px;
            background: linear-gradient(135deg, #00C2FF 0%, #8A2BE2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .controls {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-start {
            background: linear-gradient(135deg, #00C2FF 0%, #8A2BE2 100%);
            color: white;
        }
        .btn-start:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 194, 255, 0.4);
        }
        .btn-stop {
            background: #ff4444;
            color: white;
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .main-content {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }
        .video-container {
            position: relative;
            max-width: 100%;
            max-height: 100%;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }
        #videoCanvas {
            display: block;
            width: 100%;
            height: auto;
            max-width: 1280px;
            max-height: 720px;
        }
        .status-overlay {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-indicator.active {
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }
        .status-indicator.inactive {
            background: #ff4444;
        }
        .pose-indicator {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
        }
        .pose-detected {
            color: #00ff00;
        }
        .no-pose {
            color: #ffaa00;
        }
        .loading {
            text-align: center;
            padding: 40px;
        }
        .spinner {
            border: 4px solid rgba(0, 194, 255, 0.3);
            border-top: 4px solid #00C2FF;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Pose Animator - Web Edition</h1>
        <div class="controls">
            <button id="startBtn" class="btn btn-start" onclick="startCamera()">▶ Start Camera</button>
            <button id="stopBtn" class="btn btn-stop" onclick="stopCamera()" disabled>⏹ Stop Camera</button>
        </div>
    </div>
    
    <div class="main-content">
        <div class="video-container" id="videoContainer">
            <canvas id="videoCanvas"></canvas>
            <div class="status-overlay">
                <span class="status-indicator" id="statusIndicator"></span>
                <span id="statusText">Not Running</span>
            </div>
            <div class="pose-indicator" id="poseIndicator">
                <span id="poseText">Waiting for pose detection...</span>
            </div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        let frameInterval = null;
        const canvas = document.getElementById('videoCanvas');
        const ctx = canvas.getContext('2d');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const poseIndicator = document.getElementById('poseIndicator');
        const poseText = document.getElementById('poseText');
        
        async function startCamera() {
            try {
                startBtn.disabled = true;
                statusText.textContent = 'Starting...';
                
                const response = await fetch('/start');
                const data = await response.json();
                
                if (data.ok) {
                    isRunning = true;
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    statusIndicator.className = 'status-indicator active';
                    statusText.textContent = 'Running';
                    
                    // Start frame loop
                    fetchFrame();
                    frameInterval = setInterval(fetchFrame, 33); // ~30 FPS
                } else {
                    alert('Failed to start camera: ' + (data.error || 'Unknown error'));
                    startBtn.disabled = false;
                }
            } catch (error) {
                alert('Error starting camera: ' + error.message);
                startBtn.disabled = false;
            }
        }
        
        async function stopCamera() {
            isRunning = false;
            if (frameInterval) {
                clearInterval(frameInterval);
                frameInterval = null;
            }
            
            try {
                await fetch('/stop');
            } catch (e) {
                console.error('Stop error:', e);
            }
            
            startBtn.disabled = false;
            stopBtn.disabled = true;
            statusIndicator.className = 'status-indicator inactive';
            statusText.textContent = 'Stopped';
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            poseText.textContent = 'Camera stopped';
            poseIndicator.className = 'pose-indicator no-pose';
        }
        
        async function fetchFrame() {
            if (!isRunning) return;
            
            try {
                const response = await fetch('/frame?t=' + Date.now());
                const data = await response.json();
                
                if (data.frame) {
                    const img = new Image();
                    img.onload = function() {
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);
                    };
                    img.src = data.frame;
                    
                    // Update pose indicator
                    if (data.has_pose) {
                        poseText.textContent = '✅ Pose Detected';
                        poseIndicator.className = 'pose-indicator pose-detected';
                    } else {
                        poseText.textContent = '⏳ No pose detected';
                        poseIndicator.className = 'pose-indicator no-pose';
                    }
                }
            } catch (error) {
                console.error('Frame fetch error:', error);
                if (error.message.includes('404') || error.message.includes('Failed')) {
                    // Camera might have stopped
                    stopCamera();
                }
            }
        }
        
        // Initialize on page load
        window.addEventListener('load', () => {
            statusIndicator.className = 'status-indicator inactive';
        });
    </script>
</body>
</html>"""

def main():
    import socket
    port = int(os.environ.get('PORT', '8001'))
    host = '0.0.0.0'
    
    server = ThreadingHTTPServer((host, port), Handler)
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f'\n{"="*60}')
        print(f'   Pose Animator - Web Version Started!')
        print(f'{"="*60}')
        print(f'   Local:    http://localhost:{port}/')
        print(f'   Network: http://{local_ip}:{port}/')
        print(f'   Mobile:   http://{local_ip}:{port}/')
        print(f'{"="*60}\n')
    except Exception:
        print(f'\n{"="*60}')
        print(f'   Pose Animator - Web Version Started!')
        print(f'   Access at: http://localhost:{port}/')
        print(f'{"="*60}\n')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\nShutting down...')
        release_camera()
    finally:
        server.server_close()
        release_camera()
        print('Server stopped.')

if __name__ == '__main__':
    main()

