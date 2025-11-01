"""
Simple working version of PoseAnimator that avoids the complex issues.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import torch
import torch.nn as nn
import mediapipe as mp
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import camera helper
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils"))
try:
    from camera_helper import initialize_camera, set_camera_properties
except ImportError:
    print("Warning: Could not import camera_helper. Using fallback camera initialization.")

# Pose Detection Class
class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = None
        self.mp_drawing = mp.solutions.drawing_utils
        self._initialize_pose()
        
    def _initialize_pose(self):
        """Initialize pose detection."""
        try:
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception as e:
            print(f"Error initializing pose detector: {e}")
            self.pose = None
        
    def detect_pose(self, frame):
        """Detect pose landmarks in the frame (single person)."""
        if self.pose is None:
            return frame.copy(), None
            
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            pose_image = frame.copy()
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    pose_image, 
                    results.pose_landmarks, 
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
            
            return pose_image, results.pose_landmarks
        except Exception as e:
            print(f"Error in pose detection: {e}")
            return frame.copy(), None
    
    def detect_multiple_poses(self, frame):
        """Detect multiple poses in the frame - simple and fast version."""
        if self.pose is None:
            return frame.copy(), []
            
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            all_poses = []
            
            # Simply run pose detection 3 times with slight offsets to catch different people
            # This is simple and won't hang
            offsets = [0, -50, 50]  # Center, left shift, right shift
            
            for offset in offsets:
                if offset == 0:
                    # Process full frame
                    shifted = rgb_frame
                else:
                    # Shift frame
                    height, width = rgb_frame.shape[:2]
                    shifted = np.zeros_like(rgb_frame)
                    if offset > 0:
                        shifted[:, :width-offset] = rgb_frame[:, offset:]
                    else:
                        shifted[:, abs(offset):] = rgb_frame[:, :width-abs(offset)]
                
                results = self.pose.process(shifted)
                
                if results.pose_landmarks:
                    # Check if this pose is different from already detected ones
                    is_new = True
                    for existing in all_poses:
                        # Compare first few landmarks
                        diff = 0
                        for i in range(min(5, len(results.pose_landmarks.landmark), len(existing.landmark))):
                            diff += abs(results.pose_landmarks.landmark[i].x - existing.landmark[i].x)
                            diff += abs(results.pose_landmarks.landmark[i].y - existing.landmark[i].y)
                        
                        if diff < 0.5:
                            is_new = False
                            break
                    
                    if is_new:
                        all_poses.append(results.pose_landmarks)
                        if len(all_poses) >= 3:  # Max 3 people
                            break
            
            # Draw all detected poses
            pose_image = frame.copy()
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            
            for i, pose_landmarks in enumerate(all_poses):
                color = colors[i % len(colors)]
                self.mp_drawing.draw_landmarks(
                    pose_image,
                    pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=color, thickness=2)
                )
            
            return pose_image, all_poses if len(all_poses) > 0 else None
            
        except Exception as e:
            import traceback
            print(f"Error in multi-pose detection: {e}")
            traceback.print_exc()
            return frame.copy(), None
    
    def close(self):
        """Close the pose detector."""
        try:
            if self.pose is not None:
                self.pose.close()
                self.pose = None
        except Exception as e:
            print(f"Error closing pose detector: {e}")

# Simple pose-to-animation model
class SimplePoseAnimator(nn.Module):
    def __init__(self):
        super().__init__()
        self.generator = nn.Sequential(
            nn.Conv2d(3, 32, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 3, 2, 1, 1),
            nn.ReLU(),
            nn.Conv2d(32, 3, 3, 1, 1),
            nn.Tanh()
        )
    
    def forward(self, x):
        return self.generator(x)

class SimplePoseAnimatorGUI:
    """Simple GUI for PoseAnimator that works without complex dependencies."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PoseAnimator - Simple Working Version")
        self.root.geometry("1400x900")
        
        # Center the window on screen
        self.root.update_idletasks()
        window_width = 1500
        window_height = 950
        x = (self.root.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Application state
        self.cap = None
        self.is_running = False
        self.model = SimplePoseAnimator()
        self.model.eval()
        
        # Pose detection
        self.pose_detector = PoseDetector()
        
        # FPS tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Auto-capture settings
        self.auto_capture_enabled = False
        self.capture_interval = 10  # seconds
        self.last_capture_time = 0
        self.capture_count = 0
        self.captured_frames = []
        
        self._create_widgets()
        self._setup_layout()
        
        # Start GUI update loop
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
                                                  variable=self.auto_capture_var, 
                                                  command=self._toggle_auto_capture)
        self.capture_status_label = ttk.Label(self.control_frame, text="Captures: 0", font=("Arial", 12, "bold"))
        self.countdown_label = ttk.Label(self.control_frame, text="Next capture in: --", font=("Arial", 12))
        
        # Display area
        self.display_frame = ttk.LabelFrame(self.main_frame, text="Live Feed", padding=10)
        self.video_label = ttk.Label(self.display_frame, text="Camera feed will appear here", 
                                    background="black", foreground="white")
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief="sunken", font=("Arial", 11))
        self.fps_label = ttk.Label(self.status_frame, text="FPS: 0", font=("Arial", 11, "bold"))
        
        # Info text
        self.info_text = tk.Text(self.main_frame, height=10, width=50, state="disabled")
        self.info_text.insert(1.0, """PoseAnimator - Enhanced Version

Features:
• Real-time camera feed with pose detection
• Live pose animation generation  
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
• Right panel shows your pose animation!""")
    
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
        self.info_text.config(height=25)
        
        # Status frame
        self.status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.status_label.pack(side="left", fill="x", expand=True)
        self.fps_label.pack(side="right", padx=(10, 0))
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
    
    def _toggle_auto_capture(self):
        """Toggle auto-capture functionality."""
        self.auto_capture_enabled = self.auto_capture_var.get()
        if self.auto_capture_enabled and self.is_running:
            self.last_capture_time = time.time()
            self.capture_count = 0
            self.captured_frames = []
            self.capture_status_label.config(text="Captures: 0")
    
    def _start_camera(self):
        """Start camera processing."""
        try:
            # Get camera ID
            preferred_camera_id = int(self.camera_combo.get().split()[-1])
            
            # Use robust camera initialization
            try:
                # Try to use our camera helper for robust initialization
                self.cap, working_index = initialize_camera(preferred_index=preferred_camera_id, 
                                                           max_retries=3, 
                                                           max_indices=5)
                if self.cap is None:
                    raise Exception("Could not initialize any camera")
                
                # Set camera properties
                set_camera_properties(self.cap, width=640, height=480, fps=30)
                
                # Update camera selection if a different index worked
                if working_index != preferred_camera_id:
                    self.camera_combo.set(f"Camera {working_index}")
                    
            except (NameError, ImportError):
                # Fallback to standard initialization if helper not available
                print("Using fallback camera initialization")
                self.cap = cv2.VideoCapture(preferred_camera_id)
                
                # Try alternative camera indices if the preferred one fails
                if not self.cap.isOpened():
                    for alt_index in range(3):  # Try indices 0, 1, 2
                        if alt_index == preferred_camera_id:
                            continue  # Skip the one we already tried
                        print(f"Trying alternative camera index: {alt_index}")
                        self.cap = cv2.VideoCapture(alt_index)
                        if self.cap.isOpened():
                            # Update camera selection
                            self.camera_combo.set(f"Camera {alt_index}")
                            break
            
            # Final check if camera is open
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open any camera. Please check your camera connections.")
                return
            
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Camera running")
            
            # Initialize auto-capture if enabled
            if self.auto_capture_enabled:
                self.last_capture_time = time.time()
                self.capture_count = 0
                self.captured_frames = []
                self.capture_status_label.config(text="Captures: 0")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error starting camera: {str(e)}")
    
    def _stop_camera(self):
        """Stop camera processing."""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Close pose detector
        if hasattr(self, 'pose_detector'):
            self.pose_detector.close()
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Camera stopped")
        
        # Clear video display
        self.video_label.config(image="", text="Camera feed will appear here")
    
    def _update_gui(self):
        """Update GUI elements."""
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Resize frame to larger size
                frame = cv2.resize(frame, (640, 480))
                
                # Detect pose landmarks (single person)
                try:
                    pose_image, pose_landmarks = self.pose_detector.detect_pose(frame)
                except Exception as e:
                    print(f"Pose detection error: {e}")
                    pose_image = frame.copy()
                    pose_landmarks = None
                
                # Generate pose animation
                animation_frame = self._create_pose_animation(frame, pose_landmarks)
                
                # Create side-by-side display
                display_frame = np.hstack([frame, animation_frame])
                
                # Convert to RGB
                display_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(display_rgb)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update label
                self.video_label.config(image=photo, text="")
                self.video_label.image = photo  # Keep reference
                
                # Auto-capture logic
                if self.auto_capture_enabled:
                    current_time = time.time()
                    time_since_last_capture = current_time - self.last_capture_time
                    
                    # Update countdown
                    remaining_time = max(0, self.capture_interval - time_since_last_capture)
                    self.countdown_label.config(text=f"Next capture in: {remaining_time:.1f}s")
                    
                    # Check if it's time to capture
                    if time_since_last_capture >= self.capture_interval:
                        self._capture_frame(frame, animation_frame)
                        self.last_capture_time = current_time
                        self.capture_count += 1
                        self.capture_status_label.config(text=f"Captures: {self.capture_count}")
                else:
                    self.countdown_label.config(text="Next capture in: --")
                
                # Update FPS
                self._update_fps()
        
        # Schedule next update
        self.root.after(33, self._update_gui)  # ~30 FPS
    
    def _create_pose_animation(self, frame, pose_landmarks):
        """Create pose animation from detected landmarks for all people in frame."""
        # Create a black background for the animation
        animation = np.zeros_like(frame, dtype=np.uint8)
        # Always determine frame dimensions (used in both branches)
        height, width = frame.shape[:2]
        
        if pose_landmarks:
            # Create a stylized pose animation
            
            # Draw complete pose skeleton with enhanced styling
            self._draw_pose_skeleton(animation, pose_landmarks, width, height)
            
            # Add artistic effects and enhancements
            animation = self._add_artistic_effects(animation, frame)
        else:
            # If no pose detected, show a message
            cv2.putText(animation, "No Pose Detected", (50, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (150, 150, 150), 3)
            cv2.putText(animation, "Position yourself in camera view", (20, height//2 + 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 100, 100), 2)
        
        return animation
    
    def _create_pose_animation_multiple(self, frame, all_poses):
        """Create pose animation from multiple detected poses for all people in frame."""
        # Create a black background for the animation
        animation = np.zeros_like(frame, dtype=np.uint8)
        height, width = frame.shape[:2]
        
        if all_poses and len(all_poses) > 0:
            # Different colors for different people
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), 
                     (0, 255, 255), (128, 255, 0), (255, 128, 0), (0, 128, 255), (255, 0, 128)]
            
            for idx, pose_landmarks in enumerate(all_poses):
                color = colors[idx % len(colors)]
                # Draw complete pose skeleton with person-specific color
                self._draw_pose_skeleton_with_color(animation, pose_landmarks, width, height, color)
            
            # Add artistic effects and enhancements
            animation = self._add_artistic_effects(animation, frame)
            
            # Show number of detected people
            cv2.putText(animation, f"{len(all_poses)} Person(s) Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            # If no pose detected, show a message
            cv2.putText(animation, "No Pose Detected", (50, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (150, 150, 150), 3)
            cv2.putText(animation, "Position yourself in camera view", (20, height//2 + 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 100, 100), 2)
        
        return animation
    
    def _draw_pose_skeleton(self, animation, pose_landmarks, width, height):
        """Draw complete pose skeleton with enhanced styling for all detected bodies."""
        # MediaPipe POSE_CONNECTIONS - all body connections
        connections = [
            # Face and head
            (0, 1), (0, 2), (2, 3), (3, 7),
            # Upper body
            (11, 12), (11, 13), (12, 14), (13, 15), (14, 16),
            # Arms
            (11, 23), (12, 24), (23, 24),
            (13, 15), (14, 16), (15, 17), (16, 18), (17, 19), (18, 20), (19, 21), (20, 22),
            # Torso
            (23, 24), (23, 25), (24, 26),
            # Legs
            (23, 25), (24, 26), (25, 27), (26, 28),
            (27, 29), (28, 30), (29, 31), (30, 32), (31, 33), (32, 34)
        ]
        
        # Draw all connections with thicker lines
        for connection in connections:
            start_idx, end_idx = connection
            if (start_idx < len(pose_landmarks.landmark) and 
                end_idx < len(pose_landmarks.landmark)):
                
                start_point = pose_landmarks.landmark[start_idx]
                end_point = pose_landmarks.landmark[end_idx]
                
                # Only draw if both points are visible
                if start_point.visibility > 0.5 and end_point.visibility > 0.5:
                    start_x = int(start_point.x * width)
                    start_y = int(start_point.y * height)
                    end_x = int(end_point.x * width)
                    end_y = int(end_point.y * height)
                    
                    # Draw line with bright color
                    cv2.line(animation, (start_x, start_y), (end_x, end_y), 
                            (0, 255, 255), 5)
        
        # Draw all key points with colors based on body parts
        for i, landmark in enumerate(pose_landmarks.landmark):
            # Only draw if point is visible
            if landmark.visibility < 0.5:
                continue
                
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # Different colors for different body parts - larger points
            if i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:  # Face
                color = (255, 192, 203)  # Pink
                radius = 8
            elif i in [11, 12]:  # Shoulders
                color = (255, 0, 0)  # Red
                radius = 10
            elif i in [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:  # Arms and hands
                color = (0, 255, 0)  # Green
                radius = 8
            elif i in [23, 24]:  # Hips
                color = (0, 0, 255)  # Blue
                radius = 10
            elif i in [25, 26, 27, 28, 29, 30, 31, 32, 33, 34]:  # Legs and feet
                color = (255, 255, 0)  # Yellow
                radius = 8
            else:
                color = (255, 255, 255)  # White
                radius = 6
            
            # Draw filled circle with border
            cv2.circle(animation, (x, y), radius, color, -1)
            cv2.circle(animation, (x, y), radius + 2, (255, 255, 255), 3)
    
    def _draw_pose_skeleton_with_color(self, animation, pose_landmarks, width, height, person_color):
        """Draw complete pose skeleton with person-specific color."""
        # MediaPipe POSE_CONNECTIONS - all body connections
        connections = [
            # Face and head
            (0, 1), (0, 2), (2, 3), (3, 7),
            # Upper body
            (11, 12), (11, 13), (12, 14), (13, 15), (14, 16),
            # Arms
            (11, 23), (12, 24), (23, 24),
            (13, 15), (14, 16), (15, 17), (16, 18), (17, 19), (18, 20), (19, 21), (20, 22),
            # Torso
            (23, 24), (23, 25), (24, 26),
            # Legs
            (23, 25), (24, 26), (25, 27), (26, 28),
            (27, 29), (28, 30), (29, 31), (30, 32), (31, 33), (32, 34)
        ]
        
        # Draw all connections with thicker lines using person color
        for connection in connections:
            start_idx, end_idx = connection
            if (start_idx < len(pose_landmarks.landmark) and 
                end_idx < len(pose_landmarks.landmark)):
                
                start_point = pose_landmarks.landmark[start_idx]
                end_point = pose_landmarks.landmark[end_idx]
                
                # Only draw if both points are visible
                if start_point.visibility > 0.5 and end_point.visibility > 0.5:
                    start_x = int(start_point.x * width)
                    start_y = int(start_point.y * height)
                    end_x = int(end_point.x * width)
                    end_y = int(end_point.y * height)
                    
                    # Draw line with person-specific color
                    cv2.line(animation, (start_x, start_y), (end_x, end_y), 
                            person_color, 5)
        
        # Draw all key points with person color
        for i, landmark in enumerate(pose_landmarks.landmark):
            # Only draw if point is visible
            if landmark.visibility < 0.5:
                continue
                
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # Use person color for all points
            color = person_color
            radius = 8
            
            # Draw filled circle with border
            cv2.circle(animation, (x, y), radius, color, -1)
            cv2.circle(animation, (x, y), radius + 2, (255, 255, 255), 3)
    
    def _add_artistic_effects(self, animation, original_frame):
        """Add artistic effects to make pose animation more visible."""
        # Create a subtle grid background
        background = np.zeros_like(animation)
        
        # Add grid pattern
        height, width = animation.shape[:2]
        grid_spacing = 40
        for i in range(0, width, grid_spacing):
            cv2.line(background, (i, 0), (i, height), (15, 15, 15), 1)
        for i in range(0, height, grid_spacing):
            cv2.line(background, (0, i), (width, i), (15, 15, 15), 1)
        
        # Blend animation with dark background
        animation = cv2.addWeighted(animation, 0.9, background, 0.1, 0)
        
        # Add a subtle glow effect
        kernel = np.ones((7, 7), np.float32) / 49
        glow = cv2.filter2D(animation, -1, kernel)
        animation = cv2.addWeighted(animation, 0.75, glow, 0.25, 0)
        
        # Increase overall brightness slightly
        animation = cv2.convertScaleAbs(animation, alpha=1.2, beta=10)
        
        return animation
    
    def _capture_frame(self, original_frame, animation_frame):
        """Capture and save the current frame."""
        try:
            # Create timestamp for filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Create captures directory if it doesn't exist
            import os
            captures_dir = "captures"
            if not os.path.exists(captures_dir):
                os.makedirs(captures_dir)
            
            # Save original frame
            original_filename = f"{captures_dir}/original_{timestamp}_{self.capture_count:03d}.jpg"
            cv2.imwrite(original_filename, original_frame)
            
            # Save animation frame
            animation_filename = f"{captures_dir}/animation_{timestamp}_{self.capture_count:03d}.jpg"
            cv2.imwrite(animation_filename, animation_frame)
            
            # Store frame data
            frame_data = {
                'timestamp': timestamp,
                'count': self.capture_count,
                'original_path': original_filename,
                'animation_path': animation_filename
            }
            self.captured_frames.append(frame_data)
            
            # Update status
            self.status_label.config(text=f"Captured frame {self.capture_count}")
            
            print(f"Captured frame {self.capture_count}: {timestamp}")
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            self.status_label.config(text=f"Capture error: {str(e)}")
    
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
    
    app = SimplePoseAnimatorGUI()
    app.run()


if __name__ == "__main__":
    main()
