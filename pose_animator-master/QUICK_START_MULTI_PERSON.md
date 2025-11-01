# Multi-Person Pose Detection - Quick Start

## What Changed?
The system now detects **ALL people** in the frame, not just one person!

## How It Works
1. Detects the first person in the frame
2. Masks out that person
3. Detects the next person
4. Repeats up to 10 times
5. Draws each person with a different color

## Colors for Different People
- Person 1: Green
- Person 2: Red  
- Person 3: Blue
- Person 4: Yellow
- Person 5: Magenta
- And so on...

## How to Run

### Option 1: Simple GUI (Recommended)
```bash
python simple_working_main.py
```
- Click "Start Camera"
- Multiple people will be detected automatically
- Each person gets their own colored skeleton

### Option 2: Quick Test
```bash
python test_multi_person.py
```
- Opens camera and shows multi-person detection
- Press 'q' to quit

## Key Features
✅ Detects multiple people in the same frame
✅ Each person gets a unique color
✅ Works with camera or video files
✅ Real-time processing
✅ Automatic pose animation for all detected people

## Files Modified
- `simple_working_main.py` - Main GUI with multi-person detection
- `utils/pose_detector.py` - Added multi-person detection methods
- `test_multi_person.py` - Quick test script

## Usage Tips
1. Stand 2-3 feet from the camera for best results
2. Ensure good lighting
3. Avoid overlapping bodies (may detect as one person)
4. The system can detect up to 10 people simultaneously

Enjoy detecting multiple people! 🎉

