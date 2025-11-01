import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance
import time
import os
from datetime import datetime
import mediapipe as mp
import threading
import math
import sys

# Add parent directory to path to import camera_helper
# From pose_animator-master/final_app.py, we need to go up to workspace root, then into utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
utils_path = os.path.join(parent_dir, "utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)
try:
    from camera_helper import initialize_camera, set_camera_properties
    CAMERA_HELPER_AVAILABLE = True
    print("Successfully imported camera_helper")
except ImportError as e:
    print(f"Warning: Could not import camera_helper: {e}. Using fallback camera initialization.")
    CAMERA_HELPER_AVAILABLE = False

class ModernPoseAnimatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pose Animator - Loading...")
        self.root.withdraw() # Hide window during setup

        # --- Splash Screen ---
        self.splash = tk.Toplevel(self.root)
        self.splash.overrideredirect(True)
        self.splash.geometry("400x250")
        self.center_window(self.splash)
        splash_canvas = tk.Canvas(self.splash, bg='#0E0F1A', highlightthickness=0)
        splash_canvas.pack(fill='both', expand=True)
        try:
            # A simple logo drawn with canvas
            splash_canvas.create_text(200, 100, text="🅿️🅰️", font=('Poppins', 60, 'bold'), fill='#00C2FF')
            self.loading_label = tk.Label(splash_canvas, text="Loading Model...", font=('Inter', 12), fg='#FFFFFF', bg='#0E0F1A')
            self.loading_label.place(x=140, y=180)
        except tk.TclError:
            # Fallback if fonts are not available
            self.loading_label = tk.Label(splash_canvas, text="Loading...", font=('Arial', 12), fg='#FFFFFF', bg='#0E0F1A')
            self.loading_label.place(x=160, y=180)

        self.root.after(500, self.initialize_main_app)

    def center_window(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')

    def initialize_main_app(self):
        self.loading_label.config(text="Initializing UI...")
        self.splash.update()
        # Colors and Fonts
        self.colors = {
            'background': '#0E0F1A',
            'primary': '#00C2FF', 'accent': '#8A2BE2',
            'success': '#00FFB2', 'error': '#FF4D4D',
            'text': '#FFFFFF', 'panel_bg': '#161827',
            'dark_bg': '#0A0B14'
        }
        self.fonts = {
            'header': ('Poppins', 24, 'bold'), 'body': ('Inter', 12),
            'button': ('Montserrat', 12, 'bold'), 'label': ('Inter', 10, 'bold')
        }

        # App Settings
        self.settings = {
            "resolution": tk.StringVar(value="640x480"),
            "model_complexity": tk.StringVar(value="Light"),
            "smoothness": tk.DoubleVar(value=0.8),
            "show_overlay": tk.BooleanVar(value=True),
            "animation_style": tk.StringVar(value="Cartoon")
        }

        # App Variables
        self.cap = None
        self.is_running = False
        self.pose_detector = None
        self.fps, self.frame_count, self.detected_persons, self.active_joints = 0, 0, 0, 0
        self.last_frame_time = time.time()
        self.previous_landmarks = None

        # Setup Main Window
        self.root.title("Pose Animator")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.colors['background'])
        
        # Initialize pose detector first (while splash is still available)
        self._init_pose_detector()
        
        self._create_widgets()

        # Show main window and bring it to the foreground
        try:
            if hasattr(self, 'splash') and self.splash is not None:
                self.splash.destroy()
        except Exception:
            pass
        try:
            self.root.deiconify()
            self.root.state('normal')
            self.root.lift()
            self.root.focus_force()
            # Make topmost briefly to avoid minimized/behind-other-windows state
            self.root.attributes('-topmost', True)
            self.root.after(800, lambda: self.root.attributes('-topmost', False))
        except Exception:
            pass

    def _init_pose_detector(self):
        try:
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            model_complexity = 1 if self.settings['model_complexity'].get() == "Accurate" else 0
            self.pose = self.mp_pose.Pose(
                static_image_mode=False, model_complexity=model_complexity,
                min_detection_confidence=0.5, min_tracking_confidence=0.5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize pose detector: {e}")
            self.pose = None

    def _create_widgets(self):
        # Top Navbar
        navbar = tk.Frame(self.root, bg=self.colors['panel_bg'], height=50); navbar.pack(side='top', fill='x')
        tk.Label(navbar, text="Pose Animator", font=self.fonts['header'], fg=self.colors['primary'], bg=self.colors['panel_bg']).pack(side='left', padx=20)
        nav_buttons = {'Settings': '⚙️', 'Help': '❓', 'Logout': '🔓', 'Exit': '❌'}
        for name, icon in nav_buttons.items():
            tk.Button(navbar, text=f"{icon} {name}", font=self.fonts['button'], fg=self.colors['text'], bg=self.colors['panel_bg'], relief='flat', command=lambda n=name: self._handle_nav(n)).pack(side='right', padx=10)

        # Main Content
        main_frame = tk.Frame(self.root, bg=self.colors['background']); main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1); main_frame.grid_columnconfigure(1, weight=1)

        # Camera Panel
        self.camera_panel = tk.Frame(main_frame, bg=self.colors['panel_bg'], highlightbackground=self.colors['error'], highlightthickness=2); self.camera_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.camera_panel.grid_rowconfigure(1, weight=1); self.camera_panel.grid_columnconfigure(0, weight=1)
        tk.Label(self.camera_panel, text="◀ Live Camera ▶", font=self.fonts['body'], fg=self.colors['text'], bg=self.colors['panel_bg']).grid(row=0, column=0, pady=10)
        self.live_video_label = tk.Label(self.camera_panel, bg=self.colors['dark_bg']); self.live_video_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Pose Panel
        pose_panel = tk.Frame(main_frame, bg=self.colors['panel_bg'], highlightbackground=self.colors['accent'], highlightthickness=1); pose_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        pose_panel.grid_rowconfigure(1, weight=1); pose_panel.grid_columnconfigure(0, weight=1)
        pose_header_frame = tk.Frame(pose_panel, bg=self.colors['panel_bg']); pose_header_frame.grid(row=0, column=0, pady=10, sticky='ew')
        tk.Label(pose_header_frame, text="◀ Pose Animation ▶", font=self.fonts['body'], fg=self.colors['text'], bg=self.colors['panel_bg']).pack(side='left', padx=20)
        self.animation_menu = ttk.Combobox(pose_header_frame, textvariable=self.settings["animation_style"], values=["Cartoon", "Stick Figure", "3D Avatar"], state="readonly", width=12); self.animation_menu.pack(side='right', padx=20); self.animation_menu.set('Cartoon')
        self.pose_video_label = tk.Label(pose_panel, bg=self.colors['dark_bg']); self.pose_video_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Stats Dashboard
        stats_frame = tk.Frame(main_frame, bg=self.colors['panel_bg']); stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        self.detected_person_label = tk.Label(stats_frame, text="👤 Detected: 0", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['panel_bg']); self.detected_person_label.pack(side='left', padx=20)
        self.active_joints_label = tk.Label(stats_frame, text="Active Joints: 0", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['panel_bg']); self.active_joints_label.pack(side='left', padx=20)
        self.fps_label = tk.Label(stats_frame, text="FPS: 0", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['panel_bg']); self.fps_label.pack(side='left', padx=20)

        # Controls
        control_frame = tk.Frame(self.root, bg=self.colors['panel_bg'], height=60); control_frame.pack(side='bottom', fill='x', padx=20, pady=(0,20))
        self.start_btn = tk.Button(control_frame, text="▶ Start", font=self.fonts['button'], bg=self.colors['success'], fg=self.colors['background'], relief='flat', command=self._start); self.start_btn.pack(side='left', padx=20)
        self.stop_btn = tk.Button(control_frame, text="■ Stop", font=self.fonts['button'], bg=self.colors['error'], fg=self.colors['text'], relief='flat', command=self._stop, state='disabled'); self.stop_btn.pack(side='left', padx=20)
        self.capture_btn = tk.Button(control_frame, text="📸 Capture", font=self.fonts['button'], bg=self.colors['accent'], fg=self.colors['text'], relief='flat', command=self._capture_frame, state='disabled'); self.capture_btn.pack(side='left', padx=20)
        self.overlay_toggle = tk.Checkbutton(control_frame, text="Show Pose Overlay", var=self.settings['show_overlay'], onvalue=True, offvalue=False, bg=self.colors['panel_bg'], fg=self.colors['text'], selectcolor=self.colors['dark_bg'], font=self.fonts['label']); self.overlay_toggle.pack(side='right', padx=20)

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Status: Ready", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['primary'], anchor='w'); self.status_bar.pack(side='bottom', fill='x')
        self.root.after(10, self._update_gui)

    def _handle_nav(self, cmd):
        if cmd == "Exit": self._on_closing()
        elif cmd == "Logout": self._logout()
        elif cmd == "Settings": self._show_settings_modal()
        elif cmd == "Help": self._show_help_modal()

    def _logout(self):
        # Stop camera if running, then close the window
        if self.is_running:
            self._stop()
        # Optionally show a status update before closing
        try:
            self.update_status("Status: Logging out...", self.colors['accent'])
            self.root.update_idletasks()
        except Exception:
            pass
        self.root.destroy()

    def _show_settings_modal(self):
        win = tk.Toplevel(self.root); win.title("Settings"); win.geometry("400x400"); win.configure(bg=self.colors['background']); win.transient(self.root); win.grab_set()
        tk.Label(win, text="Settings", font=self.fonts['header'], fg=self.colors['primary'], bg=self.colors['background']).pack(pady=20)
        tk.Label(win, text="Camera Resolution", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['background']).pack()
        ttk.Combobox(win, textvariable=self.settings['resolution'], values=['640x480', '1280x720'], state="readonly").pack(pady=5)
        tk.Label(win, text="Pose Detection Model", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['background']).pack()
        ttk.Combobox(win, textvariable=self.settings['model_complexity'], values=['Light', 'Accurate'], state="readonly").pack(pady=5)
        tk.Label(win, text="Animation Smoothness", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['background']).pack()
        tk.Scale(win, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.settings['smoothness'], bg=self.colors['background'], fg=self.colors['text'], troughcolor=self.colors['panel_bg']).pack(pady=5, fill='x', padx=20)
        tk.Button(win, text="Apply & Close", command=lambda: self._apply_settings(win), font=self.fonts['button'], bg=self.colors['success'], fg=self.colors['background']).pack(pady=20)

    def _show_help_modal(self):
        win = tk.Toplevel(self.root); win.title("Help"); win.geometry("500x400"); win.configure(bg=self.colors['background']); win.transient(self.root); win.grab_set()
        tk.Label(win, text="Mini-Manual", font=self.fonts['header'], fg=self.colors['primary'], bg=self.colors['background']).pack(pady=10)
        help_text = """1. Start Camera: Press '▶ Start' to begin.
2. Animate: Your pose is animated in real-time.
3. Change Style: Select animation style from the dropdown.
4. Capture: Press '📸 Capture' to save a snapshot.
5. Settings: Click '⚙️ Settings' to change resolution, model, etc.
6. Overlay: Toggle skeleton on live feed with 'Show Pose Overlay'."""
        tk.Message(win, text=help_text, font=self.fonts['body'], bg=self.colors['panel_bg'], fg=self.colors['text'], width=450, justify='left').pack(padx=20, pady=10)
        tk.Button(win, text="Close", command=win.destroy, font=self.fonts['button'], bg=self.colors['accent'], fg=self.colors['text']).pack(pady=10)

    def _apply_settings(self, window):
        self.update_status("Status: Applying settings...", self.colors['accent'])
        self._init_pose_detector()
        window.destroy()

    def _start(self):
        if self.is_running: return
        self.is_running = True
        self.update_status("Status: Starting Camera...", self.colors['accent'])
        self.camera_panel.config(highlightbackground=self.colors['accent']); self.root.update_idletasks()
        threading.Thread(target=self._start_camera_thread, daemon=True).start()

    def _start_camera_thread(self):
        try:
            W, H = map(int, self.settings['resolution'].get().split('x'))
            
            # Use camera_helper if available for robust initialization
            if CAMERA_HELPER_AVAILABLE:
                try:
                    self.cap, working_index = initialize_camera(preferred_index=0, max_retries=3, max_indices=3)
                    if self.cap is None:
                        raise Exception("Could not initialize any camera")
                    # Set camera properties
                    set_camera_properties(self.cap, width=W, height=H, fps=30)
                except NameError:
                    # Fallback to standard initialization
                    self.cap = cv2.VideoCapture(0)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
                    if not self.cap.isOpened():
                        raise Exception("Cannot open camera")
            else:
                # Fallback: Try multiple camera indices
                self.cap = None
                for idx in range(3):  # Try indices 0, 1, 2
                    print(f"Trying camera index {idx}...")
                    self.cap = cv2.VideoCapture(idx)
                    if self.cap.isOpened():
                        # Verify we can read a frame
                        ret, frame = self.cap.read()
                        if ret and frame is not None:
                            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
                            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
                            print(f"Successfully opened camera {idx}")
                            break
                    else:
                        if self.cap is not None:
                            self.cap.release()
                            self.cap = None
                
                if self.cap is None:
                    raise Exception("Cannot open any camera. Please check your camera connection.")
            
            self.root.after(0, self._update_ui_on_start)
        except Exception as e:
            self.is_running = False
            self.root.after(0, lambda: messagebox.showerror("Camera Error", str(e)))
            self.root.after(0, self.update_status, "Status: Camera Error", self.colors['error'])

    def _update_ui_on_start(self):
        self.start_btn.config(state='disabled'); self.stop_btn.config(state='normal'); self.capture_btn.config(state='normal')
        self.update_status("Status: Running smoothly", self.colors['success'])
        self.camera_panel.config(highlightbackground=self.colors['success'])

    def _stop(self):
        if not self.is_running: return
        self.is_running = False
        self.start_btn.config(state='normal'); self.stop_btn.config(state='disabled'); self.capture_btn.config(state='disabled')
        self.camera_panel.config(highlightbackground=self.colors['error'])
        if self.cap: self.cap.release(); self.cap = None
        for label in [self.live_video_label, self.pose_video_label]: label.config(image='')
        self.detected_person_label.config(text="👤 Detected: 0"); self.active_joints_label.config(text="Active Joints: 0"); self.fps_label.config(text="FPS: 0")
        self.update_status("Status: Stopped", self.colors['error'])

    def _capture_frame(self):
        if not self.is_running or not hasattr(self, 'current_frame'): return messagebox.showwarning("Capture Error", "Camera is not running.")
        if not os.path.exists('captures'): os.makedirs('captures')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S"); filename = f"captures/capture_{timestamp}.jpg"
        live_img = Image.fromarray(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))
        pose_img = self.last_pose_image if hasattr(self, 'last_pose_image') else Image.new('RGB', live_img.size)
        combined_img = Image.new('RGB', (live_img.width * 2, live_img.height)); combined_img.paste(live_img, (0, 0)); combined_img.paste(pose_img, (live_img.width, 0))
        draw = ImageDraw.Draw(combined_img); draw.text((10, 10), timestamp, fill="yellow"); combined_img.save(filename)
        self.update_status(f"Status: Saved {filename}", self.colors['success'])

    def _update_gui(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(frame_rgb)

                if results.pose_landmarks:
                    smooth_factor = self.settings['smoothness'].get()
                    if self.previous_landmarks:
                        for i, lm in enumerate(results.pose_landmarks.landmark):
                            prev_lm = self.previous_landmarks.landmark[i]
                            lm.x = prev_lm.x * (1 - smooth_factor) + lm.x * smooth_factor
                            lm.y = prev_lm.y * (1 - smooth_factor) + lm.y * smooth_factor
                            lm.z = prev_lm.z * (1 - smooth_factor) + lm.z * smooth_factor
                    self.previous_landmarks = results.pose_landmarks

                self.detected_persons = 1 if results.pose_landmarks else 0
                self.active_joints = len(results.pose_landmarks.landmark) if results.pose_landmarks else 0
                
                # Live feed
                live_img = Image.fromarray(frame_rgb)
                if self.settings["show_overlay"].get() and results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(np.array(live_img), results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                
                self._display_image(self.live_video_label, live_img)
                self._draw_animation(results, frame.shape)
                self._update_stats()

        self.root.after(15, self._update_gui)

    def _display_image(self, label, img):
        # Fade-in effect (simple version)
        if not hasattr(label, 'imgtk'):
            img = img.copy()
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.1) # Start dim

        img_tk = ImageTk.PhotoImage(image=img)
        label.imgtk = img_tk; label.config(image=img_tk)

    def _draw_animation(self, results, shape):
        h, w, _ = shape; pose_canvas_img = Image.new('RGB', (w, h), self.colors['dark_bg'])
        draw = ImageDraw.Draw(pose_canvas_img)
        style = self.settings['animation_style'].get()
        if results.pose_landmarks:
            landmarks = [(lm.x * w, lm.y * h) for lm in results.pose_landmarks.landmark]
            if style == "Stick Figure":
                connections = self.mp_pose.POSE_CONNECTIONS
                for con in connections: draw.line((landmarks[con[0]], landmarks[con[1]]), fill=self.colors['primary'], width=4)
                for lm in landmarks: draw.ellipse([(lm[0]-5, lm[1]-5), (lm[0]+5, lm[1]+5)], fill=self.colors['accent'])
            elif style == "Cartoon":
                self._draw_cartoon_character(draw, landmarks)
            elif style == "3D Avatar":
                self._draw_3d_placeholder(draw, landmarks)
        self.last_pose_image = pose_canvas_img
        self._display_image(self.pose_video_label, pose_canvas_img)
    
    def _draw_cartoon_character(self, draw, lms):
        # Simplified cartoon drawing logic
        head = (lms[0][0], lms[0][1] - 15); draw.ellipse([(head[0]-20, head[1]-20), (head[0]+20, head[1]+20)], fill='#FFE0BD', outline=self.colors['primary'])
        body_points = [lms[12], lms[11], lms[23], lms[24]]; draw.polygon(body_points, fill='#AAAAFF', outline=self.colors['primary'])
        # Arms & Legs as thick lines
        for con in [(12,14), (14,16), (11,13), (13,15), (24,26), (26,28), (23,25), (25,27)]:
            if len(lms) > max(con): draw.line((lms[con[0]], lms[con[1]]), fill='#FFE0BD', width=15)

    def _draw_3d_placeholder(self, draw, lms):
        # Pseudo-3D with skewed ellipses
        for con in self.mp_pose.POSE_CONNECTIONS: 
            p1, p2 = lms[con[0]], lms[con[1]]
            length = math.hypot(p2[0]-p1[0], p2[1]-p1[1]); angle = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
            poly = tk.Canvas(self.root); coords = [(-length/2, -8), (length/2, -8), (length/2, 8), (-length/2, 8)]
            rotated_coords = [(x*math.cos(angle) - y*math.sin(angle) + p1[0] + (p2[0]-p1[0])/2, x*math.sin(angle) + y*math.cos(angle) + p1[1] + (p2[1]-p1[1])/2) for x,y in coords]
            draw.polygon(rotated_coords, fill=self.colors['accent'], outline=self.colors['primary'])

    def _update_stats(self):
        now = time.time()
        if now - self.last_frame_time >= 1.0:
            self.fps = self.frame_count / (now - self.last_frame_time)
            self.last_frame_time, self.frame_count = now, 0
            self.fps_label.config(text=f"FPS: {self.fps:.1f}")
            self.detected_person_label.config(text=f"👤 Detected: {self.detected_persons}")
            self.active_joints_label.config(text=f"Active Joints: {self.active_joints}")
        self.frame_count +=1

    def update_status(self, text, color):
        self.status_bar.config(text=text, bg=color)
        
    def _on_closing(self):
        if self.is_running: self._stop()
        self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernPoseAnimatorGUI()
    app.run()
