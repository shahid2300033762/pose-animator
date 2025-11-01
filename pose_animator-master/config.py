"""
Configuration file for PoseAnimator.
Contains default settings and hyperparameters.
"""

import os

# Model configuration
MODEL_CONFIG = {
    'input_channels': 3,
    'output_channels': 3,
    'ngf': 64,  # Number of generator filters
    'ndf': 64,  # Number of discriminator filters
    'use_temporal_smoothing': True,
    'temporal_buffer_size': 5,
    'hidden_dim': 64
}

# Training configuration
TRAINING_CONFIG = {
    'batch_size': 8,
    'learning_rate_gen': 0.0002,
    'learning_rate_disc': 0.0002,
    'beta1': 0.5,
    'beta2': 0.999,
    'epochs': 100,
    'save_interval': 10,
    'l1_lambda': 100,  # L1 loss weight
    'cycle_lambda': 10,  # Cycle consistency loss weight
}

# Pose detection configuration
POSE_CONFIG = {
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.7,
    'model_complexity': 1,
    'input_size': (256, 256),
    'output_size': (512, 512)
}

# Evaluation configuration
EVALUATION_CONFIG = {
    'key_joint_threshold': 0.1,  # 10% of image size
    'noise_levels': [0.0, 0.1, 0.2, 0.3, 0.5],
    'temporal_sequence_length': 10,
    'metrics_weights': {
        'key_joint_accuracy': 0.3,
        'temporal_smoothness': 0.25,
        'ssim': 0.25,
        'edge_preservation': 0.2
    }
}

# Data configuration
DATA_CONFIG = {
    'pose_dir': 'poses',
    'animation_dir': 'animations',
    'supported_formats': ['.jpg', '.jpeg', '.png'],
    'image_size': (256, 256),
    'train_split': 0.8,
    'val_split': 0.2
}

# Paths
PATHS = {
    'data_dir': 'data',
    'models_dir': 'models',
    'logs_dir': 'logs',
    'results_dir': 'results',
    'checkpoints_dir': 'checkpoints'
}

# Create directories if they don't exist
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)

# Device configuration
DEVICE_CONFIG = {
    'auto_detect': True,
    'preferred_device': 'cuda',
    'fallback_device': 'cpu'
}

# GUI configuration
GUI_CONFIG = {
    'window_size': (1200, 800),
    'update_interval': 33,  # ~30 FPS
    'display_size': (600, 400),
    'theme': 'default'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'pose_animator.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}
