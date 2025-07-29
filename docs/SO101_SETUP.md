# SO-101 Hand Teleoperation Setup Guide

## Quick Start with Conda

### 1. Create and Setup Environment
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (creates conda env and installs dependencies)
./setup.sh
```

### 2. Activate Environment
```bash
conda activate hand-teleop
```

### 3. Test Your Setup

#### Basic Pose Tracking Test
```bash
# Test pose tracking only (no kinematics)
python test_so101.py --pose-only

# Test with different models
python test_so101.py --model wilor --pose-only
python test_so101.py --model mediapipe --pose-only
```

#### Full Joint Control Test
```bash
# Test with SO-101 kinematics (requires successful pose tracking first)
python test_so101.py

# With debug output
python test_so101.py --debug

# Test with scroll wheel gripper control
python test_so101.py --use-scroll
```

#### Alternative: Use main.py (now defaults to SO-101)
```bash
# Basic test
python main.py --model wilor

# With different options
python main.py --model wilor --fps 30 --use-scroll --cam-idx 0
```

## Manual Conda Setup (if setup.sh fails)

```bash
# Create environment
conda create -n hand-teleop python=3.10 -y

# Activate
conda activate hand-teleop

# Install conda packages
conda install -c conda-forge ffmpeg numpy opencv matplotlib scipy pynput pinocchio -y

# Install pip packages
pip install pydantic<2.0
pip install git+https://github.com/Joeclinton1/WiLoR-mini
pip install pupil-apriltags mediapipe

# Install hand-teleop in development mode
pip install -e .
```

## Testing Your Setup

### Step 1: Check Dependencies
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
python -c "import numpy as np; print(f'NumPy version: {np.__version__}')"
```

### Step 2: Test Camera
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print(f'Camera working: {cap.isOpened()}')"
```

### Step 3: Test Hand Tracking Models

#### Wilor (Recommended - GPU required)
```bash
python test_so101.py --model wilor --pose-only
```

#### MediaPipe (CPU-friendly, experimental)
```bash
python test_so101.py --model mediapipe --pose-only
```

### Step 4: Test SO-101 Kinematics
```bash
python test_so101.py --model wilor
```

## Controls

- `p` - Pause/resume tracking
- `space` - Hold to realign/reset pose
- `k` - Toggle keypoints-only visualization
- `scroll wheel` - Control gripper (if `--use-scroll` enabled)
- `Ctrl+C` - Exit

## Configuration

### SO-101 Safe Ranges
Edit `SO101_SAFE_RANGE` in `test_so101.py` to match your robot's workspace:

```python
SO101_SAFE_RANGE = {
    "x": (0.10, 0.40),    # Forward/backward reach
    "y": (-0.25, 0.25),   # Left/right reach  
    "z": (0.005, 0.30),   # Up/down reach
    "g": (0, 90),         # Gripper opening (degrees)
}
```

### Camera and Tracking Parameters
- `--cam-idx`: Change camera (0, 1, 2, ...)
- `--fps`: Target framerate (30, 60)
- `--hand`: Track left or right hand
- `--debug`: Enable debug output

## Troubleshooting

### Common Issues

1. **CUDA not available**: Wilor requires GPU with CUDA
   - Solution: Use `--model mediapipe` or install proper CUDA drivers

2. **Camera not working**: Check camera permissions and index
   - Solution: Try different `--cam-idx` values (0, 1, 2, ...)

3. **Hand not detected**: Poor lighting or hand position
   - Solution: Ensure good lighting and hand visible to camera

4. **Jerky motion**: Tracking unstable
   - Solution: Adjust Kalman filter parameters or use `--fps 30`

5. **Joint limits exceeded**: Robot trying to reach impossible position
   - Solution: Adjust `SO101_SAFE_RANGE` values

### Debug Mode
Enable debug mode to see detailed tracking information:
```bash
python test_so101.py --debug
```

## Next Steps

1. **Test with your actual SO-101 robot** - integrate with your robot control system
2. **Tune parameters** - adjust safe ranges and tracking parameters for your setup
3. **LeRobot integration** - follow the main README for LeRobot fork setup
4. **Custom calibration** - calibrate camera intrinsics for better accuracy

## File Structure
```
hand-teleop/
├── environment.yml          # Conda environment definition
├── setup.sh                # Automated setup script
├── test_so101.py           # SO-101 specific test script
├── main.py                 # Updated to use SO-101 by default
└── hand_teleop/
    ├── kinematics/urdf/so101.urdf  # SO-101 robot model
    └── ...
```
