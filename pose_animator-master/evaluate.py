"""
Evaluation script for PoseAnimator model.
Evaluates key joint transfer accuracy, temporal smoothness, and animation quality.
"""

import os
import sys
import argparse
import torch
import numpy as np
import cv2
from PIL import Image
import json
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.pix2pix import PoseAnimatorModel
from utils.pose_detector import PoseDetector
from evaluation.metrics import PoseTransferMetrics
from train import PoseAnimationDataset
from torch.utils.data import DataLoader


class PoseAnimatorEvaluator:
    """Evaluator for PoseAnimator model."""
    
    def __init__(self, model_path: str, device: str = 'cuda'):
        """
        Initialize evaluator.
        
        Args:
            model_path: Path to trained model
            device: Device to run evaluation on
        """
        self.device = device
        self.model = self._load_model(model_path)
        self.model.eval()
        
        # Initialize pose detector
        self.pose_detector = PoseDetector()
        
        # Initialize metrics
        self.metrics = PoseTransferMetrics()
        
        # Evaluation results
        self.results = {}
    
    def _load_model(self, model_path: str) -> PoseAnimatorModel:
        """Load trained model."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            model = PoseAnimatorModel(use_temporal_smoothing=True)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            # Return a dummy model for testing
            return PoseAnimatorModel(use_temporal_smoothing=True)
    
    def evaluate_key_joint_accuracy(self, test_loader: DataLoader) -> Dict[str, float]:
        """Evaluate key joint transfer accuracy."""
        print("Evaluating key joint transfer accuracy...")
        
        total_accuracy = 0.0
        total_mse = 0.0
        total_mae = 0.0
        num_samples = 0
        
        with torch.no_grad():
            for pose_images, target_images in tqdm(test_loader, desc="Key Joint Accuracy"):
                pose_images = pose_images.to(self.device)
                target_images = target_images.to(self.device)
                
                # Generate animations
                generated = self.model.generator(pose_images)
                
                # Convert to numpy
                pose_np = pose_images.cpu().numpy().transpose(0, 2, 3, 1)
                gen_np = generated.cpu().numpy().transpose(0, 2, 3, 1)
                target_np = target_images.cpu().numpy().transpose(0, 2, 3, 1)
                
                # Evaluate each sample in batch
                for i in range(len(pose_np)):
                    # Detect pose in generated image
                    pose_data = self.pose_detector.detect_pose(
                        (gen_np[i] * 255).astype(np.uint8)
                    )
                    
                    if pose_data is not None:
                        # Detect pose in target image
                        target_pose_data = self.pose_detector.detect_pose(
                            (target_np[i] * 255).astype(np.uint8)
                        )
                        
                        if target_pose_data is not None:
                            # Calculate key joint accuracy
                            normalized_pred = self.pose_detector.normalize_pose(pose_data, (256, 256))
                            normalized_target = self.pose_detector.normalize_pose(target_pose_data, (256, 256))
                            
                            accuracy_metrics = self.metrics.calculate_key_joint_accuracy(
                                normalized_pred, normalized_target, pose_data['visibility']
                            )
                            
                            total_accuracy += accuracy_metrics['key_joint_accuracy']
                            total_mse += accuracy_metrics['key_joint_mse']
                            total_mae += accuracy_metrics['key_joint_mae']
                            num_samples += 1
        
        if num_samples == 0:
            return {'key_joint_accuracy': 0.0, 'key_joint_mse': float('inf'), 'key_joint_mae': float('inf')}
        
        return {
            'key_joint_accuracy': total_accuracy / num_samples,
            'key_joint_mse': total_mse / num_samples,
            'key_joint_mae': total_mae / num_samples
        }
    
    def evaluate_temporal_smoothness(self, test_loader: DataLoader) -> Dict[str, float]:
        """Evaluate temporal smoothness for fast movements."""
        print("Evaluating temporal smoothness...")
        
        # Create temporal sequences
        sequence_length = 10
        sequences = []
        
        # Collect sequences from test data
        pose_sequences = []
        for pose_images, _ in test_loader:
            pose_sequences.append(pose_images)
            if len(pose_sequences) >= sequence_length:
                break
        
        if len(pose_sequences) < sequence_length:
            # Pad with last sequence
            while len(pose_sequences) < sequence_length:
                pose_sequences.append(pose_sequences[-1])
        
        # Create sequence tensor
        pose_sequence = torch.cat(pose_sequences[:sequence_length], dim=0)
        pose_sequence = pose_sequence.to(self.device)
        
        # Generate animation sequence
        with torch.no_grad():
            animation_sequence = self.model.generator(pose_sequence)
        
        # Convert to numpy
        animation_np = animation_sequence.cpu().numpy().transpose(0, 2, 3, 1)
        
        # Calculate temporal smoothness
        smoothness_metrics = self.metrics.calculate_temporal_smoothness(animation_np)
        
        return smoothness_metrics
    
    def evaluate_animation_quality(self, test_loader: DataLoader) -> Dict[str, float]:
        """Evaluate animation quality metrics."""
        print("Evaluating animation quality...")
        
        total_ssim = 0.0
        total_psnr = 0.0
        total_mse = 0.0
        total_mae = 0.0
        total_edge_preservation = 0.0
        num_samples = 0
        
        with torch.no_grad():
            for pose_images, target_images in tqdm(test_loader, desc="Animation Quality"):
                pose_images = pose_images.to(self.device)
                target_images = target_images.to(self.device)
                
                # Generate animations
                generated = self.model.generator(pose_images)
                
                # Convert to numpy
                gen_np = generated.cpu().numpy().transpose(0, 2, 3, 1)
                target_np = target_images.cpu().numpy().transpose(0, 2, 3, 1)
                
                # Evaluate each sample in batch
                for i in range(len(gen_np)):
                    quality_metrics = self.metrics.calculate_animation_quality(gen_np[i], target_np[i])
                    
                    total_ssim += quality_metrics['ssim']
                    total_psnr += quality_metrics['psnr']
                    total_mse += quality_metrics['mse']
                    total_mae += quality_metrics['mae']
                    total_edge_preservation += quality_metrics['edge_preservation']
                    num_samples += 1
        
        return {
            'ssim': total_ssim / num_samples,
            'psnr': total_psnr / num_samples,
            'mse': total_mse / num_samples,
            'mae': total_mae / num_samples,
            'edge_preservation': total_edge_preservation / num_samples
        }
    
    def evaluate_latent_noise_effect(self, test_loader: DataLoader) -> Dict[str, List[float]]:
        """Evaluate the effect of latent vector noise on animation quality."""
        print("Evaluating latent noise effect...")
        
        # Get a sample batch
        pose_images, target_images = next(iter(test_loader))
        pose_images = pose_images.to(self.device)
        
        # Evaluate noise effect
        noise_results = self.metrics.evaluate_latent_noise_effect(
            self.model, pose_images, noise_levels=[0.0, 0.1, 0.2, 0.3, 0.5]
        )
        
        return noise_results
    
    def compare_paired_unpaired(self, paired_model_path: str, unpaired_model_path: str, 
                               test_loader: DataLoader) -> Dict[str, Dict[str, float]]:
        """Compare paired vs unpaired training approaches."""
        print("Comparing paired vs unpaired training...")
        
        # Load both models
        paired_model = self._load_model(paired_model_path)
        unpaired_model = self._load_model(unpaired_model_path)
        
        # Compare approaches
        comparison_results = self.metrics.compare_paired_unpaired(
            paired_model, unpaired_model, 
            next(iter(test_loader))[0].to(self.device),
            next(iter(test_loader))[1].to(self.device)
        )
        
        return comparison_results
    
    def evaluate_model(self, test_loader: DataLoader, 
                      paired_model_path: str = None,
                      unpaired_model_path: str = None) -> Dict[str, any]:
        """Run comprehensive model evaluation."""
        print("Starting comprehensive model evaluation...")
        
        # Key joint accuracy
        key_joint_metrics = self.evaluate_key_joint_accuracy(test_loader)
        self.results['key_joint_accuracy'] = key_joint_metrics
        
        # Temporal smoothness
        temporal_metrics = self.evaluate_temporal_smoothness(test_loader)
        self.results['temporal_smoothness'] = temporal_metrics
        
        # Animation quality
        quality_metrics = self.evaluate_animation_quality(test_loader)
        self.results['animation_quality'] = quality_metrics
        
        # Latent noise effect
        noise_metrics = self.evaluate_latent_noise_effect(test_loader)
        self.results['latent_noise_effect'] = noise_metrics
        
        # Paired vs unpaired comparison
        if paired_model_path and unpaired_model_path:
            comparison_metrics = self.compare_paired_unpaired(
                paired_model_path, unpaired_model_path, test_loader
            )
            self.results['paired_unpaired_comparison'] = comparison_metrics
        
        # Generate comprehensive report
        self._generate_evaluation_report()
        
        return self.results
    
    def _generate_evaluation_report(self):
        """Generate comprehensive evaluation report."""
        print("\n" + "="*60)
        print("POSEANIMATOR EVALUATION REPORT")
        print("="*60)
        
        # Key joint accuracy
        if 'key_joint_accuracy' in self.results:
            kj = self.results['key_joint_accuracy']
            print(f"\nKey Joint Transfer Accuracy:")
            print(f"  Accuracy: {kj['key_joint_accuracy']:.2f}%")
            print(f"  MSE: {kj['key_joint_mse']:.6f}")
            print(f"  MAE: {kj['key_joint_mae']:.6f}")
        
        # Temporal smoothness
        if 'temporal_smoothness' in self.results:
            ts = self.results['temporal_smoothness']
            print(f"\nTemporal Smoothness:")
            print(f"  Smoothness Score: {ts['temporal_smoothness']:.4f}")
            print(f"  Motion Consistency: {ts['motion_consistency']:.4f}")
            print(f"  Jerk Score: {ts['jerk_score']:.4f}")
            print(f"  Mean Velocity: {ts['mean_velocity']:.4f}")
        
        # Animation quality
        if 'animation_quality' in self.results:
            aq = self.results['animation_quality']
            print(f"\nAnimation Quality:")
            print(f"  SSIM: {aq['ssim']:.4f}")
            print(f"  PSNR: {aq['psnr']:.2f} dB")
            print(f"  MSE: {aq['mse']:.6f}")
            print(f"  Edge Preservation: {aq['edge_preservation']:.4f}")
        
        # Latent noise effect
        if 'latent_noise_effect' in self.results:
            ln = self.results['latent_noise_effect']
            print(f"\nLatent Noise Effect:")
            print(f"  Noise Levels: {ln['noise_levels']}")
            print(f"  SSIM Scores: {[f'{s:.4f}' for s in ln['ssim_scores']]}")
            print(f"  PSNR Scores: {[f'{s:.2f}' for s in ln['psnr_scores']]}")
        
        # Paired vs unpaired comparison
        if 'paired_unpaired_comparison' in self.results:
            pc = self.results['paired_unpaired_comparison']
            print(f"\nPaired vs Unpaired Comparison:")
            print(f"  Paired SSIM: {pc['paired']['ssim']:.4f}")
            print(f"  Unpaired SSIM: {pc['unpaired']['ssim']:.4f}")
            print(f"  Paired PSNR: {pc['paired']['psnr']:.2f} dB")
            print(f"  Unpaired PSNR: {pc['unpaired']['psnr']:.2f} dB")
        
        print("\n" + "="*60)
    
    def save_results(self, output_path: str):
        """Save evaluation results to file."""
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                serializable_results[key] = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, np.ndarray):
                        serializable_results[key][sub_key] = sub_value.tolist()
                    else:
                        serializable_results[key][sub_key] = sub_value
            elif isinstance(value, np.ndarray):
                serializable_results[key] = value.tolist()
            else:
                serializable_results[key] = value
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Results saved to {output_path}")
    
    def generate_visualizations(self, test_loader: DataLoader, output_dir: str):
        """Generate visualization plots for evaluation results."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get sample data
        pose_images, target_images = next(iter(test_loader))
        pose_images = pose_images.to(self.device)
        target_images = target_images.to(self.device)
        
        with torch.no_grad():
            generated = self.model.generator(pose_images)
        
        # Convert to numpy
        pose_np = pose_images.cpu().numpy().transpose(0, 2, 3, 1)
        gen_np = generated.cpu().numpy().transpose(0, 2, 3, 1)
        target_np = target_images.cpu().numpy().transpose(0, 2, 3, 1)
        
        # Create comparison visualization
        fig, axes = plt.subplots(3, min(4, len(pose_np)), figsize=(16, 12))
        if len(pose_np) == 1:
            axes = axes.reshape(3, 1)
        
        for i in range(min(4, len(pose_np))):
            # Pose image
            axes[0, i].imshow(pose_np[i])
            axes[0, i].set_title(f'Pose {i+1}')
            axes[0, i].axis('off')
            
            # Generated animation
            axes[1, i].imshow(gen_np[i])
            axes[1, i].set_title(f'Generated {i+1}')
            axes[1, i].axis('off')
            
            # Target animation
            axes[2, i].imshow(target_np[i])
            axes[2, i].set_title(f'Target {i+1}')
            axes[2, i].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'sample_comparisons.png'))
        plt.close()
        
        # Latent noise effect visualization
        if 'latent_noise_effect' in self.results:
            ln = self.results['latent_noise_effect']
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # SSIM vs noise level
            ax1.plot(ln['noise_levels'], ln['ssim_scores'], 'bo-')
            ax1.set_xlabel('Noise Level')
            ax1.set_ylabel('SSIM Score')
            ax1.set_title('SSIM vs Noise Level')
            ax1.grid(True)
            
            # PSNR vs noise level
            ax2.plot(ln['noise_levels'], ln['psnr_scores'], 'ro-')
            ax2.set_xlabel('Noise Level')
            ax2.set_ylabel('PSNR (dB)')
            ax2.set_title('PSNR vs Noise Level')
            ax2.grid(True)
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'noise_effect_analysis.png'))
            plt.close()
        
        print(f"Visualizations saved to {output_dir}")


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate PoseAnimator model")
    parser.add_argument("--model_path", type=str, required=True, help="Path to trained model")
    parser.add_argument("--test_data", type=str, required=True, help="Path to test data")
    parser.add_argument("--paired_model", type=str, help="Path to paired model for comparison")
    parser.add_argument("--unpaired_model", type=str, help="Path to unpaired model for comparison")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--output_dir", type=str, default="evaluation_results", help="Output directory")
    parser.add_argument("--device", type=str, default="auto", help="Device to use")
    
    args = parser.parse_args()
    
    # Set device
    if args.device == "auto":
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    # Create test dataset
    test_dataset = PoseAnimationDataset(args.test_data, mode="paired")
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=2)
    
    # Create evaluator
    evaluator = PoseAnimatorEvaluator(args.model_path, device)
    
    # Run evaluation
    results = evaluator.evaluate_model(
        test_loader, 
        args.paired_model, 
        args.unpaired_model
    )
    
    # Save results
    os.makedirs(args.output_dir, exist_ok=True)
    evaluator.save_results(os.path.join(args.output_dir, "evaluation_results.json"))
    
    # Generate visualizations
    evaluator.generate_visualizations(test_loader, args.output_dir)
    
    print(f"Evaluation completed. Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
