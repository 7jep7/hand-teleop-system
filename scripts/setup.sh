#!/bin/bash
# Setup script for hand-teleop with conda environment

set -e

echo "🚀 Setting up hand-teleop for SO-101 robot..."

# Create conda environment
echo "📦 Creating conda environment..."
conda env create -f environment.yml

# Activate environment
echo "🔄 Activating environment..."
conda activate hand-teleop

# Install the package in development mode
echo "📋 Installing hand-teleop in development mode..."
pip install -e .

# Check if CUDA is available for Wilor
echo "🔍 Checking CUDA availability..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" || echo "⚠️  PyTorch not found, Wilor may not work properly"

echo "✅ Installation complete!"
echo ""
echo "🚀 Quick start:"
echo "  python main.py                # Quick start"
echo "  python main.py --test         # Run tests"
