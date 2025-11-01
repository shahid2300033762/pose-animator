"""
Simple demo script for PoseAnimator without camera dependencies.
Demonstrates the core functionality of the pose-to-animation transfer system.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.pix2pix import PoseAnimatorModel
from evaluation.metrics import PoseTransferMetrics


def create_sample_pose_image():
    """Create a sample pose image for demonstration."""
    # Create a simple stick figure pose
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    
    # This function is not used in the simple demo
    pass
    
    return img


def create_sample_pose_image_simple():
    """Create a sample pose image without OpenCV."""
    # Create a simple pose pattern using numpy
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    
    # Create a simple geometric pattern that represents a pose
    # Head (circle)
    y, x = np.ogrid[:256, :256]
    mask = (x - 128)**2 + (y - 50)**2 <= 15**2
    img[mask] = [255, 255, 255]
    
    # Body (vertical line)
    img[65:150, 125:131] = [255, 255, 255]
    
    # Arms (diagonal lines)
    for i in range(30):
        if 100 + i < 256 and 128 - i >= 0:
            img[100 + i, 128 - i] = [255, 255, 255]
        if 100 + i < 256 and 128 + i < 256:
            img[100 + i, 128 + i] = [255, 255, 255]
    
    # Legs (diagonal lines)
    for i in range(50):
        if 150 + i < 256 and 128 - i >= 0:
            img[150 + i, 128 - i] = [255, 255, 255]
        if 150 + i < 256 and 128 + i < 256:
            img[150 + i, 128 + i] = [255, 255, 255]
    
    return img


def demonstrate_pose_to_animation():
    """Demonstrate pose-to-animation transfer."""
    print("PoseAnimator Demonstration")
    print("=" * 40)
    
    # Initialize model
    print("Initializing PoseAnimator model...")
    model = PoseAnimatorModel(use_temporal_smoothing=True)
    model.eval()
    
    # Create sample pose image
    print("Creating sample pose image...")
    pose_image = create_sample_pose_image_simple()
    
    # Convert to tensor
    pose_tensor = torch.from_numpy(pose_image).float().permute(2, 0, 1).unsqueeze(0) / 255.0
    
    # Generate animation
    print("Generating animation...")
    with torch.no_grad():
        animation_tensor = model.generator(pose_tensor)
    
    # Convert back to image
    animation_image = animation_tensor.squeeze(0).permute(1, 2, 0).numpy()
    animation_image = (animation_image * 255).astype(np.uint8)
    
    # Display results
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    axes[0].imshow(pose_image)
    axes[0].set_title('Input Pose')
    axes[0].axis('off')
    
    axes[1].imshow(animation_image)
    axes[1].set_title('Generated Animation')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig('pose_animation_demo.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("Demo completed! Check 'pose_animation_demo.png' for results.")
    
    # Test evaluation metrics
    print("\nTesting evaluation metrics...")
    metrics = PoseTransferMetrics()
    
    # Create a dummy target image for comparison
    target_image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    
    quality_metrics = metrics.calculate_animation_quality(animation_image, target_image)
    print(f"Animation Quality Metrics:")
    print(f"  SSIM: {quality_metrics['ssim']:.4f}")
    print(f"  PSNR: {quality_metrics['psnr']:.2f} dB")
    print(f"  MSE: {quality_metrics['mse']:.6f}")
    
    # Test noise analysis
    print("\nTesting noise analysis...")
    noise_results = model.add_noise_to_latent(pose_tensor, noise_level=0.1)
    noisy_animation = model.generator(noise_results)
    noisy_image = noisy_animation.squeeze(0).permute(1, 2, 0).numpy()
    noisy_image = (noisy_image * 255).astype(np.uint8)
    
    print("Noise analysis completed!")
    
    return pose_image, animation_image, noisy_image


def demonstrate_training_setup():
    """Demonstrate training setup."""
    print("\nTraining Setup Demonstration")
    print("=" * 40)
    
    # Create sample data
    print("Creating sample training data...")
    os.makedirs('data/poses', exist_ok=True)
    os.makedirs('data/animations', exist_ok=True)
    
    for i in range(5):
        # Create sample pose
        pose = create_sample_pose_image_simple()
        
        # Create corresponding animation (simple transformation)
        animation = pose.copy()
        animation = np.roll(animation, 10, axis=1)  # Shift horizontally
        animation = np.roll(animation, 5, axis=0)   # Shift vertically
        
        # Add some color variation
        animation[:, :, 0] = np.clip(animation[:, :, 0] * 1.2, 0, 255)
        animation[:, :, 2] = np.clip(animation[:, :, 2] * 0.8, 0, 255)
        
        # Save images
        Image.fromarray(pose).save(f'data/poses/pose_{i:04d}.jpg')
        Image.fromarray(animation).save(f'data/animations/animation_{i:04d}.jpg')
    
    print("Sample data created in 'data/' directory")
    print("You can now run: python train.py --data_path data --epochs 10")


def main():
    """Main demonstration function."""
    print("Welcome to PoseAnimator!")
    print("This is a demonstration of the pose-to-animation transfer system.")
    print("Note: This demo works without camera/MediaPipe dependencies.\n")
    
    try:
        # Demonstrate pose-to-animation transfer
        pose_img, anim_img, noisy_img = demonstrate_pose_to_animation()
        
        # Demonstrate training setup
        demonstrate_training_setup()
        
        print("\n" + "=" * 40)
        print("Demonstration completed successfully!")
        print("\nNext steps:")
        print("1. Install OpenCV and MediaPipe for full functionality:")
        print("   pip install opencv-python mediapipe")
        print("2. Run the full demo: python demo.py")
        print("3. Run the GUI: python main.py")
        print("4. Train a model: python train.py --data_path data --epochs 10")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        print("Please check that all dependencies are installed correctly.")


if __name__ == "__main__":
    main()
