"""
Pose detection module using MediaPipe for real-time pose tracking.
Handles pose landmark extraction and normalization for animation transfer.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional, Dict
import torch


class PoseDetector:
    """Real-time pose detection and landmark extraction using MediaPipe."""
    
    def __init__(self, 
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 model_complexity: int = 1):
        """
        Initialize pose detector.
        
        Args:
            min_detection_confidence: Minimum confidence for pose detection
            min_tracking_confidence: Minimum confidence for pose tracking
            model_complexity: MediaPipe model complexity (0, 1, or 2)
        """
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Key joint indices for animation transfer
        self.key_joints = [
            'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
            'right_eye_inner', 'right_eye', 'right_eye_outer',
            'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
            'left_index', 'right_index', 'left_thumb', 'right_thumb',
            'left_hip', 'right_hip', 'left_knee', 'right_knee',
            'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
            'left_foot_index', 'right_foot_index'
        ]
        
        # Pose landmark connections for skeleton drawing
        self.connections = [
            # Face
            (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye
            (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye
            (9, 10),  # Mouth
            # Torso
            (11, 12), (11, 23), (12, 24), (23, 24),  # Shoulders and hips
            # Left arm
            (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  # Left arm
            (17, 19), (19, 21),  # Left hand
            # Right arm
            (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  # Right arm
            (18, 20), (20, 22),  # Right hand
            # Left leg
            (23, 25), (25, 27), (27, 29), (27, 31),  # Left leg
            (29, 31), (31, 33),  # Left foot
            # Right leg
            (24, 26), (26, 28), (28, 30), (28, 32),  # Right leg
            (30, 32), (32, 34),  # Right foot
        ]
    
    def detect_pose(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect pose landmarks in the given image (for single person).
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary containing pose landmarks and confidence scores
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Extract key joint positions and visibility
            pose_data = {
                'landmarks': [],
                'visibility': [],
                'world_landmarks': [],
                'pose_confidence': 1.0  # Default confidence
            }
            
            for landmark in landmarks:
                pose_data['landmarks'].append([landmark.x, landmark.y, landmark.z])
                pose_data['visibility'].append(landmark.visibility)
            
            # Extract world landmarks if available
            if results.pose_world_landmarks:
                for landmark in results.pose_world_landmarks.landmark:
                    pose_data['world_landmarks'].append([landmark.x, landmark.y, landmark.z])
            
            return pose_data
        
        return None
    
    def detect_multiple_poses(self, image: np.ndarray) -> List[Dict]:
        """
        Detect multiple poses in the given image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of dictionaries, each containing pose landmarks and confidence scores
        """
        all_poses = []
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = rgb_image.shape[:2]
        
        # Create a working copy for masking
        working_image = rgb_image.copy()
        mask = np.ones((height, width), dtype=np.uint8) * 255
        
        max_detections = 10  # Limit to prevent infinite loops
        detection_count = 0
        
        while detection_count < max_detections:
            # Apply mask to current frame
            masked_image = cv2.bitwise_and(working_image, working_image, mask=mask)
            
            # Process the image
            results = self.pose.process(masked_image)
            
            if not results.pose_landmarks:
                # No more poses detected
                break
            
            # Extract pose data
            landmarks = results.pose_landmarks.landmark
            
            pose_data = {
                'landmarks': [],
                'visibility': [],
                'world_landmarks': [],
                'pose_confidence': 1.0,
                'bounds': self._calculate_bounds(landmarks, width, height)
            }
            
            for landmark in landmarks:
                pose_data['landmarks'].append([landmark.x, landmark.y, landmark.z])
                pose_data['visibility'].append(landmark.visibility)
            
            # Extract world landmarks if available
            if results.pose_world_landmarks:
                for landmark in results.pose_world_landmarks.landmark:
                    pose_data['world_landmarks'].append([landmark.x, landmark.y, landmark.z])
            
            all_poses.append(pose_data)
            
            # Create mask to exclude detected person
            mask = self._create_exclusion_mask(mask, landmarks, width, height, buffer=50)
            
            detection_count += 1
        
        return all_poses
    
    def _calculate_bounds(self, landmarks, width: int, height: int) -> Dict:
        """Calculate bounding box for pose landmarks."""
        if not landmarks:
            return {'x': 0, 'y': 0, 'width': width, 'height': height}
        
        xs = [lm.x * width for lm in landmarks if lm.visibility > 0.5]
        ys = [lm.y * height for lm in landmarks if lm.visibility > 0.5]
        
        if not xs or not ys:
            return {'x': 0, 'y': 0, 'width': width, 'height': height}
        
        min_x = max(0, int(min(xs) * 0.95))
        max_x = min(width, int(max(xs) * 1.05))
        min_y = max(0, int(min(ys) * 0.95))
        max_y = min(height, int(max(ys) * 1.05))
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    
    def _create_exclusion_mask(self, current_mask, landmarks, width: int, height: int, buffer: int = 50) -> np.ndarray:
        """Create a mask excluding the detected person."""
        exclusion_mask = current_mask.copy()
        
        if not landmarks:
            return exclusion_mask
        
        # Create region around detected pose
        xs = [lm.x * width for lm in landmarks if lm.visibility > 0.5]
        ys = [lm.y * height for lm in landmarks if lm.visibility > 0.5]
        
        if not xs or not ys:
            return exclusion_mask
        
        # Calculate bounding box with buffer
        min_x = max(0, int(min(xs) - buffer))
        max_x = min(width, int(max(xs) + buffer))
        min_y = max(0, int(min(ys) - buffer))
        max_y = min(height, int(max(ys) + buffer))
        
        # Zero out the detected region
        exclusion_mask[min_y:max_y, min_x:max_x] = 0
        
        return exclusion_mask
    
    def normalize_pose(self, pose_data: Dict, image_shape: Tuple[int, int]) -> np.ndarray:
        """
        Normalize pose landmarks to [0, 1] range and center around torso.
        
        Args:
            pose_data: Pose data from detect_pose
            image_shape: (height, width) of the image
            
        Returns:
            Normalized pose landmarks as numpy array
        """
        landmarks = np.array(pose_data['landmarks'])
        visibility = np.array(pose_data['visibility'])
        
        # Filter out low-visibility landmarks
        valid_mask = visibility > 0.5
        valid_landmarks = landmarks[valid_mask]
        
        if len(valid_landmarks) == 0:
            return np.zeros((33, 3))
        
        # Normalize to [0, 1] range
        normalized_landmarks = landmarks.copy()
        normalized_landmarks[:, 0] = landmarks[:, 0]  # x is already normalized
        normalized_landmarks[:, 1] = landmarks[:, 1]  # y is already normalized
        
        # Center around torso (shoulders and hips)
        torso_center = np.mean([
            normalized_landmarks[11],  # left_shoulder
            normalized_landmarks[12],  # right_shoulder
            normalized_landmarks[23],  # left_hip
            normalized_landmarks[24],  # right_hip
        ], axis=0)
        
        # Center the pose
        normalized_landmarks -= torso_center
        
        # Scale to standard size
        scale = 1.0 / np.std(normalized_landmarks[valid_mask])
        normalized_landmarks *= scale
        
        return normalized_landmarks
    
    def create_pose_image(self, pose_data: Dict, image_shape: Tuple[int, int], 
                         thickness: int = 2, circle_radius: int = 3) -> np.ndarray:
        """
        Create a pose skeleton image from landmarks.
        
        Args:
            pose_data: Pose data from detect_pose
            image_shape: (height, width) of the image
            thickness: Line thickness for skeleton
            circle_radius: Radius for joint circles
            
        Returns:
            Pose skeleton image as numpy array
        """
        landmarks = np.array(pose_data['landmarks'])
        visibility = np.array(pose_data['visibility'])
        
        # Create blank image
        pose_image = np.zeros((image_shape[0], image_shape[1], 3), dtype=np.uint8)
        
        # Convert normalized coordinates to pixel coordinates
        pixel_landmarks = landmarks.copy()
        pixel_landmarks[:, 0] *= image_shape[1]  # x
        pixel_landmarks[:, 1] *= image_shape[0]  # y
        
        # Draw skeleton connections
        for connection in self.connections:
            start_idx, end_idx = connection
            if (visibility[start_idx] > 0.5 and visibility[end_idx] > 0.5):
                start_point = (int(pixel_landmarks[start_idx, 0]), 
                             int(pixel_landmarks[start_idx, 1]))
                end_point = (int(pixel_landmarks[end_idx, 0]), 
                           int(pixel_landmarks[end_idx, 1]))
                
                cv2.line(pose_image, start_point, end_point, (255, 255, 255), thickness)
        
        # Draw joints
        for i, (landmark, vis) in enumerate(zip(pixel_landmarks, visibility)):
            if vis > 0.5:
                center = (int(landmark[0]), int(landmark[1]))
                cv2.circle(pose_image, center, circle_radius, (0, 255, 0), -1)
        
        return pose_image
    
    def get_pose_features(self, pose_data: Dict) -> torch.Tensor:
        """
        Extract pose features for animation transfer.
        
        Args:
            pose_data: Pose data from detect_pose
            
        Returns:
            Pose features as PyTorch tensor
        """
        landmarks = np.array(pose_data['landmarks'])
        visibility = np.array(pose_data['visibility'])
        
        # Create feature vector with position and visibility
        features = []
        for i, (landmark, vis) in enumerate(zip(landmarks, visibility)):
            features.extend([landmark[0], landmark[1], landmark[2], vis])
        
        return torch.tensor(features, dtype=torch.float32)
    
    def calculate_pose_metrics(self, pose_data: Dict) -> Dict[str, float]:
        """
        Calculate pose quality metrics for evaluation.
        
        Args:
            pose_data: Pose data from detect_pose
            
        Returns:
            Dictionary of pose metrics
        """
        landmarks = np.array(pose_data['landmarks'])
        visibility = np.array(pose_data['visibility'])
        
        metrics = {
            'avg_visibility': float(np.mean(visibility)),
            'visible_joints': int(np.sum(visibility > 0.5)),
            'total_joints': len(visibility),
            'pose_confidence': float(np.mean(pose_data['pose_confidence']))
        }
        
        # Calculate joint angles for key joints
        if len(landmarks) >= 33:
            # Left elbow angle
            left_shoulder = landmarks[11]
            left_elbow = landmarks[13]
            left_wrist = landmarks[15]
            metrics['left_elbow_angle'] = self._calculate_angle(
                left_shoulder, left_elbow, left_wrist
            )
            
            # Right elbow angle
            right_shoulder = landmarks[12]
            right_elbow = landmarks[14]
            right_wrist = landmarks[16]
            metrics['right_elbow_angle'] = self._calculate_angle(
                right_shoulder, right_elbow, right_wrist
            )
            
            # Left knee angle
            left_hip = landmarks[23]
            left_knee = landmarks[25]
            left_ankle = landmarks[27]
            metrics['left_knee_angle'] = self._calculate_angle(
                left_hip, left_knee, left_ankle
            )
            
            # Right knee angle
            right_hip = landmarks[24]
            right_knee = landmarks[26]
            right_ankle = landmarks[28]
            metrics['right_knee_angle'] = self._calculate_angle(
                right_hip, right_knee, right_ankle
            )
        
        return metrics
    
    def _calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate angle between three points."""
        v1 = p1 - p2
        v2 = p3 - p2
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return np.arccos(cos_angle) * 180 / np.pi
    
    def close(self):
        """Close the pose detector."""
        self.pose.close()
