"""
Minimal test version to identify the crash issue.
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import mediapipe as mp

class SimpleTestGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Test")
        self.root.geometry("800x600")
        
        # Create widgets
        self.main_frame = ttk.Frame(self.root)
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        self.start_button = ttk.Button(self.control_frame, text="Start Camera", command=self._start_camera)
        self.stop_button = ttk.Button(self.control_frame, text="Stop Camera", command=self._stop_camera, state="disabled")
        
        self.display_frame = ttk.LabelFrame(self.main_frame, text="Live Feed", padding=10)
        self.video_label = ttk.Label(self.display_frame, text="Camera feed will appear here", 
                                    background="black", foreground="white")
        
        # Layout
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.display_frame.grid(row=1, column=0, sticky="nsew")
        self.video_label.pack(fill="both", expand=True)
        
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Initialize variables
        self.cap = None
        self.is_running = False
        
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
        
        # Start GUI update
        self._update_gui()
    
    def _start_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                print("Camera started successfully")
            else:
                print("Failed to open camera")
        except Exception as e:
            print(f"Error starting camera: {e}")
    
    def _stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        print("Camera stopped")
    
    def _update_gui(self):
        if self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.resize(frame, (640, 480))
                    
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detect pose
                    if self.pose:
                        results = self.pose.process(rgb_frame)
                        if results.pose_landmarks:
                            self.mp_drawing.draw_landmarks(
                                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                    
                    # Convert to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update label
                    self.video_label.config(image=photo)
                    self.video_label.image = photo
            except Exception as e:
                print(f"Error in update loop: {e}")
        
        # Schedule next update
        self.root.after(33, self._update_gui)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting simple test GUI...")
    app = SimpleTestGUI()
    app.run()

