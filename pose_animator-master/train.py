"""
Training script for PoseAnimator model.
Supports both paired and unpaired training approaches.
"""

import os
import sys
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import cv2
from PIL import Image
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
from tensorboard import SummaryWriter
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.pix2pix import PoseAnimatorModel, PairedUnpairedTrainer
from utils.pose_detector import PoseDetector
from evaluation.metrics import PoseTransferMetrics


class PoseAnimationDataset(Dataset):
    """Dataset for pose-to-animation training data."""
    
    def __init__(self, data_dir: str, mode: str = "paired", transform=None):
        """
        Initialize dataset.
        
        Args:
            data_dir: Directory containing training data
            mode: "paired" or "unpaired" training mode
            transform: Optional data transformations
        """
        self.data_dir = data_dir
        self.mode = mode
        self.transform = transform
        
        # Load data paths
        self.pose_images = []
        self.animation_images = []
        self._load_data_paths()
        
        # Initialize pose detector
        self.pose_detector = PoseDetector()
        
    def _load_data_paths(self):
        """Load paths to pose and animation images."""
        pose_dir = os.path.join(self.data_dir, "poses")
        animation_dir = os.path.join(self.data_dir, "animations")
        
        if not os.path.exists(pose_dir) or not os.path.exists(animation_dir):
            raise ValueError(f"Data directories not found: {pose_dir}, {animation_dir}")
        
        # Get all image files
        pose_files = sorted([f for f in os.listdir(pose_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        animation_files = sorted([f for f in os.listdir(animation_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        
        if self.mode == "paired":
            # Paired training: match pose and animation files by name
            common_files = set(pose_files) & set(animation_files)
            for filename in sorted(common_files):
                self.pose_images.append(os.path.join(pose_dir, filename))
                self.animation_images.append(os.path.join(animation_dir, filename))
        else:
            # Unpaired training: use all available files
            self.pose_images = [os.path.join(pose_dir, f) for f in pose_files]
            self.animation_images = [os.path.join(animation_dir, f) for f in animation_files]
        
        print(f"Loaded {len(self.pose_images)} pose images and {len(self.animation_images)} animation images")
    
    def __len__(self):
        if self.mode == "paired":
            return len(self.pose_images)
        else:
            return max(len(self.pose_images), len(self.animation_images))
    
    def __getitem__(self, idx):
        """Get a training sample."""
        if self.mode == "paired":
            # Paired training
            pose_path = self.pose_images[idx]
            animation_path = self.animation_images[idx]
        else:
            # Unpaired training: randomly sample pose and animation
            pose_idx = idx % len(self.pose_images)
            animation_idx = np.random.randint(0, len(self.animation_images))
            pose_path = self.pose_images[pose_idx]
            animation_path = self.animation_images[animation_idx]
        
        # Load images
        pose_image = self._load_image(pose_path)
        animation_image = self._load_image(animation_path)
        
        # Apply transformations
        if self.transform:
            pose_image = self.transform(pose_image)
            animation_image = self.transform(animation_image)
        
        return pose_image, animation_image
    
    def _load_image(self, path: str) -> torch.Tensor:
        """Load and preprocess image."""
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (256, 256))
        
        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Convert to tensor
        tensor = torch.from_numpy(image).permute(2, 0, 1)
        
        return tensor


class PoseAnimatorTrainer:
    """Trainer for PoseAnimator model."""
    
    def __init__(self, 
                 model: PoseAnimatorModel,
                 train_loader: DataLoader,
                 val_loader: DataLoader,
                 device: str = 'cuda',
                 log_dir: str = 'logs'):
        """
        Initialize trainer.
        
        Args:
            model: PoseAnimator model
            train_loader: Training data loader
            val_loader: Validation data loader
            device: Device to run training on
            log_dir: Directory for logging
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.log_dir = log_dir
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize tensorboard writer
        self.writer = SummaryWriter(log_dir)
        
        # Initialize optimizers
        self.optimizer_gen = optim.Adam(self.model.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.optimizer_disc = optim.Adam(self.model.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        # Initialize trainer
        self.trainer = PairedUnpairedTrainer(self.model, device)
        
        # Initialize metrics
        self.metrics = PoseTransferMetrics()
        
        # Training state
        self.current_epoch = 0
        self.best_val_loss = float('inf')
        
    def train_epoch(self, epoch: int, mode: str = "paired") -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        
        total_gen_loss = 0.0
        total_disc_loss = 0.0
        total_cycle_loss = 0.0
        num_batches = 0
        
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {epoch}")
        
        for batch_idx, (pose_images, animation_images) in enumerate(progress_bar):
            pose_images = pose_images.to(self.device)
            animation_images = animation_images.to(self.device)
            
            # Train based on mode
            if mode == "paired":
                losses = self.trainer.train_paired(
                    pose_images, animation_images,
                    self.optimizer_gen, self.optimizer_disc
                )
            else:
                losses = self.trainer.train_unpaired(
                    pose_images, animation_images,
                    self.optimizer_gen, self.optimizer_disc
                )
            
            # Accumulate losses
            total_gen_loss += losses['gen_loss']
            total_disc_loss += losses['disc_loss']
            if 'cycle_loss' in losses:
                total_cycle_loss += losses['cycle_loss']
            
            num_batches += 1
            
            # Update progress bar
            progress_bar.set_postfix({
                'Gen Loss': f"{losses['gen_loss']:.4f}",
                'Disc Loss': f"{losses['disc_loss']:.4f}"
            })
            
            # Log to tensorboard
            global_step = epoch * len(self.train_loader) + batch_idx
            self.writer.add_scalar('Train/Generator_Loss', losses['gen_loss'], global_step)
            self.writer.add_scalar('Train/Discriminator_Loss', losses['disc_loss'], global_step)
            if 'cycle_loss' in losses:
                self.writer.add_scalar('Train/Cycle_Loss', losses['cycle_loss'], global_step)
        
        # Calculate average losses
        avg_gen_loss = total_gen_loss / num_batches
        avg_disc_loss = total_disc_loss / num_batches
        avg_cycle_loss = total_cycle_loss / num_batches if total_cycle_loss > 0 else 0.0
        
        return {
            'gen_loss': avg_gen_loss,
            'disc_loss': avg_disc_loss,
            'cycle_loss': avg_cycle_loss
        }
    
    def validate_epoch(self, epoch: int) -> Dict[str, float]:
        """Validate for one epoch."""
        self.model.eval()
        
        total_gen_loss = 0.0
        total_disc_loss = 0.0
        total_ssim = 0.0
        total_psnr = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for pose_images, animation_images in tqdm(self.val_loader, desc="Validation"):
                pose_images = pose_images.to(self.device)
                animation_images = animation_images.to(self.device)
                
                # Forward pass
                results = self.model(pose_images, animation_images, mode='train')
                
                # Calculate losses
                gen_loss = results['gen_loss']
                disc_loss = results['disc_loss']
                
                # Calculate quality metrics
                generated = results['generated']
                gen_np = generated.cpu().numpy().transpose(0, 2, 3, 1)
                target_np = animation_images.cpu().numpy().transpose(0, 2, 3, 1)
                
                batch_ssim = []
                batch_psnr = []
                for i in range(len(gen_np)):
                    quality_metrics = self.metrics.calculate_animation_quality(gen_np[i], target_np[i])
                    batch_ssim.append(quality_metrics['ssim'])
                    batch_psnr.append(quality_metrics['psnr'])
                
                # Accumulate metrics
                total_gen_loss += gen_loss.item()
                total_disc_loss += disc_loss.item()
                total_ssim += np.mean(batch_ssim)
                total_psnr += np.mean(batch_psnr)
                num_batches += 1
        
        # Calculate average metrics
        avg_gen_loss = total_gen_loss / num_batches
        avg_disc_loss = total_disc_loss / num_batches
        avg_ssim = total_ssim / num_batches
        avg_psnr = total_psnr / num_batches
        
        return {
            'gen_loss': avg_gen_loss,
            'disc_loss': avg_disc_loss,
            'ssim': avg_ssim,
            'psnr': avg_psnr
        }
    
    def train(self, epochs: int, mode: str = "paired", save_interval: int = 10):
        """Train the model."""
        print(f"Starting training for {epochs} epochs in {mode} mode")
        
        for epoch in range(epochs):
            self.current_epoch = epoch
            
            # Train epoch
            train_metrics = self.train_epoch(epoch, mode)
            
            # Validate epoch
            val_metrics = self.validate_epoch(epoch)
            
            # Log metrics
            self.writer.add_scalar('Epoch/Train_Gen_Loss', train_metrics['gen_loss'], epoch)
            self.writer.add_scalar('Epoch/Train_Disc_Loss', train_metrics['disc_loss'], epoch)
            self.writer.add_scalar('Epoch/Val_Gen_Loss', val_metrics['gen_loss'], epoch)
            self.writer.add_scalar('Epoch/Val_Disc_Loss', val_metrics['disc_loss'], epoch)
            self.writer.add_scalar('Epoch/Val_SSIM', val_metrics['ssim'], epoch)
            self.writer.add_scalar('Epoch/Val_PSNR', val_metrics['psnr'], epoch)
            
            # Print metrics
            print(f"Epoch {epoch}/{epochs-1}:")
            print(f"  Train - Gen: {train_metrics['gen_loss']:.4f}, Disc: {train_metrics['disc_loss']:.4f}")
            print(f"  Val   - Gen: {val_metrics['gen_loss']:.4f}, Disc: {val_metrics['disc_loss']:.4f}")
            print(f"  Val   - SSIM: {val_metrics['ssim']:.4f}, PSNR: {val_metrics['psnr']:.2f}")
            
            # Save best model
            if val_metrics['gen_loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['gen_loss']
                self.save_checkpoint(epoch, is_best=True)
            
            # Save checkpoint at intervals
            if (epoch + 1) % save_interval == 0:
                self.save_checkpoint(epoch, is_best=False)
            
            # Generate sample images
            if (epoch + 1) % 5 == 0:
                self.generate_sample_images(epoch)
        
        print("Training completed!")
        self.writer.close()
    
    def save_checkpoint(self, epoch: int, is_best: bool = False):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_gen_state_dict': self.optimizer_gen.state_dict(),
            'optimizer_disc_state_dict': self.optimizer_disc.state_dict(),
            'best_val_loss': self.best_val_loss
        }
        
        # Save regular checkpoint
        checkpoint_path = os.path.join(self.log_dir, f'checkpoint_epoch_{epoch}.pth')
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model
        if is_best:
            best_path = os.path.join(self.log_dir, 'best_model.pth')
            torch.save(checkpoint, best_path)
            print(f"Saved best model at epoch {epoch}")
    
    def generate_sample_images(self, epoch: int):
        """Generate sample images for visualization."""
        self.model.eval()
        
        with torch.no_grad():
            # Get a batch from validation set
            pose_images, animation_images = next(iter(self.val_loader))
            pose_images = pose_images.to(self.device)
            animation_images = animation_images.to(self.device)
            
            # Generate animations
            generated = self.model.generator(pose_images)
            
            # Convert to numpy
            pose_np = pose_images.cpu().numpy().transpose(0, 2, 3, 1)
            gen_np = generated.cpu().numpy().transpose(0, 2, 3, 1)
            target_np = animation_images.cpu().numpy().transpose(0, 2, 3, 1)
            
            # Create comparison image
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
            plt.savefig(os.path.join(self.log_dir, f'samples_epoch_{epoch}.png'))
            plt.close()


def create_sample_data(data_dir: str, num_samples: int = 100):
    """Create sample training data for testing."""
    print(f"Creating sample data in {data_dir}")
    
    # Create directories
    pose_dir = os.path.join(data_dir, "poses")
    animation_dir = os.path.join(data_dir, "animations")
    os.makedirs(pose_dir, exist_ok=True)
    os.makedirs(animation_dir, exist_ok=True)
    
    # Initialize pose detector
    pose_detector = PoseDetector()
    
    # Create sample images
    for i in range(num_samples):
        # Create random pose image
        pose_image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        
        # Create corresponding animation (simple transformation for demo)
        animation_image = cv2.GaussianBlur(pose_image, (15, 15), 0)
        animation_image = cv2.addWeighted(pose_image, 0.7, animation_image, 0.3, 0)
        
        # Add some color variation
        animation_image[:, :, 0] = np.clip(animation_image[:, :, 0] * 1.2, 0, 255)
        animation_image[:, :, 2] = np.clip(animation_image[:, :, 2] * 0.8, 0, 255)
        
        # Save images
        cv2.imwrite(os.path.join(pose_dir, f"pose_{i:04d}.jpg"), pose_image)
        cv2.imwrite(os.path.join(animation_dir, f"animation_{i:04d}.jpg"), animation_image)
    
    print(f"Created {num_samples} sample images")


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train PoseAnimator model")
    parser.add_argument("--data_path", type=str, required=True, help="Path to training data")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--mode", choices=["paired", "unpaired"], default="paired", help="Training mode")
    parser.add_argument("--create_sample_data", action="store_true", help="Create sample data for testing")
    parser.add_argument("--log_dir", type=str, default="logs", help="Log directory")
    parser.add_argument("--device", type=str, default="auto", help="Device to use")
    
    args = parser.parse_args()
    
    # Set device
    if args.device == "auto":
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    # Create sample data if requested
    if args.create_sample_data:
        create_sample_data(args.data_path)
        return
    
    # Create datasets
    train_dataset = PoseAnimationDataset(args.data_path, mode=args.mode)
    val_dataset = PoseAnimationDataset(args.data_path, mode=args.mode)
    
    # Split dataset
    train_size = int(0.8 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        train_dataset, [train_size, val_size]
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=2)
    
    # Create model
    model = PoseAnimatorModel(use_temporal_smoothing=True)
    
    # Create trainer
    trainer = PoseAnimatorTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        log_dir=args.log_dir
    )
    
    # Train model
    trainer.train(epochs=args.epochs, mode=args.mode)


if __name__ == "__main__":
    main()
