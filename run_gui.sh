#!/bin/bash
# WiLoR GUI App Launcher
# Ensures conda environment is activated and runs the GUI

echo "🚀 Starting WiLoR Hand Tracking GUI App..."

# Check if partition is mounted
if [ ! -d "/mnt/nvme0n1p8/conda-envs" ]; then
    echo "❌ Large partition not mounted. Mounting..."
    sudo mount /dev/nvme0n1p8 /mnt/nvme0n1p8
fi

# Activate conda environment and run GUI
export PATH="/mnt/nvme0n1p8/conda-envs/hand-teleop/bin:$PATH"
export CONDA_DEFAULT_ENV="hand-teleop"

echo "✅ Environment activated"
echo "📹 Starting GUI app (this may take a moment)..."

# Run the GUI app
/mnt/nvme0n1p8/conda-envs/hand-teleop/bin/python wilor_gui_app.py
