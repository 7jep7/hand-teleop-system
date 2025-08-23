# 📖 Hand Teleop System - Technical Documentation

## Table of Contents
- [🏗️ Architecture](#architecture)
- [🚀 API Reference](#api-reference)
- [🤖 Robot Support](#robot-support)
- [🎯 Hand Tracking](#hand-tracking)
- [🌐 Web Interface](#web-interface)
- [⚙️ Configuration](#configuration)
- [🔧 Development](#development)
- [🧪 Testing](#testing)

---

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │───►│   FastAPI Backend │───►│  Hand Tracking  │
│   (Browser/UI)  │    │   (render_backend) │    │   (MediaPipe)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Robot Control    │
                       │ (Kinematics)     │
                       └──────────────────┘
```

### Core Components
- **`main.py`** - Unified entry point with resource management
- **`backend/render_backend.py`** - FastAPI server with WebSocket support
- **`core/hand_pose/`** - Hand tracking implementations (MediaPipe, WiLoR)
- **`core/robot_control/`** - Inverse kinematics and robot models
- **`frontend/`** - Web interface with Three.js visualization

### Resource Management
Production-grade resource control is enabled by default:
- CPU limiting (70% of available cores)
- Memory limits (8GB virtual, 6GB physical)
- GPU allocation (CUDA device 0)
- Process priority control (nice +10)

---

## 🚀 API Reference

### Health Check
```http
GET /api/health
```
Returns system status and configuration.

### Hand Tracking
```http
POST /api/track
Content-Type: application/json

{
  "image": "base64_encoded_image",
  "robot_type": "SO-101"
}
```

Response:
```json
{
  "hand_pose": {...},
  "robot_joints": [...],
  "robot_pose": {...},
  "processing_time": 0.023,
  "timestamp": "2025-08-22T..."
}
```

### Robot Configuration
```http
GET /api/robots
POST /api/config/robot
```

### Real-time WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.send(JSON.stringify({
  type: 'track',
  image: base64Image,
  robot_type: 'SO-101'
}));
```

---

## 🤖 Robot Support

### Supported Robots
| Robot | Type | DOF | Status |
|-------|------|-----|--------|
| SO-101 | Articulated arm | 6 | ✅ Full support |
| SO-100 | Compact arm | 5 | ✅ Full support |
| Koch | Research platform | 7 | 🔄 Beta |
| MOSS | Mobile platform | Variable | 🔄 Experimental |

### URDF Integration
Robot models are loaded from `core/robot_control/urdf/` with automatic:
- Forward/inverse kinematics
- Joint limit enforcement
- Collision detection
- 3D visualization

### Custom Robot Setup
1. Add URDF file to `core/robot_control/urdf/`
2. Update `robot_types.py` with configuration
3. Test with `python main.py --test`

---

## 🎯 Hand Tracking

### Supported Backends

#### MediaPipe (Default)
- **Pros**: Fast, lightweight, CPU-only
- **Cons**: Less accurate for complex poses
- **Usage**: Automatic fallback, good for development

#### WiLoR (Recommended)
- **Pros**: High accuracy, robust hand tracking
- **Cons**: Requires GPU, larger model
- **Setup**: CUDA required, automatic detection

### Tracking Pipeline
1. **Image Processing**: Resize, normalize, format conversion
2. **Hand Detection**: Locate hands in frame
3. **Pose Estimation**: Extract 21 hand landmarks
4. **Filtering**: Kalman filter for smoothing
5. **Mapping**: Convert to robot joint angles

### Performance Optimization
- Multi-threading for parallel processing
- Frame skipping under high load
- Adaptive quality based on performance
- Memory pool for efficient allocation

---

## 🌐 Web Interface

### Features
- **Real-time 3D visualization** using Three.js
- **Live hand tracking** with WebSocket streaming
- **Robot control panel** with joint sliders
- **Performance metrics** and diagnostics
- **Camera settings** and calibration

### Files
- `frontend/web/web_interface.html` - Main interface
- `frontend/assets/urdf_loader.js` - 3D robot rendering
- `frontend/mvp-ui.js` - UI components

### Development Server
```bash
python main.py --dev  # Starts both backend and frontend
```

Access at: `http://localhost:3000/web/web_interface.html`

---

## ⚙️ Configuration

### Environment Variables
```bash
# Resource limits
OMP_NUM_THREADS=8
MKL_NUM_THREADS=8
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Hand tracking
HAND_TRACKING_MODEL=wilor  # or mediapipe
TRACKING_CONFIDENCE=0.7
SMOOTHING_FACTOR=0.8

# Robot settings
DEFAULT_ROBOT=SO-101
JOINT_LIMITS_ENABLED=true
```

### Runtime Configuration
```python
from core.hand_pose.factory import HandPoseFactory
from core.robot_control.kinematics import InverseKinematics

# Initialize with specific backend
tracker = HandPoseFactory.create('wilor')
robot = InverseKinematics('SO-101')
```

---

## 🔧 Development

### Setup
```bash
# Clone and setup
git clone https://github.com/7jep7/hand-teleop-system.git
cd hand-teleop-system

# Install dependencies
conda env create -f environment.yml
conda activate hand-teleop

# Quick start
python main.py
```

### Development Commands
```bash
python main.py --dev       # Development mode
python main.py --test      # Run tests
python main.py --clean     # Cleanup
python main.py --validate  # Full validation
```

### Code Structure
```
hand-teleop-system/
├── main.py                 # Unified entry point
├── backend/                # FastAPI server
├── core/                   # Core functionality
│   ├── hand_pose/         # Hand tracking
│   └── robot_control/     # Robot kinematics
├── frontend/              # Web interface
├── tests/                 # Test suite
└── requirements.txt       # Dependencies
```

### Adding New Features
1. **Hand tracking**: Extend `core/hand_pose/estimators/`
2. **Robot support**: Add to `core/robot_control/`
3. **API endpoints**: Modify `backend/render_backend.py`
4. **UI components**: Update `frontend/`

---

## 🧪 Testing

### Test Suite
```bash
python main.py --test                    # Full test suite
python tests/test_hand_tracking.py       # Hand tracking only
python tests/test_robot_control.py       # Robot control only
python tests/test_api.py                 # API endpoints
```

### Performance Testing
```bash
python tests/test_performance.py --duration 60  # 60-second stress test
```

### Integration Testing
The system includes comprehensive integration tests covering:
- End-to-end hand tracking pipeline
- API response validation
- WebSocket communication
- Resource management
- Error handling and recovery

### Manual Testing
1. **Camera test**: Verify webcam access and image quality
2. **Hand tracking**: Test with various hand poses and lighting
3. **Robot control**: Validate joint movements and limits
4. **Performance**: Monitor CPU/GPU usage and frame rates

---

## 🔍 Troubleshooting

### Common Issues

#### CUDA Not Available
```bash
# Check CUDA installation
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# Fallback to CPU
export CUDA_VISIBLE_DEVICES=""
```

#### Resource Limits
```bash
# Check current limits
ulimit -a

# Increase if needed (requires privileges)
sudo sysctl -w kernel.pid_max=4194304
```

#### Environment Issues
```bash
# Reset environment
conda env remove -n hand-teleop
conda env create -f environment.yml
```

### Performance Optimization
- Ensure conda environment is on fast storage (SSD)
- Use dedicated GPU for hand tracking
- Monitor resource usage with `python main.py --info`
- Adjust tracking quality based on hardware capabilities

---

## 📚 References

### Papers & Research
- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [WiLoR: End-to-end Learning of 3D Hand Pose](https://arxiv.org/abs/xxx)
- [Real-time Hand Tracking for Robot Control](https://docs.example.com)

### Dependencies
- **FastAPI**: Modern web framework for APIs
- **Three.js**: 3D graphics in the browser
- **OpenCV**: Computer vision operations
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing

### External Tools
- **conda**: Environment management
- **uvicorn**: ASGI server
- **pytest**: Testing framework
