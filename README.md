# Hand Teleop - Hand-Controlled Robot Manipulation

A modern, web-based system for controlling robot manipulators through hand gestures using computer vision and machine learning.

## 🎯 Project Goal

Build a complete hand-controlled robot manipulation system where you can steer your SO-101 (or other robot manipulator) by simply moving your hand in front of a camera.

## 🏆 Current Status: WiLoR Hand Tracking Demo

The first milestone is complete: **Real-time hand pose estimation using WiLoR** with web interface integration.

## 🚀 Features

- **Real-time Hand Tracking**: 21-point hand pose estimation using WiLoR
- **Web Interface**: Live camera capture and overlay visualization  
- **REST API**: FastAPI backend for seamless integration
- **Remix Ready**: React component ready for jonaspetersen.com
- **Robot Support**: Kinematics and control for SO-101 and other manipulators

## 📁 Project Structure

```
hand-teleop/
├── 📖 docs/                    # Documentation
├── 🌐 frontend/               # Web interface components
│   ├── components/           # Remix/React components  
│   └── web/                 # Standalone web interface
├── ⚙️  backend/               # API and server code
├── 🔧 core/                  # Core modules
│   ├── hand_pose/          # Hand pose estimation
│   ├── robot_control/      # Robot manipulation & kinematics
│   └── tracking/           # Tracking algorithms
├── 🔨 scripts/              # Utility and setup scripts
├── 🧪 tests/                # Test files
├── 📋 examples/             # Example applications
└── 📦 assets/               # Static assets and sample data
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Run the setup script
./scripts/setup.sh
```

### 2. Start Web API
```bash
# Start the FastAPI backend
./scripts/run_web_api.sh
```

### 3. Access Web Interface
```bash
# Open browser to
http://localhost:8000
```

### 4. Try Desktop GUI (Optional)
```bash
# Run the desktop GUI example
./scripts/run_gui.sh
```

## 📚 Documentation

- [📋 Web Integration Guide](docs/WEB_INTEGRATION.md) - Complete guide for web integration
- [🤖 SO-101 Setup](docs/SO101_SETUP.md) - Robot-specific setup instructions
- [📖 Main Documentation](docs/README.md) - Detailed project documentation

## 🛠️ Development

### Core Modules
- **`core/hand_pose/`**: Hand tracking implementations (WiLoR, MediaPipe, AprilTag)
- **`core/robot_control/`**: Robot kinematics, control, and URDF support
- **`core/tracking/`**: Kalman filters and tracking utilities

### Frontend Components
- **`frontend/components/`**: Remix/React components for web integration
- **`frontend/web/`**: Standalone web interface

### Backend API
- **`backend/web_api.py`**: FastAPI server with hand processing endpoints

## 🎯 Roadmap

- [x] **Milestone 1**: WiLoR Hand Tracking Demo ✅
- [ ] **Milestone 2**: Hand-to-Robot Pose Mapping
- [ ] **Milestone 3**: Real-time Robot Control
- [ ] **Milestone 4**: Advanced Gestures & Commands
- [ ] **Milestone 5**: Multi-robot Support

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🤝 Contributing

This project is designed with a clean, modular structure to support future growth and collaboration.
