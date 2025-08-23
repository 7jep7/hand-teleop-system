# 🤖 Hand Teleop System

> **Real-time hand tracking and robot teleoperation system**

A production-ready hand tracking and robot control system that enables intuitive teleoperation using computer vision, inverse kinematics, and WebSocket streaming.

## ✨ Key Features

- **🎯 Real-time hand tracking** - MediaPipe & WiLoR integration with fallback support
- **🤖 Multi-robot support** - SO-101, SO-100, Koch arm, MOSS platform
- **📊 Performance monitoring** - Built-in metrics and health checks  
- **🌐 Production web API** - FastAPI with WebSocket real-time streaming
- **⚡ Robust error handling** - Graceful fallbacks and detailed diagnostics
- **� Live demo interface** - Browser-based control with Three.js visualization

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and setup
git clone https://github.com/7jep7/hand-teleop-system.git
cd hand-teleop-system

# Install dependencies (conda recommended)
conda env create -f environment.yml
conda activate hand-teleop
```

### 2. Start System

**Quick start (recommended):**
```bash
# Single unified entry point with production defaults
python main.py                    # Quick start with resource management
```

**Other commands:**
```bash
python main.py --start            # API server only
python main.py --dev              # Development mode (backend + frontend)
python main.py --test             # Run test suite
python main.py --validate         # Complete project validation
python main.py --info             # Show project information
```

**Legacy commands (deprecated):**
```bash
# These still work but are being phased out
python3 manage.py start           # Use: python main.py --start
./scripts/run_web_api.sh          # Use: python main.py
```

### 3. Test the API
```bash
curl http://localhost:8000/api/health
```

## 📖 Documentation

- **[📖 Complete Documentation](DOCS.md)** - Comprehensive technical guide
- **[🚀 API Reference](DOCS.md#api-reference)** - All endpoints and examples
- **[🤖 Robot Support](DOCS.md#robot-support)** - Supported robots and setup
- **[🔧 Development Guide](DOCS.md#development)** - Contributing and extending

## 🎯 Demo

### Web Interface
1. Start the system: `python main.py --dev`
2. Open browser: `http://localhost:3000/web/web_interface.html`
3. Allow camera access and move your hand!

### API Usage
```python
import requests
import base64

# Track hand pose
response = requests.post('http://localhost:8000/api/track', json={
    'image': base64_image_data,
    'robot_type': 'SO-101'
})

result = response.json()
print(f"Robot joints: {result['robot_joints']}")
```

## 🏗️ Architecture

```
Frontend (Browser) ──► FastAPI Backend ──► Hand Tracking ──► Robot Control
     │                       │                   │               │
     │                       │                   ▼               ▼
     │                       │            [MediaPipe/WiLoR]  [Kinematics]
     │                       │                   │               │
     └───────────────────────┴───────────────────┴───────────────┘
                           WebSocket Real-time Stream
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Test** your changes: `python main.py --test`
4. **Commit** and **push**: `git commit -m "Add feature" && git push`
5. **Submit** a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) for hand tracking
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Three.js](https://threejs.org/) for 3D visualization
- [LeRobot](https://github.com/huggingface/lerobot) for robot learning inspiration

## 🛠️ Project Manager

Use the built-in project manager for easy development:

```bash
# Show available commands
python3 manage.py

# Clean project (remove cache, temp files)
python3 manage.py clean

# Validate project structure  
python3 manage.py check

# Start backend server
python3 manage.py start

# Run comprehensive tests
python3 manage.py test

# Run all tasks (recommended)
python3 manage.py all
```

## 📁 Project Structure

```
hand-teleop-system/
├── manage.py                  # 🎯 Project manager (start here!)
├── backend/
│   └── render_backend.py     # 🌐 Production FastAPI server
├── core/                     # 🔧 Core system modules
│   ├── hand_pose/           # 👋 Hand tracking (MediaPipe, WiLoR)
│   ├── robot_control/       # 🤖 Robot kinematics & control
│   └── tracking/            # 📊 Motion tracking & filtering
├── tests/                   # 🧪 Test suite
│   ├── integration/         # End-to-end API tests
│   └── unit/               # Component unit tests
├── frontend/               # 🎨 Web interface assets
├── docs/                   # 📚 Documentation
├── scripts/                # 🔧 Utility scripts
└── examples/               # 💡 Example applications
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
python3 manage.py test
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
POST /api/track           # Hand pose estimation
GET  /diagnostics         # Camera diagnostics
```

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- MediaPipe for real-time hand tracking
- WiLoR research team for precision hand pose estimation
- Open source robotics community
