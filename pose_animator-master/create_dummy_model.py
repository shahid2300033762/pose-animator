"""
Create a dummy model file for testing.
"""

import torch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.pix2pix import PoseAnimatorModel

def create_dummy_model():
    """Create a dummy model for testing."""
    print("Creating dummy model...")
    
    # Create model
    model = PoseAnimatorModel(use_temporal_smoothing=True)
    
    # Create dummy checkpoint
    checkpoint = {
        'epoch': 0,
        'model_state_dict': model.state_dict(),
        'optimizer_gen_state_dict': {},
        'optimizer_disc_state_dict': {},
        'best_val_loss': float('inf')
    }
    
    # Save model
    torch.save(checkpoint, 'dummy_model.pth')
    print("Dummy model saved as 'dummy_model.pth'")

if __name__ == "__main__":
    create_dummy_model()
