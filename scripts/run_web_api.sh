#!/bin/bash
# Professional WiLoR Web API Launcher with Resource Management

echo "� This script is deprecated. Use the unified entry point instead:"
echo "   python main.py                # Quick start with resource management"
echo "   python main.py --start        # API server only"
echo "   python main.py --dev          # Development mode"
echo ""
echo "⚠️  Continuing with legacy functionality for compatibility..."
echo ""

# Set resource limits to prevent system crashes
echo "�️  Setting system resource limits..."
ulimit -v 8388608    # Limit virtual memory to 8GB
ulimit -m 6291456    # Limit physical memory to 6GB

# Set CPU affinity to use only some cores (leave cores for system)
TOTAL_CORES=$(nproc)
USE_CORES=$((TOTAL_CORES * 70 / 100))  # Use 70% of available cores
echo "💻 Using $USE_CORES of $TOTAL_CORES CPU cores"

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

# Set environment variables for resource control
export OMP_NUM_THREADS=$USE_CORES
export MKL_NUM_THREADS=$USE_CORES
export CUDA_VISIBLE_DEVICES=0  # Use only first GPU if multiple available

# Set PyTorch memory management
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Set process priority to be nice to the system
export NICE_PRIORITY=10

echo "⚙️  Resource management configured:"
echo "   - Virtual memory: 8GB limit"
echo "   - Physical memory: 6GB limit" 
echo "   - CPU cores: $USE_CORES cores"
echo "   - GPU memory: Controlled allocation"
echo "   - Process priority: Nice +$NICE_PRIORITY"

echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📱 Web interface will be available at http://localhost:8000"
echo ""
echo "For your Remix website integration:"
echo "  - API endpoints: http://localhost:8000/api/*" 
echo "  - CORS enabled for cross-origin requests"
echo "  - Ready for jonaspetersen.com integration"
echo ""

# Navigate to project root and run with resource management
cd "$(dirname "$0")/.."

# Start server with resource management and nice priority
nice -n $NICE_PRIORITY /mnt/nvme0n1p8/conda-envs/j11n/bin/python -c "
import uvicorn
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Configure for safety
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

try:
    from render_backend import app
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
except KeyboardInterrupt:
    print('\\n🛑 Server stopped by user')
except Exception as e:
    print(f'❌ Server error: {e}')
    sys.exit(1)
"
