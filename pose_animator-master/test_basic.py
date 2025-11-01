"""
Basic test script for PoseAnimator without MediaPipe and OpenCV.
Tests the core functionality that can work without these dependencies.
"""

import sys
import os

def test_imports():
    """Test if core modules can be imported."""
    print("Testing core imports...")
    
    try:
        import torch
        print(f"+ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"- PyTorch import failed: {e}")
        return False
    
    try:
        import torchvision
        print(f"+ TorchVision {torchvision.__version__}")
    except ImportError as e:
        print(f"- TorchVision import failed: {e}")
        return False
    
    try:
        import numpy
        print(f"+ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"- NumPy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("+ Pillow")
    except ImportError as e:
        print(f"- Pillow import failed: {e}")
        return False
    
    try:
        import matplotlib
        print(f"+ Matplotlib {matplotlib.__version__}")
    except ImportError as e:
        print(f"- Matplotlib import failed: {e}")
        return False
    
    return True

def test_model():
    """Test model initialization."""
    print("\nTesting model...")
    
    try:
        from models.pix2pix import PoseAnimatorModel
        model = PoseAnimatorModel()
        print("+ PoseAnimatorModel initialized successfully")
        return True
    except Exception as e:
        print(f"- PoseAnimatorModel initialization failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without camera/pose detection."""
    print("\nTesting basic functionality...")
    
    try:
        import torch
        import numpy as np
        
        # Test tensor operations
        x = torch.randn(1, 3, 256, 256)
        print("+ Tensor operations work")
        
        # Test model forward pass
        from models.pix2pix import PoseAnimatorModel
        model = PoseAnimatorModel()
        model.eval()
        
        with torch.no_grad():
            output = model.generator(x)
            print("+ Model forward pass works")
        
        # Test evaluation metrics
        from evaluation.metrics import PoseTransferMetrics
        metrics = PoseTransferMetrics()
        print("+ Evaluation metrics initialized")
        
        return True
    except Exception as e:
        print(f"- Basic functionality test failed: {e}")
        return False

def main():
    """Run basic tests."""
    print("PoseAnimator Basic Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_model,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("+ Basic tests passed! Core functionality works.")
        print("\nNote: Full functionality requires MediaPipe and OpenCV.")
        print("For complete setup, install:")
        print("pip install opencv-python mediapipe")
        print("\nYou can still use the model training and evaluation features.")
    else:
        print("- Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
