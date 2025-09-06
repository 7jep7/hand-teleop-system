# 🏗️ Project Structure

## Overview
The hand-teleop-system is organized into clear functional modules with browser compatibility safeguards and emergency recovery capabilities.

```
hand-teleop-system/
├── 📁 Core System
│   ├── main.py                    # 🚀 FastAPI application entry point
│   ├── health_check.py            # 🏥 System health monitoring
│   ├── core/                      # 🧠 Core functionality modules
│   │   ├── __init__.py
│   │   ├── resource_manager.py    # 💾 Resource management
│   │   ├── hand_pose/             # 👋 Hand tracking implementations
│   │   │   ├── factory.py         # 🏭 Hand pose estimator factory
│   │   │   ├── types.py           # 📝 Type definitions
│   │   │   └── estimators/        # 🔍 Various hand tracking methods
│   │   ├── robot_control/         # 🤖 Robot kinematics and control
│   │   │   ├── kinematics.py      # 🧮 Inverse kinematics solver
│   │   │   ├── gripper_pose*.py   # 🦾 Gripper control modules
│   │   │   ├── so101_simulation.py # 🎮 SO-101 robot simulation
│   │   │   └── urdf/              # 📐 Robot URDF files
│   │   └── tracking/              # 📊 Kalman filtering and tracking
│   │       ├── kalman_filter.py   # 🎯 State estimation
│   │       └── tracker.py         # 📍 Object tracking
│   └── backend/                   # 🖼️ 3D rendering backend
│       └── render_backend.py      # 🎨 Three.js integration
│
├── 🌐 Frontend (Browser-Safe)
│   ├── index.html                 # 🏠 Main production interface
│   ├── demos/                     # 🎮 Demo applications
│   │   ├── legacy_demo.html       # 📜 Original implementation
│   │   └── chrome_safe_demo.html  # 🛡️ Chrome-optimized version
│   ├── diagnostics/               # 🔧 Debugging and testing tools
│   │   ├── camera_diagnostic.html # 📹 Camera functionality testing
│   │   ├── camera_safe_mode.html  # 🛡️ Safe mode for testing
│   │   └── minimal_camera_test.html # ⚡ Minimal functionality test
│   └── web/                       # 🌍 Advanced web interfaces
│       └── web_interface.html     # 🎨 Three.js 3D visualization
│
├── 🛠️ Scripts & Utilities
│   ├── scripts/
│   │   ├── recovery/              # 🚨 Emergency recovery tools
│   │   │   ├── chrome_camera_recovery.sh   # 🔧 Chrome bug recovery
│   │   │   └── emergency_camera_recovery.sh # 🆘 System-wide recovery
│   │   ├── setup.sh               # ⚙️ Environment setup
│   │   ├── run_*.sh               # 🏃 Execution utilities
│   │   └── README.md              # 📖 Scripts documentation
│   ├── start_dev.sh               # 🚀 Development environment starter
│   └── start_local.sh             # 🏠 Local development starter
│
├── 📚 Documentation
│   ├── README.md                  # 🏠 Main project documentation
│   ├── BROWSER_COMPATIBILITY.md  # 🌍 Browser compatibility guide
│   ├── CAMERA_CORRUPTION_INCIDENT.md # 🚨 Bug incident report
│   ├── DOCS.md                    # 📖 Comprehensive documentation
│   └── docs/                      # 📁 Additional documentation
│       ├── DEVELOPMENT.md         # 👨‍💻 Development guide
│       └── WEB_INTEGRATION.md     # 🌐 Web integration guide
│
├── 🧪 Testing & Examples
│   ├── tests/                     # 🧪 Test suites
│   │   ├── __init__.py
│   │   ├── unit/                  # 🔬 Unit tests
│   │   │   └── __init__.py
│   │   └── integration/           # 🔗 Integration tests
│   │       ├── __init__.py
│   │       ├── test_comprehensive.py # 🎯 Full system tests
│   │       └── test_simple.py     # ⚡ Basic integration tests
│   ├── examples/                  # 💡 Example implementations
│   │   ├── mvp_test_fingertips.py # 👆 Fingertip tracking example
│   │   ├── websocket_bridge.py   # 🌉 WebSocket integration
│   │   └── wilor_gui_app.py       # 🖼️ WiLoR GUI application
│   ├── test_*.py                  # 🧪 Root-level test files
│   └── pytest.ini                # ⚙️ Test configuration
│
├── 🏗️ Infrastructure
│   ├── assets/                    # 📦 Static assets
│   │   ├── meshes/                # 🎨 3D model files
│   │   │   └── so101/             # 🤖 SO-101 robot meshes
│   │   └── samples/               # 📋 Sample data and configurations
│   ├── integrations/              # 🔗 Framework integrations
│   │   └── remix/                 # ⚛️ React/Remix components
│   │       ├── HandTeleopWidget.tsx # 🎮 Main widget component
│   │       └── README.md          # 📖 Integration guide
│   └── temp/                      # 🗑️ Temporary files
│       ├── *.backup               # 💾 Backup files
│       ├── test_*.jpg             # 🖼️ Test images
│       └── server.log             # 📝 Server logs
│
└── 🔧 Configuration
    ├── .gitignore                 # 🚫 Git ignore rules
    ├── .pre-commit-config.yaml    # 🔍 Code quality checks
    ├── pyproject.toml             # 🐍 Python project configuration
    ├── requirements.txt           # 📦 Python dependencies
    ├── requirements-deploy.txt    # 🚀 Deployment dependencies
    ├── environment.yml            # 🐍 Conda environment
    ├── package.json               # 📦 Node.js dependencies
    ├── Dockerfile                 # 🐳 Container configuration
    └── render.yaml                # ☁️ Deployment configuration
```

## 🔍 Module Descriptions

### Core System (`/core/`)
- **Hand Pose**: Multiple estimator implementations (MediaPipe, WiLoR) with factory pattern
- **Robot Control**: IK solvers, gripper control, and robot simulations
- **Tracking**: Kalman filtering for smooth motion tracking
- **Resource Manager**: Memory and CPU optimization

### Frontend (`/frontend/`)
- **Production Interface** (`index.html`): Browser-safe main interface
- **Demos**: Legacy and Chrome-optimized versions
- **Diagnostics**: Camera testing and debugging tools
- **Web**: Advanced 3D visualization interfaces

### Scripts (`/scripts/`)
- **Recovery**: Emergency scripts for browser/camera issues
- **Development**: Setup and execution utilities
- **Automation**: Deployment and testing scripts

### Documentation (`/docs/`)
- **User Guides**: Setup, usage, and troubleshooting
- **Developer Guides**: Architecture, contributing, and API reference
- **Incident Reports**: Browser compatibility issues and solutions

### Testing (`/tests/`)
- **Unit Tests**: Individual module testing
- **Integration Tests**: End-to-end system testing
- **Examples**: Reference implementations and demos

## 🛡️ Safety Features

### Browser Compatibility
- **Chrome Bug Mitigation**: Resource-safe processing, emergency recovery
- **Firefox Optimization**: Recommended platform with full feature support
- **Cross-browser Testing**: Comprehensive compatibility testing suite

### Resource Management
- **Memory Monitoring**: Real-time usage tracking and limits
- **CPU Optimization**: Multi-threading controls and performance tuning
- **Emergency Stop**: Immediate resource cleanup and system reset

### Error Handling
- **Graceful Degradation**: Fallback mechanisms for component failures
- **Comprehensive Logging**: Detailed error tracking and diagnostics
- **Recovery Scripts**: Automated recovery from common issues

## 🚀 Entry Points

### Development
```bash
./start_dev.sh              # Full development environment
python main.py --dev        # Backend + frontend development mode
python main.py --start      # Production backend only
```

### Testing
```bash
python main.py --test       # Complete test suite
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

### Diagnostics
```bash
python main.py --validate   # Project validation
open /diagnostics/camera_diagnostic.html  # Camera testing
./scripts/recovery/chrome_camera_recovery.sh  # Emergency recovery
```

## 📋 File Naming Conventions

- **`*.html`**: Frontend interfaces and demos
- **`*_test.py`**: Unit and integration tests
- **`*_demo.html`**: Demo applications
- **`*_diagnostic.html`**: Debugging tools
- **`*_recovery.sh`**: Emergency recovery scripts
- **`*.md`**: Documentation files
- **`requirements*.txt`**: Dependency specifications

---

**Key Design Principles:**
1. **Browser Safety First**: Chrome bug mitigation throughout
2. **Clear Separation**: Frontend, backend, diagnostics, and recovery
3. **Comprehensive Testing**: Unit, integration, and manual testing
4. **Documentation**: Every component documented with troubleshooting
5. **Emergency Recovery**: Always available fallback mechanisms
