# 🤖 Hand Teleop System

> **Self-contained hand tracking system for robot teleoperation**

A real-time hand tracking and robot control system that enables intuitive teleoperation using computer vision and inverse kinematics.

## ✨ Features

- **🎯 Real-time fingertip tracking** - MediaPipe & WiLoR integration
- **🤖 Robot kinematics** - Inverse kinematics for multiple robot arms  
- **📊 Kalman filtering** - Smooth motion tracking and prediction
- **🌐 Web interface** - Browser-based control with live camera feed
- **⚡ FastAPI backend** - RESTful API for integration
- **🎮 Multiple estimators** - MediaPipe, WiLoR, AprilTag support

## 🚀 Quick Start

### Web Interface
```bash
# Start the web API server
python main.py web
# Open browser to http://localhost:8000
```

### Desktop GUI
```bash
python main.py gui
```

### Test Hand Tracking
```bash
python main.py test
```

## 📁 Project Structure

```
hand-teleop-system/
├── core/                      # Core system modules
│   ├── hand_pose/            # Hand tracking estimators
│   ├── robot_control/        # Robot kinematics & control  
│   └── tracking/             # Motion tracking & filtering
├── backend/                   # Web API server
├── frontend/                  # Web interface
├── integrations/              # External integrations (React/Remix)
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
└── examples/                  # Example applications
```

## �️ Installation

```bash
# Install with Poetry (recommended)
poetry install

# Or with pip
pip install -e .

# Install optional features
pip install -e ".[wilor,mediapipe]"
```

## 🧪 Testing

```bash
# Run all tests
python main.py test
pytest tests/

# Run specific test
pytest tests/test_mvp_fingertips.py -v
```

## 🔧 Configuration

### Supported Robots
- **SO-101** - 6-DOF manipulator
- **Koch** - Bimanual system  
- **MOSS** - Research platform

### Hand Pose Estimators
- **MediaPipe** - Fast, lightweight (default)
- **WiLoR** - High precision research model
- **AprilTag** - Marker-based tracking

## 📚 Documentation

- [Web Integration](docs/WEB_INTEGRATION.md) - Browser integration guide
- [Robot Setup](docs/SO101_SETUP.md) - Hardware configuration  
- [API Reference](docs/README.md) - Detailed API documentation

## � Integration

### React/Remix Components
```typescript
// Available in integrations/remix/
import HandTeleopWidget from './integrations/remix/HandTeleopWidget'
```

### API Endpoints
```bash
GET  /                    # Web interface
GET  /health              # Health check  
POST /api/process-hand    # Hand pose estimation
GET  /diagnostics         # Camera diagnostics
```

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- MediaPipe for real-time hand tracking
- WiLoR research team for precision hand pose estimation
- Open source robotics community
