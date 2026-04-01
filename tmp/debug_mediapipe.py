import sys
import os

try:
    import mediapipe as mp
    print(f"Mediapipe imported. Version: {getattr(mp, '__version__', 'unknown')}")
    print(f"Has solutions: {hasattr(mp, 'solutions')}")
    if hasattr(mp, 'solutions'):
        print(f"Solutions: {mp.solutions}")
    else:
        print("mp.solutions is MISSING after import mediapipe")
        print("Attempting to fix by: import mediapipe.python.solutions as solutions")
        import mediapipe.python.solutions as solutions
        print(f"Direct import solutions: {solutions}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
