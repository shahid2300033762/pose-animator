"""
Auto-start camera with live feed + pose animation.
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import mediapipe as mp
import time

class AutoCameraPoseAnimator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Feed + Pose Animation")
        self.root.geometry("1200x600")
        
        # Variables
        self.cap = None
        self.is_running = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Initialize MediaPipe
        try:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            print("MediaPipe initialized successfully")
        except Exception as e:
            print(f"Error initializing MediaPipe: {e}")
            self.pose = None
        
        # Create GUI
        self._create_gui()
        
        # Auto-start camera
        self.root.after(1000, self.auto_start_camera)  # Start camera after 1 second
        
        self._update_loop()
    
    def _create_gui(self):
        """Create GUI with side-by-side display."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="Start Camera", command=self.start_camera)
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Camera", command=self.stop_camera, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # FPS label
        self.fps_label = ttk.Label(button_frame, text="FPS: 0", font=("Arial", 12, "bold"))
        self.fps_label.pack(side="right")
        
        # Display area - side by side
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill="both", expand=True)
        
        # Left side - Live feed
        self.live_frame = ttk.LabelFrame(display_frame, text="Live Camera Feed", padding=5)
        self.live_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.live_label = ttk.Label(self.live_frame, text="Starting camera...", 
                                   background="black", foreground="white")
        self.live_label.pack(fill="both", expand=True)
        
        # Right side - Pose animation
        self.pose_frame = ttk.LabelFrame(display_frame, text="Pose Animation", padding=5)
        self.pose_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.pose_label = ttk.Label(self.pose_frame, text="Pose animation will appear here", 
                                   background="black", foreground="white")
        self.pose_label.pack(fill="both", expand=True)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Initializing camera...", relief="sunken")
        self.status_label.pack(fill="x", pady=(10, 0))
    
    def auto_start_camera(self):
        """Auto-start camera after GUI is ready."""
        print("Auto-starting camera...")
        self.start_camera()
    
    def start_camera(self):
        """Start camera with better error handling."""
        try:
            print("Attempting to start camera...")
            self.cap = cv2.VideoCapture(0)
            
            # Test if camera is working
            ret, test_frame = self.cap.read()
            if ret and test_frame is not None:
                self.is_running = True
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                self.status_label.config(text="Camera running - showing live feed and pose animation")
                self.live_label.config(text="Camera started successfully!")
                print("Camera started successfully")
            else:
                print("Camera test failed - trying different camera index")
                self.cap.release()
                # Try camera index 1
                self.cap = cv2.VideoCapture(1)
                ret, test_frame = self.cap.read()
                if ret and test_frame is not None:
                    self.is_running = True
                    self.start_btn.config(state="disabled")
                    self.stop_btn.config(state="normal")
                    self.status_label.config(text="Camera running (index 1) - showing live feed and pose animation")
                    self.live_label.config(text="Camera started successfully!")
                    print("Camera started successfully on index 1")
                else:
                    self.status_label.config(text="No camera found - check camera connection")
                    self.live_label.config(text="No camera found!")
                    print("No camera found")
        except Exception as e:
            self.status_label.config(text=f"Camera error: {e}")
            self.live_label.config(text=f"Error: {e}")
            print(f"Camera error: {e}")
    
    def stop_camera(self):
        """Stop camera."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Camera stopped")
        self.live_label.config(text="Camera stopped")
        print("Camera stopped")
    
    def _update_loop(self):
        """Main update loop - optimized to prevent hanging."""
        if self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Resize frame for better performance
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Convert to RGB for MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Create pose animation on black background
                    pose_frame = np.zeros_like(frame, dtype=np.uint8)
                    
                    if self.pose:
                        results = self.pose.process(rgb_frame)
                        if results.pose_landmarks:
                            # Draw pose on black background
                            self.mp_drawing.draw_landmarks(
                                pose_frame,
                                results.pose_landmarks,
                                self.mp_pose.POSE_CONNECTIONS,
                                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                                    color=(0, 255, 0), thickness=3, circle_radius=4
                                ),
                                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                                    color=(255, 0, 0), thickness=3
                                )
                            )
                        else:
                            # No pose detected
                            cv2.putText(pose_frame, "No Pose Detected", (50, 240),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (150, 150, 150), 3)
                    
                    # Convert frames to PIL Images
                    live_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    live_image = Image.fromarray(live_rgb)
                    live_photo = ImageTk.PhotoImage(live_image)
                    
                    pose_rgb = cv2.cvtColor(pose_frame, cv2.COLOR_BGR2RGB)
                    pose_image = Image.fromarray(pose_rgb)
                    pose_photo = ImageTk.PhotoImage(pose_image)
                    
                    # Update labels
                    self.live_label.config(image=live_photo)
                    self.live_label.image = live_photo
                    
                    self.pose_label.config(image=pose_photo)
                    self.pose_label.image = pose_photo
                    
                    # Update FPS
                    self._update_fps()
                else:
                    print("Failed to read frame from camera")
                    self.status_label.config(text="Failed to read from camera")
            except Exception as e:
                print(f"Update error: {e}")
                self.status_label.config(text=f"Error: {e}")
        
        # Schedule next update
        self.root.after(50, self._update_loop)  # ~20 FPS
    
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
        """Run the application."""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Auto Camera + Pose Animation...")
    app = AutoCameraPoseAnimator()
    app.run()

