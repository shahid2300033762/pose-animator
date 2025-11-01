"""
Camera helper utility to ensure robust camera initialization.
"""

import cv2
import time
import logging

def initialize_camera(preferred_index=0, max_retries=3, max_indices=3):
    """
    Initialize camera with robust error handling and multiple index attempts.
    
    Args:
        preferred_index: The preferred camera index to try first
        max_retries: Maximum number of retries per camera index
        max_indices: Maximum number of camera indices to try
        
    Returns:
        tuple: (cv2.VideoCapture object, working_index) or (None, None) if failed
    """
    # Try multiple camera indices
    for camera_index in range(max_indices):
        # Try the preferred index first
        idx = preferred_index if camera_index == 0 else camera_index
        
        # Try multiple times for each index (sometimes cameras need multiple attempts)
        for attempt in range(max_retries):
            try:
                print(f"Trying camera index {idx} (attempt {attempt+1}/{max_retries})...")
                
                # Initialize camera
                cap = cv2.VideoCapture(idx)
                
                # Check if opened successfully
                if not cap.isOpened():
                    print(f"Failed to open camera with index {idx}")
                    cap.release()
                    continue
                
                # Try to read a frame to confirm it's working
                ret, frame = cap.read()
                if not ret or frame is None:
                    print(f"Camera opened but failed to read frame from index {idx}")
                    cap.release()
                    continue
                
                # Success!
                print(f"Successfully connected to camera with index {idx}")
                return cap, idx
                
            except Exception as e:
                print(f"Error with camera index {idx}: {e}")
                try:
                    if 'cap' in locals() and cap is not None:
                        cap.release()
                except:
                    pass
                
                # Small delay before retry
                time.sleep(0.5)
    
    # If we get here, no camera worked
    print("No working camera found!")
    return None, None

def set_camera_properties(cap, width=640, height=480, fps=30):
    """Set common camera properties."""
    if cap is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Return actual properties (may differ from requested)
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        
        return actual_width, actual_height, actual_fps
    
    return None, None, None