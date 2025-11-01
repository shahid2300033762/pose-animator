"""
Simple working version of PoseAnimator - Clean and minimal.
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import mediapipe as mp
import time

class SimplePoseAnimator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PoseAnimator - Simple Working Version")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.cap = None
        self.is_running = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Initialize pose detection
        try:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            print("Pose detection initialized successfully")
        except Exception as e:
            print(f"Error initializing pose detection: {e}")
            self.pose = None
        
        self._create_widgets()
        self._setup_layout()
        self._update_gui()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        self.main_frame = ttk.Frame(self.root)
        
        # Control panel
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        self.camera_label = ttk.Label(self.control_frame, text="Camera:", font=("Arial", 12))
        self.camera_combo = ttk.Combobox(self.control_frame, values=["Camera 0", "Camera 1"], width=20)
        self.camera_combo.set("Camera 0")
        self.start_button = ttk.Button(self.control_frame, text="Start Camera", command=self._start_camera)
        self.stop_button = ttk.Button(self.control_frame, text="Stop Camera", command=self._stop_camera, state="disabled")
        
        # Auto-capture controls
        self.auto_capture_var = tk.BooleanVar()
        self.auto_capture_check = ttk.Checkbutton(self.control_frame, text="Auto Capture (10s)", 
                                                  variable=self.auto_capture_var)
        self.capture_status_label = ttk.Label(self.control_frame, text="Captures: 0", font=("Arial", 12, "bold"))
        self.countdown_label = ttk.Label(self.control_frame, text="Next capture in: --", font=("Arial", 12))
        
        # Display area
        self.display_frame = ttk.LabelFrame(self.main_frame, text="Pose Animation", padding=10)
        self.video_label = ttk.Label(self.display_frame, text="Pose animation will appear here", 
                                    background="black", foreground="white")
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief="sunken", font=("Arial", 11))
        self.fps_label = ttk.Label(self.status_frame, text="FPS: 0", font=("Arial", 11, "bold"))
        
        # Info text
        self.info_text = tk.Text(self.main_frame, height=15, width=50, state="disabled")
        self.info_text.insert(1.0, """PoseAnimator - Simple Working Version

Features:
• Real-time pose animation only
• Live pose detection and drawing
• Auto-capture every 10 seconds
• MediaPipe pose detection technology

Controls:
• Click 'Start Camera' to begin
• Click 'Stop Camera' to stop
• Check 'Auto Capture' for screenshots
• Select camera from dropdown

Tips:
• Stand 2-3 feet from camera
• Ensure good lighting
• Best results with full body visible
• Only pose animation is displayed (no live feed)""")
    
    def _setup_layout(self):
        """Setup GUI layout."""
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control frame
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.camera_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.camera_combo.grid(row=0, column=1, padx=(0, 10))
        self.start_button.grid(row=0, column=2, padx=(10, 5))
        self.stop_button.grid(row=0, column=3, padx=(5, 10))
        self.auto_capture_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 5))
        self.capture_status_label.grid(row=1, column=2, padx=(10, 5), pady=(10, 5))
        self.countdown_label.grid(row=1, column=3, padx=(5, 0), pady=(10, 5))
        
        # Display frame
        self.display_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 5))
        self.video_label.pack(fill="both", expand=True)
        
        # Info text
        self.info_text.grid(row=2, column=1, sticky="nsew", padx=(5, 0))
        
        # Status frame
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.status_label.pack(side="left", fill="x", expand=True)
        self.fps_label.pack(side="right", padx=(10, 0))
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
    
    def _start_camera(self):
        """Start camera capture."""
        try:
            camera_index = int(self.camera_combo.get().split()[-1])
            self.cap = cv2.VideoCapture(camera_index)
            
            if self.cap.isOpened():
                self.is_running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self.status_label.config(text="Camera running")
                print("Camera started successfully")
            else:
                print("Failed to open camera")
                self.status_label.config(text="Failed to open camera")
        except Exception as e:
            print(f"Error starting camera: {e}")
            self.status_label.config(text=f"Error: {e}")
    
    def _stop_camera(self):
        """Stop camera capture."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Camera stopped")
        print("Camera stopped")
    
    def _update_gui(self):
        """Update GUI elements."""
        if self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret:
                    # Resize frame
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Convert BGR to RGB for MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Create pose animation with black background
                    pose_frame = np.zeros_like(frame, dtype=np.uint8)
                    if self.pose:
                        results = self.pose.process(rgb_frame)
                        if results.pose_landmarks:
                            # Draw pose landmarks on black background
                            self.mp_drawing.draw_landmarks(
                                pose_frame, 
                                results.pose_landmarks, 
                                self.mp_pose.POSE_CONNECTIONS,
                                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=4),
                                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=3)
                            )
                        else:
                            # No pose detected - show message
                            cv2.putText(pose_frame, "No Pose Detected", (50, 240), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (150, 150, 150), 3)
                            cv2.putText(pose_frame, "Position yourself in camera view", (20, 290), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 100, 100), 2)
                    
                    # Use only pose animation (no live feed)
                    display_frame = pose_frame
                    
                    # Convert to PIL Image
                    display_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(display_rgb)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update label
                    self.video_label.config(image=photo)
                    self.video_label.image = photo
                    
                    # Update FPS
                    self._update_fps()
            except Exception as e:
                print(f"Error in update loop: {e}")
        
        # Schedule next update
        self.root.after(33, self._update_gui)
    
    def _update_fps(self):
        """Update FPS counter."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time
            self.fps_label.config(text=f"FPS: {self.current_fps}")
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

def main():
    """Main function."""
    print("Starting PoseAnimator Simple Working Version...")
    print("This version avoids the complex dependencies and errors.")
    
    app = SimplePoseAnimator()
    app.run()

if __name__ == "__main__":
    main()
