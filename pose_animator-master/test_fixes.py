"""
Test script to verify all fixes are working.
"""

import torch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_loading():
    """Test if model loading works with the fixes."""
    print("Testing model loading...")
    
    try:
        # Test loading with weights_only=False
        if os.path.exists('dummy_model.pth'):
            checkpoint = torch.load('dummy_model.pth', map_location='cpu', weights_only=False)
            print("✓ Model loading with weights_only=False works")
            return True
        else:
            print("✗ Dummy model file not found")
            return False
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False

def test_pose_detector():
    """Test if pose detector works without the visibility error."""
    print("Testing pose detector...")
    
    try:
        from utils.pose_detector import PoseDetector
        detector = PoseDetector()
        print("✓ PoseDetector initialized successfully")
        detector.close()
        return True
    except Exception as e:
        print(f"✗ PoseDetector failed: {e}")
        return False

def test_simple_model():
    """Test simple model creation."""
    print("Testing simple model...")
    
    try:
        from models.pix2pix import PoseAnimatorModel
        model = PoseAnimatorModel()
        print("✓ PoseAnimatorModel created successfully")
        return True
    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("PoseAnimator Fix Verification")
    print("=" * 40)
    
    tests = [
        test_model_loading,
        test_pose_detector,
        test_simple_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All fixes are working!")
        print("\nYou can now run:")
        print("1. python simple_working_main.py (simple GUI)")
        print("2. python main.py (full GUI with fixes)")
    else:
        print("✗ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
