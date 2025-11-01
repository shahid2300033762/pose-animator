"""
Demo script for PoseAnimator.
Creates sample data and demonstrates the system functionality.
"""

import os
import sys
import cv2
import numpy as np
import torch
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pose_detector import PoseDetector
from models.pix2pix import PoseAnimatorModel


class PoseAnimatorDemo:
    """Demo application for PoseAnimator."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PoseAnimator Demo")
        self.root.geometry("800x600")
        
        # Initialize pose detector
        self.pose_detector = PoseDetector()
        
        # Initialize model (dummy for demo)
        self.model = PoseAnimatorModel(use_temporal_smoothing=True)
        self.model.eval()
        
        # Demo state
        self.is_running = False
        self.cap = None
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create demo widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Control panel
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Demo Controls", padding=10)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(self.control_frame, text="Start Demo", command=self._start_demo)
        self.stop_button = ttk.Button(self.control_frame, text="Stop Demo", command=self._stop_demo, state="disabled")
        
        # Demo mode selection
        self.mode_var = tk.StringVar(value="pose_detection")
        self.mode_frame = ttk.LabelFrame(self.control_frame, text="Demo Mode", padding=5)
        
        self.pose_radio = ttk.Radiobutton(self.mode_frame, text="Pose Detection Only", 
                                        variable=self.mode_var, value="pose_detection")
        self.animation_radio = ttk.Radiobutton(self.mode_frame, text="Pose + Animation", 
                                             variable=self.mode_var, value="pose_animation")
        
        # Display area
        self.display_frame = ttk.LabelFrame(self.main_frame, text="Live Feed", padding=10)
        self.video_label = ttk.Label(self.display_frame, text="Demo will start here", 
                                   background="black", foreground="white")
        
        # Status
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief="sunken")
        self.fps_label = ttk.Label(self.status_frame, text="FPS: 0")
    
    def _setup_layout(self):
        """Setup demo layout."""
        # Main frame
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control panel
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Buttons
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        # Demo mode
        self.mode_frame.grid(row=0, column=2, padx=(20, 0), sticky="w")
        self.pose_radio.grid(row=0, column=0, sticky="w")
        self.animation_radio.grid(row=1, column=0, sticky="w")
        
        # Display area
        self.display_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.video_label.pack(fill="both", expand=True)
        
        # Status
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_label.pack(side="left", fill="x", expand=True)
        self.fps_label.pack(side="right", padx=(10, 0))
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    def _start_demo(self):
        """Start demo."""
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.status_label.config(text="Error: Could not open camera")
                return
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Demo running")
            
            # Start update loop
            self._update_demo()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def _stop_demo(self):
        """Stop demo."""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Demo stopped")
        
        # Clear display
        self.video_label.config(image="", text="Demo will start here")
    
    def _update_demo(self):
        """Update demo display."""
        if not self.is_running or not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # Resize frame
        frame = cv2.resize(frame, (640, 480))
        
        # Get demo mode
        mode = self.mode_var.get()
        
        if mode == "pose_detection":
            # Pose detection only
            display_frame = self._demo_pose_detection(frame)
        else:
            # Pose + Animation
            display_frame = self._demo_pose_animation(frame)
        
        # Convert to PIL Image
        display_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(display_rgb)
        
        # Resize for display
        pil_image = pil_image.resize((600, 400), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Update display
        self.video_label.config(image=photo, text="")
        self.video_label.image = photo  # Keep reference
        
        # Schedule next update
        self.root.after(33, self._update_demo)  # ~30 FPS
    
    def _demo_pose_detection(self, frame):
        """Demo pose detection."""
        # Detect pose
        pose_data = self.pose_detector.detect_pose(frame)
        
        if pose_data is not None:
            # Draw pose landmarks
            frame = self._draw_pose_landmarks(frame, pose_data)
            
            # Add pose metrics
            metrics = self.pose_detector.calculate_pose_metrics(pose_data)
            self._draw_metrics(frame, metrics)
        else:
            # No pose detected
            cv2.putText(frame, "No pose detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame
    
    def _demo_pose_animation(self, frame):
        """Demo pose to animation transfer."""
        # Detect pose
        pose_data = self.pose_detector.detect_pose(frame)
        
        if pose_data is not None:
            # Create pose image
            pose_image = self.pose_detector.create_pose_image(pose_data, (256, 256))
            
            # Generate animation (dummy for demo)
            animation = self._generate_dummy_animation(pose_image)
            
            # Create side-by-side display
            pose_resized = cv2.resize(pose_image, (200, 200))
            animation_resized = cv2.resize(animation, (200, 200))
            
            # Place side by side
            display = np.hstack([frame, pose_resized, animation_resized])
            
            # Add labels
            cv2.putText(display, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, "Pose", (650, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, "Animation", (860, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return display
        else:
            # No pose detected
            cv2.putText(frame, "No pose detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame
    
    def _draw_pose_landmarks(self, frame, pose_data):
        """Draw pose landmarks on frame."""
        landmarks = np.array(pose_data['landmarks'])
        visibility = np.array(pose_data['visibility'])
        
        # Convert normalized coordinates to pixel coordinates
        h, w = frame.shape[:2]
        pixel_landmarks = landmarks.copy()
        pixel_landmarks[:, 0] *= w
        pixel_landmarks[:, 1] *= h
        
        # Draw connections
        connections = [
            # Face
            (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye
            (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye
            (9, 10),  # Mouth
            # Torso
            (11, 12), (11, 23), (12, 24), (23, 24),  # Shoulders and hips
            # Left arm
            (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  # Left arm
            # Right arm
            (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  # Right arm
            # Left leg
            (23, 25), (25, 27), (27, 29), (27, 31),  # Left leg
            # Right leg
            (24, 26), (26, 28), (28, 30), (28, 32),  # Right leg
        ]
        
        for connection in connections:
            start_idx, end_idx = connection
            if (visibility[start_idx] > 0.5 and visibility[end_idx] > 0.5):
                start_point = (int(pixel_landmarks[start_idx, 0]), 
                             int(pixel_landmarks[start_idx, 1]))
                end_point = (int(pixel_landmarks[end_idx, 0]), 
                           int(pixel_landmarks[end_idx, 1]))
                
                cv2.line(frame, start_point, end_point, (0, 255, 0), 2)
        
        # Draw joints
        for i, (landmark, vis) in enumerate(zip(pixel_landmarks, visibility)):
            if vis > 0.5:
                center = (int(landmark[0]), int(landmark[1]))
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
        
        return frame
    
    def _draw_metrics(self, frame, metrics):
        """Draw pose metrics on frame."""
        y_offset = 60
        cv2.putText(frame, f"Visible Joints: {metrics['visible_joints']}/{metrics['total_joints']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_offset += 30
        cv2.putText(frame, f"Avg Visibility: {metrics['avg_visibility']:.3f}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_offset += 30
        cv2.putText(frame, f"Pose Confidence: {metrics['pose_confidence']:.3f}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def _generate_dummy_animation(self, pose_image):
        """Generate dummy animation for demo."""
        # Simple transformation for demo
        animation = cv2.GaussianBlur(pose_image, (15, 15), 0)
        animation = cv2.addWeighted(pose_image, 0.7, animation, 0.3, 0)
        
        # Add color variation
        animation[:, :, 0] = np.clip(animation[:, :, 0] * 1.2, 0, 255)
        animation[:, :, 2] = np.clip(animation[:, :, 2] * 0.8, 0, 255)
        
        return animation
    
    def run(self):
        """Run the demo."""
        self.root.mainloop()


def main():
    """Main demo function."""
    print("Starting PoseAnimator Demo...")
    print("This demo shows pose detection and basic animation generation.")
    print("Note: This is a demonstration with dummy animation generation.")
    print("For full functionality, train a model using train.py")
    
    demo = PoseAnimatorDemo()
    demo.run()


if __name__ == "__main__":
    main()
