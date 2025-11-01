#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "================================================"
echo "  PoseAnimator.com Web Launcher"
echo "  AI-Powered Real-Time Animation Studio"
echo "================================================"
echo ""
echo "Starting web server on http://localhost:8000"
echo ""
echo -e "${BLUE}Opening browser...${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Try to open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8000 &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8000 &
fi

# Start the web server
python3 web_launcher.py


