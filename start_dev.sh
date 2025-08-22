#!/bin/bash
# Hand Teleop System - Quick Start Script

echo "🚀 Hand Teleop System - Quick Start"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

echo "✅ Python 3 available"

# Check dependencies
echo "📦 Checking dependencies..."

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q fastapi uvicorn opencv-python-headless numpy mediapipe websockets pydantic

echo "🧪 Testing API..."
python3 -c "
import sys
sys.path.insert(0, 'backend')
from deploy_api import app
print('✅ API loaded successfully')

# Count routes
routes = [route.path for route in app.routes]
api_routes = [r for r in routes if r.startswith('/api/')]
print(f'✅ Found {len(api_routes)} API endpoints')

# Check required endpoints
required = ['/api/health', '/api/robots', '/api/config/robot', '/api/track']
missing = [r for r in required if r not in routes]
if not missing:
    print('✅ All required endpoints present')
else:
    print(f'❌ Missing: {missing}')
"

echo ""
echo "🌐 Starting development server..."
echo "   API docs: http://localhost:8000/docs"
echo "   Demo: http://localhost:8000/demo"
echo "   Health: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
cd backend && python3 -m uvicorn deploy_api:app --host 0.0.0.0 --port 8000 --reload
