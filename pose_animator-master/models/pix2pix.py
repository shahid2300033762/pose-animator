"""
Pix2Pix model implementation for pose-to-animation transfer.
Includes generator, discriminator, and training utilities.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional, Dict, List


class UNetBlock(nn.Module):
    """U-Net block with skip connections."""
    
    def __init__(self, in_channels: int, out_channels: int, 
                 down: bool = True, use_dropout: bool = False):
        super().__init__()
        
        self.down = down
        
        if down:
            self.conv = nn.Conv2d(in_channels, out_channels, 3, 2, 1, bias=False)
        else:
            self.conv = nn.ConvTranspose2d(in_channels, out_channels, 3, 2, 1, bias=False)
        
        self.bn = nn.BatchNorm2d(out_channels)
        self.dropout = nn.Dropout(0.5) if use_dropout else None
        
    def forward(self, x: torch.Tensor, skip: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = self.conv(x)
        x = self.bn(x)
        
        if self.dropout is not None:
            x = self.dropout(x)
        
        if not self.down and skip is not None:
            x = torch.cat([x, skip], dim=1)
        
        return F.leaky_relu(x, 0.2) if self.down else F.relu(x)


class PoseToAnimationGenerator(nn.Module):
    """Generator network for pose-to-animation transfer using simplified U-Net architecture."""
    
    def __init__(self, input_channels: int = 3, output_channels: int = 3, 
                 ngf: int = 64, use_dropout: bool = True):
        super().__init__()
        
        # Simplified encoder-decoder architecture
        self.encoder = nn.Sequential(
            # 256x256 -> 128x128
            nn.Conv2d(input_channels, ngf, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf),
            nn.LeakyReLU(0.2, inplace=True),
            
            # 128x128 -> 64x64
            nn.Conv2d(ngf, ngf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 2),
            nn.LeakyReLU(0.2, inplace=True),
            
            # 64x64 -> 32x32
            nn.Conv2d(ngf * 2, ngf * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 4),
            nn.LeakyReLU(0.2, inplace=True),
            
            # 32x32 -> 16x16
            nn.Conv2d(ngf * 4, ngf * 8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 8),
            nn.LeakyReLU(0.2, inplace=True),
        )
        
        # Bottleneck
        self.bottleneck = nn.Sequential(
            nn.Conv2d(ngf * 8, ngf * 8, 3, 1, 1, bias=False),
            nn.BatchNorm2d(ngf * 8),
            nn.ReLU(inplace=True),
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            # 16x16 -> 32x32
            nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 4),
            nn.ReLU(inplace=True),
            
            # 32x32 -> 64x64
            nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 2),
            nn.ReLU(inplace=True),
            
            # 64x64 -> 128x128
            nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf),
            nn.ReLU(inplace=True),
            
            # 128x128 -> 256x256
            nn.ConvTranspose2d(ngf, output_channels, 4, 2, 1, bias=False),
            nn.Tanh()
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encoder
        encoded = self.encoder(x)
        
        # Bottleneck
        bottleneck = self.bottleneck(encoded)
        
        # Decoder
        decoded = self.decoder(bottleneck)
        
        return decoded


class PatchDiscriminator(nn.Module):
    """PatchGAN discriminator for pose-to-animation transfer."""
    
    def __init__(self, input_channels: int = 6, ndf: int = 64):
        super().__init__()
        
        self.conv1 = nn.Conv2d(input_channels, ndf, 3, 2, 1, bias=False)
        self.conv2 = nn.Conv2d(ndf, ndf * 2, 3, 2, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(ndf * 2)
        self.conv3 = nn.Conv2d(ndf * 2, ndf * 4, 3, 2, 1, bias=False)
        self.bn3 = nn.BatchNorm2d(ndf * 4)
        self.conv4 = nn.Conv2d(ndf * 4, ndf * 8, 3, 1, 1, bias=False)
        self.bn4 = nn.BatchNorm2d(ndf * 8)
        self.conv5 = nn.Conv2d(ndf * 8, 1, 3, 1, 1, bias=False)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.leaky_relu(self.conv1(x), 0.2)
        x = F.leaky_relu(self.bn2(self.conv2(x)), 0.2)
        x = F.leaky_relu(self.bn3(self.conv3(x)), 0.2)
        x = F.leaky_relu(self.bn4(self.conv4(x)), 0.2)
        x = torch.sigmoid(self.conv5(x))
        
        return x


class TemporalSmoother(nn.Module):
    """Temporal smoothing module for handling fast movements."""
    
    def __init__(self, input_channels: int = 3, hidden_dim: int = 64, 
                 sequence_length: int = 5):
        super().__init__()
        
        self.sequence_length = sequence_length
        self.hidden_dim = hidden_dim
        
        # LSTM for temporal modeling
        self.lstm = nn.LSTM(input_channels, hidden_dim, batch_first=True)
        
        # Convolutional layers for spatial processing
        self.conv1 = nn.Conv2d(hidden_dim, 64, 3, 1, 1)
        self.conv2 = nn.Conv2d(64, 32, 3, 1, 1)
        self.conv3 = nn.Conv2d(32, input_channels, 3, 1, 1)
        
        self.bn1 = nn.BatchNorm2d(64)
        self.bn2 = nn.BatchNorm2d(32)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply temporal smoothing to input sequence.
        
        Args:
            x: Input tensor of shape (batch, sequence, channels, height, width)
            
        Returns:
            Smoothed output tensor
        """
        batch_size, seq_len, channels, height, width = x.shape
        
        # Reshape for LSTM processing
        x_flat = x.view(batch_size, seq_len, channels * height * width)
        
        # Apply LSTM
        lstm_out, _ = self.lstm(x_flat)
        
        # Take the last output
        last_output = lstm_out[:, -1, :].view(batch_size, self.hidden_dim, height, width)
        
        # Apply convolutional layers
        x = F.relu(self.bn1(self.conv1(last_output)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = torch.tanh(self.conv3(x))
        
        return x


class PoseAnimatorModel(nn.Module):
    """Complete PoseAnimator model with generator, discriminator, and temporal smoothing."""
    
    def __init__(self, input_channels: int = 3, output_channels: int = 3,
                 ngf: int = 64, ndf: int = 64, use_temporal_smoothing: bool = True):
        super().__init__()
        
        self.use_temporal_smoothing = use_temporal_smoothing
        
        # Generator
        self.generator = PoseToAnimationGenerator(
            input_channels, output_channels, ngf
        )
        
        # Discriminator
        self.discriminator = PatchDiscriminator(
            input_channels + output_channels, ndf
        )
        
        # Temporal smoother
        if use_temporal_smoothing:
            self.temporal_smoother = TemporalSmoother(
                output_channels, hidden_dim=64, sequence_length=5
            )
        
        # Loss functions
        self.l1_loss = nn.L1Loss()
        self.bce_loss = nn.BCELoss()
        
    def forward(self, pose_images: torch.Tensor, 
                target_images: Optional[torch.Tensor] = None,
                mode: str = 'generate') -> Dict[str, torch.Tensor]:
        """
        Forward pass through the model.
        
        Args:
            pose_images: Input pose images
            target_images: Target animation images (for training)
            mode: 'generate', 'discriminate', or 'train'
            
        Returns:
            Dictionary containing model outputs and losses
        """
        results = {}
        
        if mode == 'generate':
            # Generate animation from pose
            generated = self.generator(pose_images)
            results['generated'] = generated
            
        elif mode == 'discriminate':
            # Discriminate real vs fake
            if target_images is not None:
                real_pair = torch.cat([pose_images, target_images], dim=1)
                fake_pair = torch.cat([pose_images, self.generator(pose_images)], dim=1)
                
                real_pred = self.discriminator(real_pair)
                fake_pred = self.discriminator(fake_pair)
                
                results['real_pred'] = real_pred
                results['fake_pred'] = fake_pred
                
        elif mode == 'train':
            # Training mode
            generated = self.generator(pose_images)
            results['generated'] = generated
            
            if target_images is not None:
                # Discriminator predictions
                real_pair = torch.cat([pose_images, target_images], dim=1)
                fake_pair = torch.cat([pose_images, generated], dim=1)
                
                real_pred = self.discriminator(real_pair)
                fake_pred = self.discriminator(fake_pair)
                
                # Calculate losses
                gen_loss = self._generator_loss(fake_pred, generated, target_images)
                disc_loss = self._discriminator_loss(real_pred, fake_pred)
                
                results['gen_loss'] = gen_loss
                results['disc_loss'] = disc_loss
                results['real_pred'] = real_pred
                results['fake_pred'] = fake_pred
        
        return results
    
    def _generator_loss(self, fake_pred: torch.Tensor, 
                       generated: torch.Tensor, 
                       target: torch.Tensor) -> torch.Tensor:
        """Calculate generator loss."""
        # Adversarial loss
        adversarial_loss = self.bce_loss(fake_pred, torch.ones_like(fake_pred))
        
        # L1 loss for pixel-wise accuracy
        l1_loss = self.l1_loss(generated, target)
        
        # Combined loss
        total_loss = adversarial_loss + 100 * l1_loss  # Lambda = 100 for L1
        
        return total_loss
    
    def _discriminator_loss(self, real_pred: torch.Tensor, 
                           fake_pred: torch.Tensor) -> torch.Tensor:
        """Calculate discriminator loss."""
        real_loss = self.bce_loss(real_pred, torch.ones_like(real_pred))
        fake_loss = self.bce_loss(fake_pred, torch.zeros_like(fake_pred))
        
        return (real_loss + fake_loss) * 0.5
    
    def apply_temporal_smoothing(self, sequence: torch.Tensor) -> torch.Tensor:
        """Apply temporal smoothing to a sequence of generated frames."""
        if not self.use_temporal_smoothing:
            return sequence[-1]  # Return last frame
        
        # Ensure sequence has correct length
        if sequence.shape[0] < self.temporal_smoother.sequence_length:
            # Pad with last frame
            padding = self.temporal_smoother.sequence_length - sequence.shape[0]
            last_frame = sequence[-1:].repeat(padding, 1, 1, 1)
            sequence = torch.cat([sequence, last_frame], dim=0)
        else:
            # Take last sequence_length frames
            sequence = sequence[-self.temporal_smoother.sequence_length:]
        
        # Add batch dimension
        sequence = sequence.unsqueeze(0)
        
        # Apply temporal smoothing
        smoothed = self.temporal_smoother(sequence)
        
        return smoothed.squeeze(0)
    
    def add_noise_to_latent(self, pose_images: torch.Tensor, 
                           noise_level: float = 0.1) -> torch.Tensor:
        """Add noise to latent representation for noise analysis."""
        # Add Gaussian noise to input
        noise = torch.randn_like(pose_images) * noise_level
        return pose_images + noise
    
    def get_latent_representation(self, pose_images: torch.Tensor) -> torch.Tensor:
        """Extract latent representation from pose images."""
        # Get features from encoder layers
        with torch.no_grad():
            e1 = self.generator.enc1(pose_images)
            e2 = self.generator.enc2(e1)
            e3 = self.generator.enc3(e2)
            e4 = self.generator.enc4(e3)
            e5 = self.generator.enc5(e4)
            e6 = self.generator.enc6(e5)
            e7 = self.generator.enc7(e6)
            e8 = self.generator.enc8(e7)
            bottleneck = self.generator.bottleneck(e8)
        
        return bottleneck


class PairedUnpairedTrainer:
    """Trainer for comparing paired vs unpaired training approaches."""
    
    def __init__(self, model: PoseAnimatorModel, device: str = 'cuda'):
        self.model = model
        self.device = device
        self.model.to(device)
        
    def train_paired(self, pose_images: torch.Tensor, 
                    target_images: torch.Tensor,
                    optimizer_gen: torch.optim.Adam,
                    optimizer_disc: torch.optim.Adam) -> Dict[str, float]:
        """Train with paired data (pose-image pairs)."""
        pose_images = pose_images.to(self.device)
        target_images = target_images.to(self.device)
        
        # Forward pass
        results = self.model(pose_images, target_images, mode='train')
        
        # Generator loss
        gen_loss = results['gen_loss']
        
        # Discriminator loss
        disc_loss = results['disc_loss']
        
        # Backward pass
        optimizer_gen.zero_grad()
        gen_loss.backward(retain_graph=True)
        optimizer_gen.step()
        
        optimizer_disc.zero_grad()
        disc_loss.backward()
        optimizer_disc.step()
        
        return {
            'gen_loss': gen_loss.item(),
            'disc_loss': disc_loss.item()
        }
    
    def train_unpaired(self, pose_images: torch.Tensor,
                      target_images: torch.Tensor,
                      optimizer_gen: torch.optim.Adam,
                      optimizer_disc: torch.optim.Adam) -> Dict[str, float]:
        """Train with unpaired data (cycle consistency loss)."""
        pose_images = pose_images.to(self.device)
        target_images = target_images.to(self.device)
        
        # Generate fake target from pose
        fake_target = self.model.generator(pose_images)
        
        # Generate fake pose from target (cycle consistency)
        fake_pose = self.model.generator(target_images)
        
        # Cycle consistency loss
        cycle_loss = self.model.l1_loss(fake_pose, pose_images)
        
        # Adversarial losses
        fake_pred = self.model.discriminator(torch.cat([pose_images, fake_target], dim=1))
        adv_loss = self.model.bce_loss(fake_pred, torch.ones_like(fake_pred))
        
        # Total generator loss
        gen_loss = adv_loss + 10 * cycle_loss  # Lambda = 10 for cycle consistency
        
        # Discriminator loss
        real_pred = self.model.discriminator(torch.cat([pose_images, target_images], dim=1))
        fake_pred = self.model.discriminator(torch.cat([pose_images, fake_target.detach()], dim=1))
        
        disc_loss = (self.model.bce_loss(real_pred, torch.ones_like(real_pred)) +
                    self.model.bce_loss(fake_pred, torch.zeros_like(fake_pred))) * 0.5
        
        # Backward pass
        optimizer_gen.zero_grad()
        gen_loss.backward(retain_graph=True)
        optimizer_gen.step()
        
        optimizer_disc.zero_grad()
        disc_loss.backward()
        optimizer_disc.step()
        
        return {
            'gen_loss': gen_loss.item(),
            'disc_loss': disc_loss.item(),
            'cycle_loss': cycle_loss.item()
        }
