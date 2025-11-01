"""
Real-time camera capture and processing for pose-to-animation transfer.
Handles camera input, pose detection, and animation generation in real-time.
"""

import cv2
import numpy as np
import torch
import time
from typing import Optional, Tuple, Dict, List
from collections import deque
import threading
from queue import Queue

from .pose_detector import PoseDetector
from models.pix2pix import PoseAnimatorModel


class CameraProcessor:
    """Real-time camera processing for pose-to-animation transfer."""
    
    def __init__(self, 
                 model_path: str,
                 camera_id: int = 0,
                 input_size: Tuple[int, int] = (256, 256),
                 output_size: Tuple[int, int] = (512, 512),
                 buffer_size: int = 5,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        """
        Initialize camera processor.
        
        Args:
            model_path: Path to trained PoseAnimator model
            camera_id: Camera device ID
            input_size: Input image size for pose detection
            output_size: Output animation size
            buffer_size: Size of temporal smoothing buffer
            device: Device to run inference on
        """
        self.camera_id = camera_id
        self.input_size = input_size
        self.output_size = output_size
        self.buffer_size = buffer_size
        self.device = device
        
        # Initialize pose detector
        self.pose_detector = PoseDetector(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Load model
        self.model = self._load_model(model_path)
        self.model.eval()
        
        # Initialize camera
        self.cap = None
        self.is_running = False
        
        # Temporal smoothing buffer
        self.pose_buffer = deque(maxlen=buffer_size)
        self.animation_buffer = deque(maxlen=buffer_size)
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Threading for real-time processing
        self.processing_queue = Queue(maxsize=2)
        self.output_queue = Queue(maxsize=2)
        self.processing_thread = None
        
    def _load_model(self, model_path: str) -> PoseAnimatorModel:
        """Load the trained PoseAnimator model."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            model = PoseAnimatorModel(use_temporal_smoothing=True)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            # Return a dummy model for testing
            return PoseAnimatorModel(use_temporal_smoothing=True)
    
    def start_camera(self) -> bool:
        """Start camera capture."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_running = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._processing_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            print("Camera started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture."""
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
        
        self.pose_detector.close()
        print("Camera stopped")
    
    def _processing_loop(self):
        """Main processing loop running in separate thread."""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Resize frame for processing
            frame_resized = cv2.resize(frame, self.input_size)
            
            # Detect pose
            pose_data = self.pose_detector.detect_pose(frame_resized)
            
            if pose_data is not None:
                # Process pose and generate animation
                processed_frame = self._process_frame(frame_resized, pose_data)
                
                # Add to output queue
                if not self.output_queue.full():
                    self.output_queue.put(processed_frame)
            
            # Update FPS counter
            self._update_fps()
    
    def _process_frame(self, frame: np.ndarray, pose_data: Dict) -> Dict:
        """Process a single frame and generate animation."""
        # Normalize pose
        normalized_pose = self.pose_detector.normalize_pose(pose_data, self.input_size)
        
        # Create pose image
        pose_image = self.pose_detector.create_pose_image(pose_data, self.input_size)
        
        # Convert to tensor
        pose_tensor = self._image_to_tensor(pose_image)
        
        # Generate animation
        with torch.no_grad():
            animation_tensor = self.model.generator(pose_tensor)
        
        # Apply temporal smoothing if buffer has enough frames
        if len(self.animation_buffer) >= self.buffer_size:
            animation_sequence = torch.stack(list(self.animation_buffer))
            smoothed_animation = self.model.apply_temporal_smoothing(animation_sequence)
        else:
            smoothed_animation = animation_tensor
        
        # Add to buffer
        self.animation_buffer.append(animation_tensor)
        
        # Convert back to image
        animation_image = self._tensor_to_image(smoothed_animation)
        
        # Resize to output size
        animation_image = cv2.resize(animation_image, self.output_size)
        
        # Calculate pose metrics
        pose_metrics = self.pose_detector.calculate_pose_metrics(pose_data)
        
        return {
            'original_frame': frame,
            'pose_image': pose_image,
            'animation_image': animation_image,
            'pose_data': pose_data,
            'pose_metrics': pose_metrics,
            'fps': self.current_fps
        }
    
    def _image_to_tensor(self, image: np.ndarray) -> torch.Tensor:
        """Convert image to PyTorch tensor."""
        # Normalize to [0, 1]
        image_norm = image.astype(np.float32) / 255.0
        
        # Convert to tensor and add batch dimension
        tensor = torch.from_numpy(image_norm).permute(2, 0, 1).unsqueeze(0)
        
        return tensor.to(self.device)
    
    def _tensor_to_image(self, tensor: torch.Tensor) -> np.ndarray:
        """Convert PyTorch tensor to image."""
        # Remove batch dimension and move to CPU
        tensor = tensor.squeeze(0).cpu()
        
        # Convert to numpy and denormalize
        image = tensor.permute(1, 2, 0).numpy()
        image = (image * 255.0).astype(np.uint8)
        
        return image
    
    def _update_fps(self):
        """Update FPS counter."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def get_latest_frame(self) -> Optional[Dict]:
        """Get the latest processed frame."""
        if not self.output_queue.empty():
            return self.output_queue.get()
        return None
    
    def get_pose_sequence(self, length: int = 10) -> List[Dict]:
        """Get a sequence of recent poses for temporal analysis."""
        return list(self.pose_buffer)[-length:]
    
    def add_noise_analysis(self, noise_level: float = 0.1) -> Dict:
        """Add noise to current pose for noise analysis."""
        if self.pose_buffer:
            latest_pose = self.pose_buffer[-1]
            
            # Add noise to pose landmarks
            noisy_pose = latest_pose.copy()
            noise = np.random.normal(0, noise_level, latest_pose['landmarks'].shape)
            noisy_pose['landmarks'] = latest_pose['landmarks'] + noise
            
            # Generate animation with noisy pose
            pose_image = self.pose_detector.create_pose_image(noisy_pose, self.input_size)
            pose_tensor = self._image_to_tensor(pose_image)
            
            with torch.no_grad():
                noisy_animation = self.model.generator(pose_tensor)
            
            animation_image = self._tensor_to_image(noisy_animation)
            animation_image = cv2.resize(animation_image, self.output_size)
            
            return {
                'noisy_pose': noisy_pose,
                'noisy_animation': animation_image,
                'noise_level': noise_level
            }
        
        return {}


class RealTimeVisualizer:
    """Real-time visualization for pose-to-animation transfer."""
    
    def __init__(self, window_name: str = "PoseAnimator"):
        self.window_name = window_name
        self.is_running = False
        
    def start_visualization(self, camera_processor: CameraProcessor):
        """Start real-time visualization."""
        self.is_running = True
        cv2.namedWindow(self.window_name, cv2.WINDOW_RESIZABLE)
        
        print("Starting visualization. Press 'q' to quit, 's' to save frame, 'n' for noise analysis")
        
        while self.is_running:
            # Get latest processed frame
            frame_data = camera_processor.get_latest_frame()
            
            if frame_data is not None:
                # Create display image
                display_image = self._create_display_image(frame_data)
                
                # Show image
                cv2.imshow(self.window_name, display_image)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.is_running = False
                elif key == ord('s'):
                    self._save_frame(frame_data)
                elif key == ord('n'):
                    self._show_noise_analysis(camera_processor)
            
            # Check if window was closed
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                self.is_running = False
        
        cv2.destroyAllWindows()
    
    def _create_display_image(self, frame_data: Dict) -> np.ndarray:
        """Create display image with pose and animation side by side."""
        original = frame_data['original_frame']
        pose_image = frame_data['pose_image']
        animation = frame_data['animation_image']
        
        # Resize images to same height
        target_height = 300
        original_resized = cv2.resize(original, (int(original.shape[1] * target_height / original.shape[0]), target_height))
        pose_resized = cv2.resize(pose_image, (target_height, target_height))
        animation_resized = cv2.resize(animation, (target_height, target_height))
        
        # Create side-by-side display
        top_row = np.hstack([original_resized, pose_resized])
        bottom_row = np.hstack([animation_resized, np.zeros((target_height, target_height, 3), dtype=np.uint8)])
        
        display = np.vstack([top_row, bottom_row])
        
        # Add FPS and metrics text
        fps_text = f"FPS: {frame_data['fps']}"
        cv2.putText(display, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add pose metrics
        metrics = frame_data['pose_metrics']
        metrics_text = f"Visible Joints: {metrics['visible_joints']}/{metrics['total_joints']}"
        cv2.putText(display, metrics_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return display
    
    def _save_frame(self, frame_data: Dict):
        """Save current frame and animation."""
        timestamp = int(time.time())
        
        # Save original frame
        cv2.imwrite(f"frame_{timestamp}.jpg", frame_data['original_frame'])
        
        # Save pose image
        cv2.imwrite(f"pose_{timestamp}.jpg", frame_data['pose_image'])
        
        # Save animation
        cv2.imwrite(f"animation_{timestamp}.jpg", frame_data['animation_image'])
        
        print(f"Saved frame {timestamp}")
    
    def _show_noise_analysis(self, camera_processor: CameraProcessor):
        """Show noise analysis window."""
        noise_data = camera_processor.add_noise_analysis(0.2)
        
        if noise_data:
            # Create noise analysis display
            original_pose = camera_processor.pose_detector.create_pose_image(
                camera_processor.pose_buffer[-1], camera_processor.input_size
            )
            noisy_pose = camera_processor.pose_detector.create_pose_image(
                noise_data['noisy_pose'], camera_processor.input_size
            )
            
            # Resize for display
            original_resized = cv2.resize(original_pose, (200, 200))
            noisy_resized = cv2.resize(noisy_pose, (200, 200))
            animation_resized = cv2.resize(noise_data['noisy_animation'], (200, 200))
            
            # Create comparison display
            comparison = np.hstack([original_resized, noisy_resized, animation_resized])
            
            # Add labels
            cv2.putText(comparison, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(comparison, "Noisy", (220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(comparison, "Animation", (430, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Noise Analysis", comparison)
            cv2.waitKey(3000)  # Show for 3 seconds
            cv2.destroyWindow("Noise Analysis")
