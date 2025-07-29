#!/bin/bash
# WiLoR Web API Launcher
# Runs the FastAPI server using j11n environment

echo "🚀 Starting WiLoR Hand Tracking Web API..."

# Check if partition is mounted
if [ ! -d "/mnt/nvme0n1p8/conda-envs" ]; then
    echo "❌ Large partition not mounted. Mounting..."
    sudo mount /dev/nvme0n1p8 /mnt/nvme0n1p8
fi

# Check environments exist
if [ ! -d "/mnt/nvme0n1p8/conda-envs/j11n" ]; then
    echo "❌ j11n environment not found!"
    exit 1
fi

if [ ! -d "/mnt/nvme0n1p8/conda-envs/hand-teleop" ]; then
    echo "❌ hand-teleop environment not found!"
    exit 1
fi

echo "✅ Both environments found"
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📱 Web interface will be available at http://localhost:8000"
echo ""
echo "For your Remix website integration:"
echo "  - API endpoints: http://localhost:8000/api/*" 
echo "  - CORS enabled for cross-origin requests"
echo "  - Ready for jonaspetersen.com integration"
echo ""

# Run the web API using j11n environment
/mnt/nvme0n1p8/conda-envs/j11n/bin/python web_api.py
