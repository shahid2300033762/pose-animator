"""
Test script to verify PoseAnimator installation and dependencies.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
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
        import cv2
        print(f"+ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"- OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe
        print(f"+ MediaPipe {mediapipe.__version__}")
    except ImportError as e:
        print(f"- MediaPipe import failed: {e}")
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

def test_pose_detector():
    """Test pose detector initialization."""
    print("\nTesting pose detector...")
    
    try:
        from utils.pose_detector import PoseDetector
        detector = PoseDetector()
        print("+ PoseDetector initialized successfully")
        detector.close()
        return True
    except Exception as e:
        print(f"- PoseDetector initialization failed: {e}")
        return False

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

def test_camera():
    """Test camera access."""
    print("\nTesting camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("+ Camera accessible")
            cap.release()
            return True
        else:
            print("- Camera not accessible")
            return False
    except Exception as e:
        print(f"- Camera test failed: {e}")
        return False

def test_gpu():
    """Test GPU availability."""
    print("\nTesting GPU availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"+ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
            return True
        else:
            print("- CUDA not available, using CPU")
            return False
    except Exception as e:
        print(f"- GPU test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("PoseAnimator Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_pose_detector,
        test_model,
        test_camera,
        test_gpu
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("+ All tests passed! PoseAnimator is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python demo.py' to see the demo")
        print("2. Run 'python main.py' to start the GUI")
        print("3. Run 'python train.py --create_sample_data --data_path data' to create sample data")
        print("4. Run 'python train.py --data_path data --epochs 10' to train a model")
    else:
        print("- Some tests failed. Please check the error messages above.")
        print("\nTo install missing dependencies, run:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
