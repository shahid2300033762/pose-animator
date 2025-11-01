# PoseAnimator - Real-Time Pose-to-Animation Transfer

A real-time system that translates human poses captured via camera into cartoon animations using Pix2Pix architecture.

## Features

- Real-time pose detection using MediaPipe
- Pix2Pix-based pose-to-animation transfer
- Temporal smoothness for fast movements
- Key joint transfer accuracy evaluation
- Latent vector noise analysis
- Paired vs unpaired training comparison

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Real-time Animation
```bash
python main.py --mode realtime
```

### Training
```bash
python train.py --data_path /path/to/dataset --epochs 100
```

### Evaluation
```bash
python evaluate.py --model_path /path/to/model --test_data /path/to/test
```

## Research Questions Addressed

1. **Key Joint Transfer Accuracy**: Evaluation metrics for pose-to-animation fidelity
2. **Latent Vector Noise Effect**: Analysis of noise impact on animation quality
3. **Paired vs Unpaired Training**: Comparison of training methodologies
4. **Temporal Smoothness**: Investigation of fast movement handling

## Project Structure

```
pose-animator/
├── models/           # Neural network architectures
├── data/            # Data processing and augmentation
├── utils/           # Utility functions
├── evaluation/      # Evaluation metrics and analysis
├── training/        # Training scripts
├── main.py         # Main application
├── train.py        # Training script
└── evaluate.py     # Evaluation script
```
