# 🛠️ Development Guide

## Project Structure

```
hand-teleop-system/
├── 🔧 Core Backend
│   ├── main.py                    # FastAPI application entry point
│   ├── backend/render_backend.py  # 3D rendering and visualization
│   └── core/                      # Core modules
│       ├── hand_pose/             # Hand tracking implementations
│       ├── robot_control/         # Robot kinematics and control
│       └── tracking/              # Kalman filtering and tracking
│
├── 🌐 Frontend (Browser-Safe)
│   ├── index.html                 # Main production interface
│   ├── demos/                     # Demo applications
│   │   ├── legacy_demo.html       # Original implementation
│   │   └── chrome_safe_demo.html  # Chrome-optimized version
│   ├── diagnostics/               # Debugging tools
│   │   ├── camera_diagnostic.html # Camera testing
│   │   ├── camera_safe_mode.html  # Safe mode testing
│   │   └── minimal_camera_test.html # Basic functionality test
│   └── web/                       # Advanced interfaces
│       └── web_interface.html     # Three.js visualization
│
├── 🔧 Scripts & Utilities
│   ├── scripts/recovery/          # Emergency recovery tools
│   │   ├── chrome_camera_recovery.sh   # Chrome bug recovery
│   │   └── emergency_camera_recovery.sh # System-wide recovery
│   └── scripts/                   # Development utilities
│       ├── setup.sh               # Environment setup
│       └── run_*.sh               # Execution scripts
│
├── 📚 Documentation
│   ├── README.md                  # Main project documentation
│   ├── BROWSER_COMPATIBILITY.md  # Browser compatibility guide
│   ├── CAMERA_CORRUPTION_INCIDENT.md # Bug incident report
│   └── docs/                      # Additional documentation
│
└── 🧪 Testing
    ├── tests/                     # Test suites
    │   ├── unit/                  # Unit tests
    │   └── integration/           # Integration tests
    └── examples/                  # Example implementations
```

## 🚀 Development Workflow

### 1. Environment Setup

```bash
# Create conda environment
conda env create -f environment.yml
conda activate hand-teleop

# Verify installation
python -c "import cv2, mediapipe; print('✅ Dependencies OK')"
```

### 2. Development Server

```bash
# Start development environment
./start_dev.sh

# Or start components individually
python main.py --start          # Backend only
cd frontend && python -m http.server 3000  # Frontend only
```

### 3. Testing Strategy

```bash
# Full test suite
pytest

# Browser compatibility testing
# 1. Test in Firefox (recommended)
# 2. Test in Chrome with caution
# 3. Use diagnostic tools in /diagnostics/

# Camera safety testing
open http://localhost:8000/diagnostics/camera_safe_mode.html
```

## 🌍 Browser Compatibility Development

### Safe Development Practices

1. **Always test in Firefox first** - Most stable platform
2. **Chrome development requires caution** - Use recovery scripts
3. **Implement resource cleanup** - Prevent memory leaks
4. **Use diagnostic tools** - Monitor system health

### Chrome Bug Mitigation Code Patterns

```javascript
// ✅ Safe Resource Management
class SafeResourceManager {
    constructor() {
        this.resources = new Set();
        this.cleanup = new Set();
    }

    register(resource, cleanupFn) {
        this.resources.add(resource);
        this.cleanup.add(cleanupFn);
    }

    async safeCleanup() {
        for (const cleanupFn of this.cleanup) {
            try {
                await cleanupFn();
            } catch (error) {
                console.warn('Cleanup error:', error);
            }
        }
        this.resources.clear();
        this.cleanup.clear();
    }
}

// ✅ Browser Detection
function detectBrowser() {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Chrome') && !userAgent.includes('Edg')) {
        return 'chrome';
    } else if (userAgent.includes('Firefox')) {
        return 'firefox';
    }
    return 'unknown';
}

// ✅ Safe Canvas Operations (Chrome-compatible)
function safeCanvasOperation(video, callback) {
    try {
        // Use smaller canvas sizes for Chrome
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = 160;  // Reduced from 640
        tempCanvas.height = 120; // Reduced from 480
        
        const ctx = tempCanvas.getContext('2d');
        ctx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
        
        callback(tempCanvas);
    } catch (error) {
        console.warn('Canvas operation failed:', error);
        // Graceful degradation
    }
}

// ✅ Resource-Safe Frame Processing
function processFrame() {
    if (!this.isRunning) return;
    
    const startTime = performance.now();
    
    try {
        // Minimal processing to avoid Chrome deadlock
        safeCanvasOperation(this.video, (canvas) => {
            const imageData = canvas.toDataURL('image/jpeg', 0.7);
            this.sendToBackend(imageData);
        });
    } catch (error) {
        console.warn('Frame processing error:', error);
    }
    
    // Always schedule next frame safely
    if (this.isRunning) {
        requestAnimationFrame(() => this.processFrame());
    }
}
```

### Emergency Recovery Integration

```javascript
// ✅ Emergency Stop Implementation
async emergencyStop() {
    console.log('🚨 EMERGENCY STOP');
    this.isRunning = false;
    
    await this.resourceManager.safeCleanup();
    
    // Additional safety for Chrome
    setTimeout(() => {
        if (confirm('Emergency stop complete. Reload page for fresh start?')) {
            window.location.reload();
        }
    }, 1000);
}

// ✅ Page Unload Safety
window.addEventListener('beforeunload', () => {
    this.resourceManager.safeCleanup();
});
```

## 🔧 Backend Development

### Adding New Robot Support

1. **Create robot module**: `core/robot_control/new_robot.py`
2. **Implement IK solver**: Extend base kinematics
3. **Add URDF/mesh files**: Place in `assets/`
4. **Update visualization**: Add to Three.js renderer
5. **Write tests**: Add integration tests

### Hand Tracking Integration

1. **Estimator interface**: Implement in `core/hand_pose/estimators/`
2. **Factory pattern**: Register in `factory.py`
3. **Error handling**: Implement graceful fallbacks
4. **Performance**: Monitor processing times

### WebSocket API Extension

```python
# Add new endpoint to main.py
@app.websocket("/ws/new-feature")
async def new_feature_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process data
            await websocket.send_text(response)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
```

## 🧪 Testing Guidelines

### Unit Tests
```bash
# Test specific modules
pytest tests/unit/test_kinematics.py
pytest tests/unit/test_hand_pose.py

# Test coverage
pytest --cov=core tests/unit/
```

### Integration Tests
```bash
# Full system tests
pytest tests/integration/test_comprehensive.py

# Browser compatibility tests
pytest tests/integration/test_browser_compatibility.py
```

### Manual Testing Checklist

#### Camera Functionality
- [ ] Firefox: Camera starts/stops cleanly
- [ ] Chrome: Camera with recovery script ready
- [ ] Resource cleanup: No memory leaks
- [ ] Error handling: Graceful degradation

#### Robot Control
- [ ] Hand tracking accuracy
- [ ] IK solver performance
- [ ] WebSocket latency
- [ ] 3D visualization sync

#### Production Readiness
- [ ] Health checks respond
- [ ] Resource monitoring active
- [ ] Error logging comprehensive
- [ ] Recovery procedures documented

## 📦 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Resource limits set
- [ ] Browser compatibility warnings active
- [ ] Recovery scripts available
- [ ] Monitoring enabled
- [ ] Documentation updated

### Docker Deployment
```bash
# Build production image
docker build -t hand-teleop-system .

# Run with resource limits
docker run -p 8000:8000 \
  --memory=2g \
  --cpus=2 \
  hand-teleop-system
```

## 🚨 Troubleshooting

### Camera Issues
```bash
# Check system
./scripts/recovery/emergency_camera_recovery.sh

# Chrome-specific
./scripts/recovery/chrome_camera_recovery.sh

# Diagnostic mode
open http://localhost:8000/diagnostics/camera_diagnostic.html
```

### Performance Issues
1. **Monitor resource usage**: Check diagnostic panel
2. **Reduce frame rate**: Lower processing frequency
3. **Optimize canvas operations**: Use smaller sizes
4. **Switch browsers**: Try Firefox

### Development Issues
1. **Port conflicts**: Use `netstat -tulpn | grep :8000`
2. **Dependencies**: Verify conda environment
3. **CORS issues**: Check backend CORS settings
4. **WebSocket failures**: Verify firewall settings

## 📋 Contributing Guidelines

1. **Test browser compatibility** - Firefox and Chrome
2. **Implement safe resource management** - Always cleanup
3. **Add diagnostic capabilities** - Help future debugging
4. **Document browser-specific behavior** - Update compatibility guide
5. **Write integration tests** - Verify end-to-end functionality

### Code Review Checklist
- [ ] Resource cleanup implemented
- [ ] Browser detection included
- [ ] Error handling comprehensive
- [ ] Tests pass in Firefox
- [ ] Chrome compatibility tested with recovery ready
- [ ] Documentation updated
- [ ] No memory leaks detected

---

**Remember**: Browser compatibility is critical. Always test in Firefox first, then Chrome with recovery scripts ready.
