"""
Evaluation metrics for pose-to-animation transfer accuracy.
Includes key joint transfer accuracy, temporal smoothness, and quality metrics.
"""

import torch
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt


class PoseTransferMetrics:
    """Comprehensive evaluation metrics for pose-to-animation transfer."""
    
    def __init__(self, key_joints: List[int] = None):
        """
        Initialize metrics calculator.
        
        Args:
            key_joints: List of key joint indices to focus on for evaluation
        """
        if key_joints is None:
            # Default key joints: head, shoulders, elbows, wrists, hips, knees, ankles
            self.key_joints = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        else:
            self.key_joints = key_joints
    
    def calculate_key_joint_accuracy(self, 
                                   predicted_pose: np.ndarray,
                                   target_pose: np.ndarray,
                                   visibility: np.ndarray) -> Dict[str, float]:
        """
        Calculate accuracy metrics for key joint transfer.
        
        Args:
            predicted_pose: Predicted pose landmarks (N, 3)
            target_pose: Target pose landmarks (N, 3)
            visibility: Visibility scores for each joint (N,)
            
        Returns:
            Dictionary of accuracy metrics
        """
        # Filter for visible key joints
        visible_mask = visibility > 0.5
        key_joint_mask = np.zeros(len(visibility), dtype=bool)
        key_joint_mask[self.key_joints] = True
        valid_mask = visible_mask & key_joint_mask
        
        if not np.any(valid_mask):
            return {'key_joint_accuracy': 0.0, 'key_joint_mse': float('inf')}
        
        # Extract key joint positions
        pred_key = predicted_pose[valid_mask]
        target_key = target_pose[valid_mask]
        
        # Calculate Euclidean distance for each key joint
        distances = np.linalg.norm(pred_key - target_key, axis=1)
        
        # Key joint accuracy (percentage within threshold)
        threshold = 0.1  # 10% of image size
        accuracy = np.mean(distances < threshold) * 100
        
        # Mean squared error for key joints
        mse = mean_squared_error(target_key.flatten(), pred_key.flatten())
        
        # Mean absolute error for key joints
        mae = mean_absolute_error(target_key.flatten(), pred_key.flatten())
        
        # Per-joint accuracy
        per_joint_accuracy = {}
        for i, joint_idx in enumerate(self.key_joints):
            if valid_mask[joint_idx]:
                joint_dist = distances[valid_mask][i]
                per_joint_accuracy[f'joint_{joint_idx}'] = float(joint_dist < threshold)
        
        return {
            'key_joint_accuracy': float(accuracy),
            'key_joint_mse': float(mse),
            'key_joint_mae': float(mae),
            'key_joint_mean_distance': float(np.mean(distances)),
            'key_joint_std_distance': float(np.std(distances)),
            'per_joint_accuracy': per_joint_accuracy
        }
    
    def calculate_temporal_smoothness(self, 
                                    pose_sequence: np.ndarray,
                                    frame_rate: float = 30.0) -> Dict[str, float]:
        """
        Calculate temporal smoothness metrics for fast movements.
        
        Args:
            pose_sequence: Sequence of pose landmarks (T, N, 3)
            frame_rate: Frame rate of the sequence
            
        Returns:
            Dictionary of temporal smoothness metrics
        """
        if len(pose_sequence) < 2:
            return {'temporal_smoothness': 0.0}
        
        # Calculate velocity (first derivative)
        velocity = np.diff(pose_sequence, axis=0)
        
        # Calculate acceleration (second derivative)
        acceleration = np.diff(velocity, axis=0)
        
        # Temporal smoothness metrics
        velocity_magnitude = np.linalg.norm(velocity, axis=2)
        acceleration_magnitude = np.linalg.norm(acceleration, axis=2)
        
        # Smoothness score (inverse of acceleration variance)
        smoothness = 1.0 / (1.0 + np.var(acceleration_magnitude))
        
        # Jerk (third derivative) for very fast movements
        if len(pose_sequence) > 2:
            jerk = np.diff(acceleration, axis=0)
            jerk_magnitude = np.linalg.norm(jerk, axis=2)
            jerk_score = 1.0 / (1.0 + np.mean(jerk_magnitude))
        else:
            jerk_score = 1.0
        
        # Motion consistency
        motion_consistency = 1.0 - np.std(velocity_magnitude) / (np.mean(velocity_magnitude) + 1e-8)
        
        return {
            'temporal_smoothness': float(smoothness),
            'jerk_score': float(jerk_score),
            'motion_consistency': float(motion_consistency),
            'mean_velocity': float(np.mean(velocity_magnitude)),
            'max_velocity': float(np.max(velocity_magnitude)),
            'velocity_variance': float(np.var(velocity_magnitude))
        }
    
    def calculate_animation_quality(self, 
                                  generated_image: np.ndarray,
                                  target_image: np.ndarray) -> Dict[str, float]:
        """
        Calculate animation quality metrics.
        
        Args:
            generated_image: Generated animation image
            target_image: Target animation image
            
        Returns:
            Dictionary of quality metrics
        """
        # Convert to grayscale if needed
        if len(generated_image.shape) == 3:
            gen_gray = cv2.cvtColor(generated_image, cv2.COLOR_RGB2GRAY)
            target_gray = cv2.cvtColor(target_image, cv2.COLOR_RGB2GRAY)
        else:
            gen_gray = generated_image
            target_gray = target_image
        
        # Structural Similarity Index (SSIM)
        ssim = self._calculate_ssim(gen_gray, target_gray)
        
        # Peak Signal-to-Noise Ratio (PSNR)
        psnr = self._calculate_psnr(gen_gray, target_gray)
        
        # Mean Squared Error
        mse = mean_squared_error(target_gray.flatten(), gen_gray.flatten())
        
        # Mean Absolute Error
        mae = mean_absolute_error(target_gray.flatten(), gen_gray.flatten())
        
        # Edge preservation
        edge_preservation = self._calculate_edge_preservation(gen_gray, target_gray)
        
        return {
            'ssim': float(ssim),
            'psnr': float(psnr),
            'mse': float(mse),
            'mae': float(mae),
            'edge_preservation': float(edge_preservation)
        }
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index."""
        # Convert to float
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)
        
        # Constants
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        
        # Calculate means
        mu1 = np.mean(img1)
        mu2 = np.mean(img2)
        
        # Calculate variances and covariance
        sigma1_sq = np.var(img1)
        sigma2_sq = np.var(img2)
        sigma12 = np.mean((img1 - mu1) * (img2 - mu2))
        
        # Calculate SSIM
        ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
               ((mu1**2 + mu2**2 + c1) * (sigma1_sq + sigma2_sq + c2))
        
        return ssim
    
    def _calculate_psnr(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Peak Signal-to-Noise Ratio."""
        mse = mean_squared_error(img1.flatten(), img2.flatten())
        if mse == 0:
            return float('inf')
        
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
    
    def _calculate_edge_preservation(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate edge preservation score."""
        # Calculate gradients
        grad1_x = cv2.Sobel(img1, cv2.CV_64F, 1, 0, ksize=3)
        grad1_y = cv2.Sobel(img1, cv2.CV_64F, 0, 1, ksize=3)
        grad2_x = cv2.Sobel(img2, cv2.CV_64F, 1, 0, ksize=3)
        grad2_y = cv2.Sobel(img2, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitudes
        mag1 = np.sqrt(grad1_x**2 + grad1_y**2)
        mag2 = np.sqrt(grad2_x**2 + grad2_y**2)
        
        # Edge preservation score
        edge_score = 1.0 - np.mean(np.abs(mag1 - mag2)) / (np.mean(mag1) + 1e-8)
        
        return max(0, edge_score)
    
    def evaluate_latent_noise_effect(self, 
                                   model: torch.nn.Module,
                                   pose_images: torch.Tensor,
                                   noise_levels: List[float] = [0.0, 0.1, 0.2, 0.3, 0.5]) -> Dict[str, List[float]]:
        """
        Evaluate the effect of latent vector noise on animation quality.
        
        Args:
            model: Trained PoseAnimator model
            pose_images: Input pose images
            noise_levels: List of noise levels to test
            
        Returns:
            Dictionary with quality metrics for each noise level
        """
        results = {
            'noise_levels': noise_levels,
            'ssim_scores': [],
            'psnr_scores': [],
            'mse_scores': [],
            'temporal_smoothness': []
        }
        
        model.eval()
        with torch.no_grad():
            # Generate reference without noise
            reference = model.generator(pose_images)
            
            for noise_level in noise_levels:
                # Add noise to latent representation
                noisy_pose = model.add_noise_to_latent(pose_images, noise_level)
                generated = model.generator(noisy_pose)
                
                # Calculate quality metrics
                gen_np = generated.cpu().numpy().transpose(0, 2, 3, 1)
                ref_np = reference.cpu().numpy().transpose(0, 2, 3, 1)
                
                # Average metrics across batch
                ssim_scores = []
                psnr_scores = []
                mse_scores = []
                
                for i in range(len(gen_np)):
                    quality_metrics = self.calculate_animation_quality(gen_np[i], ref_np[i])
                    ssim_scores.append(quality_metrics['ssim'])
                    psnr_scores.append(quality_metrics['psnr'])
                    mse_scores.append(quality_metrics['mse'])
                
                results['ssim_scores'].append(np.mean(ssim_scores))
                results['psnr_scores'].append(np.mean(psnr_scores))
                results['mse_scores'].append(np.mean(mse_scores))
        
        return results
    
    def compare_paired_unpaired(self, 
                              paired_model: torch.nn.Module,
                              unpaired_model: torch.nn.Module,
                              test_pose_images: torch.Tensor,
                              test_target_images: torch.Tensor) -> Dict[str, Dict[str, float]]:
        """
        Compare paired vs unpaired training approaches.
        
        Args:
            paired_model: Model trained with paired data
            unpaired_model: Model trained with unpaired data
            test_pose_images: Test pose images
            test_target_images: Test target images
            
        Returns:
            Dictionary comparing both approaches
        """
        paired_model.eval()
        unpaired_model.eval()
        
        results = {
            'paired': {},
            'unpaired': {}
        }
        
        with torch.no_grad():
            # Generate animations
            paired_generated = paired_model.generator(test_pose_images)
            unpaired_generated = unpaired_model.generator(test_pose_images)
            
            # Convert to numpy
            paired_np = paired_generated.cpu().numpy().transpose(0, 2, 3, 1)
            unpaired_np = unpaired_generated.cpu().numpy().transpose(0, 2, 3, 1)
            target_np = test_target_images.cpu().numpy().transpose(0, 2, 3, 1)
            
            # Calculate metrics for paired model
            paired_ssim = []
            paired_psnr = []
            paired_mse = []
            
            for i in range(len(paired_np)):
                quality_metrics = self.calculate_animation_quality(paired_np[i], target_np[i])
                paired_ssim.append(quality_metrics['ssim'])
                paired_psnr.append(quality_metrics['psnr'])
                paired_mse.append(quality_metrics['mse'])
            
            results['paired'] = {
                'ssim': float(np.mean(paired_ssim)),
                'psnr': float(np.mean(paired_psnr)),
                'mse': float(np.mean(paired_mse))
            }
            
            # Calculate metrics for unpaired model
            unpaired_ssim = []
            unpaired_psnr = []
            unpaired_mse = []
            
            for i in range(len(unpaired_np)):
                quality_metrics = self.calculate_animation_quality(unpaired_np[i], target_np[i])
                unpaired_ssim.append(quality_metrics['ssim'])
                unpaired_psnr.append(quality_metrics['psnr'])
                unpaired_mse.append(quality_metrics['mse'])
            
            results['unpaired'] = {
                'ssim': float(np.mean(unpaired_ssim)),
                'psnr': float(np.mean(unpaired_psnr)),
                'mse': float(np.mean(unpaired_mse))
            }
        
        return results
    
    def generate_evaluation_report(self, 
                                 metrics: Dict[str, float],
                                 save_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive evaluation report.
        
        Args:
            metrics: Dictionary of evaluation metrics
            save_path: Path to save the report
            
        Returns:
            Formatted evaluation report
        """
        report = "=== PoseAnimator Evaluation Report ===\n\n"
        
        # Key joint accuracy
        if 'key_joint_accuracy' in metrics:
            report += f"Key Joint Transfer Accuracy: {metrics['key_joint_accuracy']:.2f}%\n"
            report += f"Key Joint MSE: {metrics['key_joint_mse']:.6f}\n"
            report += f"Key Joint MAE: {metrics['key_joint_mae']:.6f}\n\n"
        
        # Temporal smoothness
        if 'temporal_smoothness' in metrics:
            report += f"Temporal Smoothness: {metrics['temporal_smoothness']:.4f}\n"
            report += f"Motion Consistency: {metrics['motion_consistency']:.4f}\n"
            report += f"Jerk Score: {metrics['jerk_score']:.4f}\n\n"
        
        # Animation quality
        if 'ssim' in metrics:
            report += f"Structural Similarity (SSIM): {metrics['ssim']:.4f}\n"
            report += f"Peak Signal-to-Noise Ratio (PSNR): {metrics['psnr']:.2f} dB\n"
            report += f"Mean Squared Error: {metrics['mse']:.6f}\n"
            report += f"Edge Preservation: {metrics['edge_preservation']:.4f}\n\n"
        
        # Overall assessment
        overall_score = self._calculate_overall_score(metrics)
        report += f"Overall Quality Score: {overall_score:.2f}/100\n"
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report)
        
        return report
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from individual metrics."""
        score = 0.0
        weight_sum = 0.0
        
        # Key joint accuracy (30% weight)
        if 'key_joint_accuracy' in metrics:
            score += metrics['key_joint_accuracy'] * 0.3
            weight_sum += 0.3
        
        # Temporal smoothness (25% weight)
        if 'temporal_smoothness' in metrics:
            score += metrics['temporal_smoothness'] * 100 * 0.25
            weight_sum += 0.25
        
        # SSIM (25% weight)
        if 'ssim' in metrics:
            score += metrics['ssim'] * 100 * 0.25
            weight_sum += 0.25
        
        # Edge preservation (20% weight)
        if 'edge_preservation' in metrics:
            score += metrics['edge_preservation'] * 100 * 0.2
            weight_sum += 0.2
        
        return score / weight_sum if weight_sum > 0 else 0.0
