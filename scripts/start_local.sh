#!/bin/bash
# Local Test Server for Hand Teleop System API
# Quick development and testing setup

echo "🚀 Starting Hand Teleop System API (Local Development)"
echo "=================================================="

# Check Python version
python3 --version

# Check if we're in the right directory
if [ ! -f "backend/render_backend.py" ]; then
    echo "❌ Error: Please run this script from the hand-teleop-system root directory"
    exit 1
fi

echo "✅ Found render_backend.py"

# Install/check dependencies
echo "📦 Checking dependencies..."
python3 -c "
import sys
missing = []
try:
    import fastapi
    print('✅ FastAPI available')
except ImportError:
    missing.append('fastapi')

try:
    import uvicorn
    print('✅ Uvicorn available')
except ImportError:
    missing.append('uvicorn')

try:
    import cv2
    print('✅ OpenCV available')
except ImportError:
    missing.append('opencv-python')

try:
    import numpy
    print('✅ NumPy available')
except ImportError:
    missing.append('numpy')

try:
    import pydantic
    print('✅ Pydantic available')
except ImportError:
    missing.append('pydantic')

if missing:
    print(f'❌ Missing packages: {missing}')
    print('Install with: pip3 install ' + ' '.join(missing))
    sys.exit(1)
else:
    print('✅ All required packages available')
"

if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Install them first:"
    echo "pip3 install fastapi uvicorn opencv-python numpy pydantic websockets"
    exit 1
fi

echo ""
echo "🌐 Starting server on http://localhost:8000"
echo "📱 Demo interface will be at: http://localhost:8000/demo"
echo "🔗 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 backend/render_backend.py
