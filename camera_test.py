"""
Simple camera test script to diagnose camera issues.
"""

import cv2
import time
import sys

def test_camera():
    """Test camera access with multiple indices."""
    print("Testing camera access...")
    
    # Try multiple camera indices
    for camera_index in range(3):  # Try indices 0, 1, 2
        print(f"\nTrying camera index: {camera_index}")
        try:
            # Open camera
            cap = cv2.VideoCapture(camera_index)
            
            # Check if opened successfully
            if not cap.isOpened():
                print(f"- Failed to open camera with index {camera_index}")
                continue
                
            # Try to read a frame
            ret, frame = cap.read()
            if not ret or frame is None:
                print(f"- Camera opened but failed to read frame from index {camera_index}")
                cap.release()
                continue
                
            # Success!
            print(f"+ Successfully accessed camera with index {camera_index}")
            print(f"+ Frame shape: {frame.shape}")
            
            # Display camera properties
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"+ Camera properties: {width}x{height} @ {fps}fps")
            
            # Try to display the frame
            try:
                window_name = f"Camera Test (Index {camera_index})"
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.imshow(window_name, frame)
                print("+ Displaying camera frame. Press any key to continue...")
                cv2.waitKey(3000)  # Wait for 3 seconds or key press
                cv2.destroyWindow(window_name)
            except Exception as e:
                print(f"- Display error: {e}")
            
            # Release camera
            cap.release()
            return camera_index  # Return working camera index
            
        except Exception as e:
            print(f"- Error with camera index {camera_index}: {e}")
            try:
                if 'cap' in locals() and cap is not None:
                    cap.release()
            except:
                pass
    
    # If we get here, no camera worked
    print("\nNo working camera found!")
    return None

if __name__ == "__main__":
    working_index = test_camera()
    
    if working_index is not None:
        print(f"\nSUCCESS: Working camera found at index {working_index}")
        print(f"Use this index in your application.")
    else:
        print("\nFAILURE: No working camera found. Check your camera connections and permissions.")
        
    # Wait before exit
    print("\nTest complete. Press Enter to exit...")
    input()