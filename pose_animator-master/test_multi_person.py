"""
Quick test script for multi-person pose detection.
"""

import cv2
import numpy as np

# Import from simple_working_main
from simple_working_main import PoseDetector

def test_multi_person_detection():
    """Test multi-person pose detection."""
    print("Testing multi-person pose detection...")
    
    # Initialize detector
    detector = PoseDetector()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("Camera opened. Detecting multiple people...")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Resize frame
            frame = cv2.resize(frame, (640, 480))
            
            # Detect multiple poses
            pose_image, all_poses = detector.detect_multiple_poses(frame)
            
            # Show number of detected people
            if all_poses:
                cv2.putText(pose_image, f"{len(all_poses)} Person(s) Detected", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display
            cv2.imshow('Multi-Person Pose Detection', pose_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        detector.close()
        cv2.destroyAllWindows()
    
    print("Test complete!")

if __name__ == "__main__":
    test_multi_person_detection()

