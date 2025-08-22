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

### 3. Test System
```bash
# Run comprehensive tests
python3 manage.py test

# Or run all checks
python3 manage.py all
```

### 4. Access Demo
Open your browser to: **http://localhost:8000/demo**

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
