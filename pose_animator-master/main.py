"""
Main application for PoseAnimator - Real-Time Pose-to-Animation Transfer.
Provides both GUI and command-line interfaces for pose-to-animation transfer.
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import torch
from PIL import Image, ImageTk
import threading
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pose_detector import PoseDetector
from utils.camera_processor import CameraProcessor, RealTimeVisualizer
from models.pix2pix import PoseAnimatorModel
from evaluation.metrics import PoseTransferMetrics


class PoseAnimatorGUI:
    """Main GUI application for PoseAnimator."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PoseAnimator - Real-Time Pose-to-Animation Transfer")
        self.root.geometry("1200x800")
        
        # Application state
        self.camera_processor = None
        self.visualizer = None
        self.is_running = False
        self.model_path = None
        
        # Create GUI elements
        self._create_widgets()
        self._setup_layout()
        
        # Start GUI update loop
        self._update_gui()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Control panel
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        
        # Model selection
        self.model_label = ttk.Label(self.control_frame, text="Model Path:")
        self.model_entry = ttk.Entry(self.control_frame, width=50)
        self.model_button = ttk.Button(self.control_frame, text="Browse", command=self._browse_model)
        
        # Camera controls
        self.camera_label = ttk.Label(self.control_frame, text="Camera:")
        self.camera_combo = ttk.Combobox(self.control_frame, values=["Camera 0", "Camera 1", "Camera 2"], width=20)
        self.camera_combo.set("Camera 0")
        
        # Start/Stop buttons
        self.start_button = ttk.Button(self.control_frame, text="Start Camera", command=self._start_camera)
        self.stop_button = ttk.Button(self.control_frame, text="Stop Camera", command=self._stop_camera, state="disabled")
        
        # Settings
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding=10)
        
        # Pose detection settings
        self.confidence_label = ttk.Label(self.settings_frame, text="Detection Confidence:")
        self.confidence_scale = ttk.Scale(self.settings_frame, from_=0.1, to=1.0, orient="horizontal")
        self.confidence_scale.set(0.7)
        
        self.tracking_label = ttk.Label(self.settings_frame, text="Tracking Confidence:")
        self.tracking_scale = ttk.Scale(self.settings_frame, from_=0.1, to=1.0, orient="horizontal")
        self.tracking_scale.set(0.7)
        
        # Temporal smoothing
        self.smoothing_var = tk.BooleanVar(value=True)
        self.smoothing_check = ttk.Checkbutton(self.settings_frame, text="Enable Temporal Smoothing", 
                                             variable=self.smoothing_var)
        
        # Buffer size
        self.buffer_label = ttk.Label(self.settings_frame, text="Buffer Size:")
        self.buffer_spinbox = ttk.Spinbox(self.settings_frame, from_=3, to=10, width=10)
        self.buffer_spinbox.set(5)
        
        # Display area
        self.display_frame = ttk.LabelFrame(self.main_frame, text="Live Feed", padding=10)
        
        # Video display
        self.video_label = ttk.Label(self.display_frame, text="Camera feed will appear here", 
                                   background="black", foreground="white")
        self.video_label.pack(fill="both", expand=True)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief="sunken")
        self.fps_label = ttk.Label(self.status_frame, text="FPS: 0")
        
        # Metrics display
        self.metrics_frame = ttk.LabelFrame(self.main_frame, text="Pose Metrics", padding=10)
        self.metrics_text = tk.Text(self.metrics_frame, height=8, width=40, state="disabled")
        self.metrics_scrollbar = ttk.Scrollbar(self.metrics_frame, orient="vertical", command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=self.metrics_scrollbar.set)
    
    def _setup_layout(self):
        """Setup GUI layout."""
        # Main frame
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control panel
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Model selection
        self.model_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.model_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.model_button.grid(row=0, column=2, padx=(0, 10))
        
        # Camera controls
        self.camera_label.grid(row=0, column=3, sticky="w", padx=(10, 5))
        self.camera_combo.grid(row=0, column=4, padx=(0, 10))
        
        # Buttons
        self.start_button.grid(row=0, column=5, padx=(10, 5))
        self.stop_button.grid(row=0, column=6, padx=(5, 0))
        
        # Configure grid weights
        self.control_frame.columnconfigure(1, weight=1)
        
        # Settings
        self.settings_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Pose detection settings
        self.confidence_label.grid(row=0, column=0, sticky="w", pady=5)
        self.confidence_scale.grid(row=0, column=1, sticky="ew", pady=5)
        
        self.tracking_label.grid(row=1, column=0, sticky="w", pady=5)
        self.tracking_scale.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Temporal smoothing
        self.smoothing_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        
        # Buffer size
        self.buffer_label.grid(row=3, column=0, sticky="w", pady=5)
        self.buffer_spinbox.grid(row=3, column=1, sticky="w", pady=5)
        
        # Configure settings grid
        self.settings_frame.columnconfigure(1, weight=1)
        
        # Display area
        self.display_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        
        # Metrics
        self.metrics_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Metrics text
        self.metrics_text.grid(row=0, column=0, sticky="nsew")
        self.metrics_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure metrics grid
        self.metrics_frame.columnconfigure(0, weight=1)
        self.metrics_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.status_label.pack(side="left", fill="x", expand=True)
        self.fps_label.pack(side="right", padx=(10, 0))
        
        # Configure main grid
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    def _browse_model(self):
        """Browse for model file."""
        filename = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("PyTorch models", "*.pth"), ("All files", "*.*")]
        )
        if filename:
            self.model_entry.delete(0, tk.END)
            self.model_entry.insert(0, filename)
            self.model_path = filename
    
    def _start_camera(self):
        """Start camera processing."""
        if not self.model_path:
            messagebox.showerror("Error", "Please select a model file first.")
            return
        
        try:
            # Get camera ID
            camera_id = int(self.camera_combo.get().split()[-1])
            
            # Get settings
            detection_conf = self.confidence_scale.get()
            tracking_conf = self.tracking_scale.get()
            buffer_size = int(self.buffer_spinbox.get())
            use_smoothing = self.smoothing_var.get()
            
            # Initialize camera processor
            self.camera_processor = CameraProcessor(
                model_path=self.model_path,
                camera_id=camera_id,
                buffer_size=buffer_size,
                device='cuda' if torch.cuda.is_available() else 'cpu'
            )
            
            # Update pose detector settings
            self.camera_processor.pose_detector.pose.min_detection_confidence = detection_conf
            self.camera_processor.pose_detector.pose.min_tracking_confidence = tracking_conf
            
            # Start camera
            if self.camera_processor.start_camera():
                self.is_running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self.status_label.config(text="Camera running")
            else:
                messagebox.showerror("Error", "Failed to start camera.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error starting camera: {str(e)}")
    
    def _stop_camera(self):
        """Stop camera processing."""
        if self.camera_processor:
            self.camera_processor.stop_camera()
            self.camera_processor = None
        
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Camera stopped")
        
        # Clear video display
        self.video_label.config(image="", text="Camera feed will appear here")
    
    def _update_gui(self):
        """Update GUI elements."""
        if self.is_running and self.camera_processor:
            # Get latest frame
            frame_data = self.camera_processor.get_latest_frame()
            
            if frame_data is not None:
                # Update video display
                self._update_video_display(frame_data)
                
                # Update metrics
                self._update_metrics_display(frame_data)
                
                # Update FPS
                self.fps_label.config(text=f"FPS: {frame_data['fps']}")
        
        # Schedule next update
        self.root.after(33, self._update_gui)  # ~30 FPS
    
    def _update_video_display(self, frame_data):
        """Update video display with latest frame."""
        try:
            # Create display image
            original = frame_data['original_frame']
            pose_image = frame_data['pose_image']
            animation = frame_data['animation_image']
            
            # Resize images
            target_height = 200
            original_resized = cv2.resize(original, (int(original.shape[1] * target_height / original.shape[0]), target_height))
            pose_resized = cv2.resize(pose_image, (target_height, target_height))
            animation_resized = cv2.resize(animation, (target_height, target_height))
            
            # Create side-by-side display
            top_row = np.hstack([original_resized, pose_resized])
            bottom_row = np.hstack([animation_resized, np.zeros((target_height, target_height, 3), dtype=np.uint8)])
            
            display = np.vstack([top_row, bottom_row])
            
            # Add labels
            cv2.putText(display, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, "Pose", (220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, "Animation", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Convert to PIL Image
            display_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(display_rgb)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error updating video display: {e}")
    
    def _update_metrics_display(self, frame_data):
        """Update metrics display."""
        try:
            metrics = frame_data['pose_metrics']
            
            # Clear previous text
            self.metrics_text.config(state="normal")
            self.metrics_text.delete(1.0, tk.END)
            
            # Format metrics
            metrics_text = f"""Pose Detection Metrics:
Visible Joints: {metrics['visible_joints']}/{metrics['total_joints']}
Average Visibility: {metrics['avg_visibility']:.3f}
Pose Confidence: {metrics['pose_confidence']:.3f}

Key Joint Angles:
Left Elbow: {metrics.get('left_elbow_angle', 0):.1f}°
Right Elbow: {metrics.get('right_elbow_angle', 0):.1f}°
Left Knee: {metrics.get('left_knee_angle', 0):.1f}°
Right Knee: {metrics.get('right_knee_angle', 0):.1f}°

Performance:
FPS: {frame_data['fps']}
Buffer Size: {len(self.camera_processor.animation_buffer)}
"""
            
            self.metrics_text.insert(1.0, metrics_text)
            self.metrics_text.config(state="disabled")
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="PoseAnimator - Real-Time Pose-to-Animation Transfer")
    parser.add_argument("--mode", choices=["gui", "realtime", "train", "evaluate"], 
                       default="gui", help="Application mode")
    parser.add_argument("--model", type=str, help="Path to model file")
    parser.add_argument("--camera", type=int, default=0, help="Camera device ID")
    parser.add_argument("--data_path", type=str, help="Path to training data")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        # Launch GUI
        app = PoseAnimatorGUI()
        app.run()
    
    elif args.mode == "realtime":
        # Command-line real-time mode
        if not args.model:
            print("Error: Model path required for real-time mode")
            return
        
        # Initialize camera processor
        camera_processor = CameraProcessor(
            model_path=args.model,
            camera_id=args.camera
        )
        
        # Start camera
        if camera_processor.start_camera():
            print("Starting real-time visualization. Press 'q' to quit.")
            
            # Start visualization
            visualizer = RealTimeVisualizer()
            visualizer.start_visualization(camera_processor)
        
        # Cleanup
        camera_processor.stop_camera()
    
    elif args.mode == "train":
        # Training mode
        if not args.data_path:
            print("Error: Data path required for training mode")
            return
        
        print(f"Training mode not implemented yet. Data path: {args.data_path}")
    
    elif args.mode == "evaluate":
        # Evaluation mode
        if not args.model:
            print("Error: Model path required for evaluation mode")
            return
        
        print(f"Evaluation mode not implemented yet. Model: {args.model}")


if __name__ == "__main__":
    main()
