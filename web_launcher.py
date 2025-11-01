import os
import sys
import subprocess
import urllib.parse
import time
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json


def json_escape(s: str) -> str:
    """Escape string for JSON output."""
    try:
        # naive escape to keep simple without importing json
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    except Exception:
        return '"unknown error"'


APP_PROCESS = None
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, 'static')


def file_exists(path):
    try:
        return os.path.exists(path)
    except Exception:
        return False


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    def _send_text(self, code, text, content_type='text/plain; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))
    
    def _send_json(self, code, data):
        self._send_text(code, json.dumps(data), 'application/json')

    def _send_file(self, fs_path, content_type='text/html; charset=utf-8'):
        if not file_exists(fs_path):
            self._send_text(404, 'Not Found')
            return
        try:
            with open(fs_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._send_text(500, f'Error reading file: {e}')

    def do_GET(self):
        global APP_PROCESS
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Basic request logging for diagnostics
        try:
            print(f"[web] GET {path} query={query}")
        except Exception:
            pass

        if path in ('/', '/index', '/index.html'):
            index_path = os.path.join(STATIC_DIR, 'index.html')
            self._send_file(index_path, content_type='text/html; charset=utf-8')
            return

        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            target = os.path.join(STATIC_DIR, rel)
            # naive content-type handling
            ext = os.path.splitext(target)[1].lower()
            ct = 'text/plain; charset=utf-8'
            if ext == '.html':
                ct = 'text/html; charset=utf-8'
            elif ext == '.css':
                ct = 'text/css; charset=utf-8'
            elif ext == '.js':
                ct = 'application/javascript; charset=utf-8'
            elif ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg'):
                ct = 'image/' + (ext[1:] if ext != '.svg' else 'svg+xml')
            self._send_file(target, content_type=ct)
            return

        if path == '/launch':
            # Launch web-based version instead (runs in browser)
            # Redirect to web version on port 8001
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
                s.close()
                web_url = f'http://{local_ip}:8001/'
            except Exception:
                web_url = 'http://localhost:8001/'
            
            # Start web version in background if not running
            web_process = None
            try:
                # Check if web version is already running
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(0.5)
                result = test_socket.connect_ex(('localhost', 8001))
                test_socket.close()
                
                if result != 0:  # Port not in use, start server
                    web_process = subprocess.Popen([sys.executable, 'web_pose_animator.py'], cwd=ROOT_DIR)
                    time.sleep(1)  # Give it a moment to start
            except Exception:
                pass
            
            self._send_json(200, {
                'ok': True,
                'message': 'Opening web version in browser window...',
                'redirect': web_url
            })
            return
        
        if path == '/launch-desktop':
            # Start the desktop app if not already running
            if APP_PROCESS and APP_PROCESS.poll() is None:
                self._send_text(200, '{"ok": true, "message": "Project already running."}', content_type='application/json')
                return
            try:
                # Use current Python interpreter to avoid PATH issues
                APP_PROCESS = subprocess.Popen([sys.executable, 'run_app.py'], cwd=ROOT_DIR)
                self._send_text(200, '{"ok": true, "message": "Launched desktop app."}', content_type='application/json')
            except Exception as e:
                self._send_text(500, '{"ok": false, "error": ' + json_escape(str(e)) + '}', content_type='application/json')
            return

        if path == '/status':
            running = APP_PROCESS is not None and APP_PROCESS.poll() is None
            self._send_text(200, ('{"running": true}' if running else '{"running": false}'), content_type='application/json')
            return

        self._send_text(404, 'Not Found')


def main():
    import socket
    port = int(os.environ.get('PORT', '8000'))
    
    # Bind to all interfaces (0.0.0.0) to allow network access
    host = '0.0.0.0'
    server = ThreadingHTTPServer((host, port), Handler)
    
    # Get local IP address for display
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f'\n{"="*60}')
        print(f'   PoseAnimator.com Web Server Started!')
        print(f'{"="*60}')
        print(f'   Local access:    http://localhost:{port}/')
        print(f'   Network access:  http://{local_ip}:{port}/')
        print(f'   Any device:      http://{local_ip}:{port}/')
        print(f'{"="*60}\n')
    except Exception:
        print(f'\n{"="*60}')
        print(f'   PoseAnimator.com Web Server Started!')
        print(f'{"="*60}')
        print(f'   Access at:       http://localhost:{port}/')
        print(f'{"="*60}\n')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\nShutting down web server...')
    finally:
        server.server_close()
        print('Server stopped.')


if __name__ == '__main__':
    main()