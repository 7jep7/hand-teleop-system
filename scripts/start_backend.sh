#!/bin/bash

# Simple backend server launcher for hand-teleop-system
# This starts the backend with clean, minimal logging

cd "$(dirname "$0")"

echo "🚀 Starting Hand Tracking Backend..."
echo "📋 API: http://localhost:8000"
echo "🎯 Demo: http://localhost:8000/"
echo "🌐 Main Demo: http://localhost:8000/"
echo "📊 Health: http://localhost:8000/api/health"
echo ""

# Start with minimal logging - only show errors and startup
uvicorn backend.render_backend:app --host 0.0.0.0 --port 8000 --log-level warning --no-access-log
