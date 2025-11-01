"""
Minimal pose animation - guaranteed to work.
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import mediapipe as mp
import time

class MinimalPoseAnimator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pose Animation")
        self.root.geometry("800x600")
        
        # Variables
        self.cap = None
        self.is_running = False
        
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
        self._update_loop()
    
    def _create_gui(self):
        """Create simple GUI."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="Start Camera", command=self.start_camera)
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Camera", command=self.stop_camera, state="disabled")
        self.stop_btn.pack(side="left")
        
        # Display area
        self.display_label = ttk.Label(main_frame, text="Pose animation will appear here", 
                                     background="black", foreground="white")
        self.display_label.pack(fill="both", expand=True)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready", relief="sunken")
        self.status_label.pack(fill="x", pady=(10, 0))
    
    def start_camera(self):
        """Start camera."""
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_running = True
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                self.status_label.config(text="Camera running")
                print("Camera started")
            else:
                self.status_label.config(text="Failed to open camera")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            print(f"Error: {e}")
    
    def stop_camera(self):
        """Stop camera."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Camera stopped")
        print("Camera stopped")
    
    def _update_loop(self):
        """Main update loop."""
        if self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret:
                    # Resize frame
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Convert to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Create pose animation
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
                    
                    # Convert to PIL and display
                    pose_rgb = cv2.cvtColor(pose_frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(pose_rgb)
                    photo = ImageTk.PhotoImage(image)
                    
                    self.display_label.config(image=photo)
                    self.display_label.image = photo
                    
            except Exception as e:
                print(f"Update error: {e}")
                self.status_label.config(text=f"Error: {e}")
        
        # Schedule next update
        self.root.after(33, self._update_loop)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Minimal Pose Animator...")
    app = MinimalPoseAnimator()
    app.run()

