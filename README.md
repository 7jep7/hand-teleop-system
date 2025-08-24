# 🤖 Hand Teleop System

> **Real-time hand tracking and robot teleoperation system**

A production-ready hand tracking and robot control system that enables intuitive teleoperation using computer vision, inverse kinematics, and WebSocket streaming.

## ✨ Key Features

- **🎯 Real-time hand tracking** - MediaPipe & WiLoR integration with fallback support
- **🤖 Multi-robot support** - SO-101, SO-100, Koch arm, MOSS platform
- **📊 Performance monitoring** - Built-in metrics and health checks  
- **🌐 Production web API** - FastAPI with WebSocket real-time streaming
- **⚡ Robust error handling** - Graceful fallbacks and detailed diagnostics
- **🎮 Live demo interface** - Browser-based control with Three.js visualization

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
python main.py                    # Quick start with resource management
python main.py --start            # API server only
python main.py --dev              # Development mode (backend + frontend)
python main.py --test             # Run test suite
python main.py --info             # Show project information
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
