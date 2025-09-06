# 🤖 Hand Teleop System

> **Production-ready real-time hand tracking and robot teleoperation system**

A robust, production-grade hand tracking and robot control system that enables intuitive teleoperation using computer vision, inverse kinematics, and WebSocket streaming. Built with FastAPI, MediaPipe/WiLoR integration, and Three.js visualization.

## ✨ Key Features

- **🎯 Real-time hand tracking** - MediaPipe & WiLoR integration with automatic fallback
- **🤖 Multi-robot support** - SO-101, SO-100, Koch arm, MOSS platform
- **📊 Performance monitoring** - Built-in metrics, health checks, and resource management
- **🌐 Production web API** - FastAPI with WebSocket real-time streaming
- **⚡ Robust error handling** - Graceful fallbacks and comprehensive diagnostics
- **🎮 Live demo interface** - Browser-based control with Three.js 3D visualization
- **🛡️ Resource management** - Production-grade CPU/memory optimization
- **🌍 Browser compatibility** - Chrome bug mitigation and Firefox optimization

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

```bash
# Single unified entry point with production defaults
python3 main.py                    # Quick start with resource management
python3 main.py --start            # API server only
python3 main.py --dev              # Development mode (backend + frontend)
python3 main.py --test             # Run comprehensive test suite
python3 main.py --validate         # Complete project validation
python3 main.py --info             # Show project information
```

### 3. Test the API
```bash
curl http://localhost:8000/api/health
```

## 🌐 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| **Firefox** | ✅ Recommended | Most stable, optimal performance |
| **Chrome** | ⚠️ Caution | May cause camera freezing (see recovery) |
| **Safari** | 🔬 Testing | Limited testing on macOS |
| **Edge** | 🔬 Testing | Chromium-based, similar to Chrome |

### Chrome Bug Recovery
Chrome's VideoCaptureService can cause system-wide camera freezing:

```bash
# Quick recovery for Chrome issues
./scripts/recovery/chrome_camera_recovery.sh

# Emergency system-wide recovery
./scripts/recovery/emergency_camera_recovery.sh
```

**Recommendation**: Use Firefox for production deployments and development.

## 📖 Documentation

- **[📖 Complete Documentation](DOCS.md)** - Comprehensive technical guide
- **[🚀 API Reference](DOCS.md#api-reference)** - All endpoints and examples
- **[🤖 Robot Support](DOCS.md#robot-support)** - Supported robots and setup
- **[🔧 Development Guide](DOCS.md#development)** - Contributing and extending

## 🎯 Demo

### Web Interface
1. Start the system: `python3 main.py --dev`
2. Open browser: `http://localhost:3000/web/web_interface.html`
3. Allow camera access and move your hand!

### SO-101 Robot Simulation
1. Start backend: `python3 main.py --start`
2. Open: `http://localhost:8000/so101-simulation`
3. Real-time 3D robot visualization with hand tracking

### React/Remix Integration
```bash
# Copy the ready-to-use React component
cp integrations/remix/remix-component.tsx app/components/HandTracking.tsx

# Use in your Remix app
import HandTracking from "~/components/HandTracking";
export default function Demo() { return <HandTracking />; }
```

### API Usage
```python
import requests
import base64

# Track hand pose
response = requests.post('http://localhost:8000/api/track', json={
    'image_data': base64_image_data,
    'robot_type': 'so101',
    'tracking_mode': 'wilor'
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

### Core Components

- **`backend/render_backend.py`** - FastAPI production server
- **`core/hand_pose/`** - Hand tracking estimators (MediaPipe, WiLoR)
- **`core/robot_control/`** - Robot kinematics and control
- **`frontend/web/`** - Web interfaces and 3D visualization
- **`tests/integration/`** - Comprehensive test suite

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python3 main.py --test

# Run specific test file
python3 tests/integration/test_comprehensive.py

# Validate complete project
python3 main.py --validate
```

**Current Test Status**: ✅ All 5/5 tests passing
- File Structure ✅
- Core Imports ✅  
- Backend Endpoints ✅
- Hand Pose Estimators ✅
- Robot Kinematics ✅

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Test** your changes: `python3 main.py --test`
4. **Commit** and **push**: `git commit -m "Add feature" && git push`
5. **Submit** a pull request

### Development Guidelines

- All code must pass the comprehensive test suite
- Follow the existing code style and architecture
- Add tests for new functionality
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) for hand tracking
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Three.js](https://threejs.org/) for 3D visualization
- [LeRobot](https://github.com/huggingface/lerobot) for robot learning inspiration

## 🔧 Troubleshooting

### Common Issues

1. **Backend won't start**: Check conda environment and dependencies
2. **Camera not working**: Ensure browser permissions and HTTPS in production
3. **Performance issues**: Use `python3 main.py --start` for production settings
4. **Tests failing**: Ensure backend is running and dependencies are installed

### Support

- Check the [DOCS.md](DOCS.md) for detailed troubleshooting
- Review [TESTING_GUIDE.md](TESTING_GUIDE.md) for test-specific issues
- Open an issue with detailed error logs and system information
