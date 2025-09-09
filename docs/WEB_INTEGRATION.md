# Hand Teleop System - Web Integration Guide

## Current Architecture Overview

```
┌─────────────────────┐    ┌──────────────────────────┐
│  jonaspetersen.com  │    │   Hand Tracking API      │
│   (Production)      │    │  (FastAPI/Render.com)    │
│                     │    │                          │
│ • Hand cursor       │◄──►│ • Real-time tracking     │
│ • Gesture control   │    │ • MediaPipe processing   │
│ • Portfolio nav     │    │ • Fingertip detection    │
│ • Interactive UI    │    │ • WebSocket streaming    │
└─────────────────────┘    └──────────────────────────┘
         │                            │
         │                            │
         v                            v
┌─────────────────────┐    ┌──────────────────────────┐
│   Testing Demo      │    │   Local Development      │
│ (Backend Static)    │    │   (Conda Environment)    │
│                     │    │                          │
│ • WebSocket test    │    │ • Backend debugging      │
│ • Connection debug  │    │ • Dual backend testing   │
│ • Validation tools  │    │ • Development workflow   │
└─────────────────────┘    └──────────────────────────┘
```

## API Reference

### Production Backend: `https://hand-teleop-api.onrender.com`

#### **Core System Endpoints**
```
GET  /                       # Main demo interface
GET  /api/health            # System health & OpenCV status  
GET  /docs                  # Interactive API documentation (Swagger UI)
GET  /demo.html            # Main dual-camera demo interface
GET  /api/deployment-info   # Git commit & deployment details
GET  /api/performance      # System performance statistics
```

#### **Hand Tracking API**
```
POST /api/track             # Single-frame hand tracking
WebSocket: /api/tracking/live   # Real-time hand tracking stream
```

#### **Robot Control API**
```
GET  /api/robots            # List available robot types
POST /api/config/robot      # Configure robot settings
GET  /api/robot/so101/info  # SO-101 robot information
GET  /api/robot/so101/state # Current SO-101 joint state
POST /api/robot/so101/joints # Set SO-101 joint positions
GET  /api/assets/robot/so101/{file} # Robot asset files (URDF, STL)
WebSocket: /api/robot/so101/simulation # Real-time SO-101 control
```

#### **Calibration & Utilities**
```
POST /api/calibration/start # Start camera calibration
```

## WebSocket Protocol Implementation

### Connection Setup
```javascript
// Production integration for jonaspetersen.com
const ws = new WebSocket('wss://hand-teleop-api.onrender.com/api/tracking/live');

ws.onopen = () => {
    console.log('✅ Hand tracking connected');
};

ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};
```

### Data Exchange Protocol

#### **Send Format (Client → Server)**
```javascript
// Send camera frame for processing
const message = {
    "type": "image",
    "data": "data:image/jpeg;base64,/9j/4AAQ...", // Base64 encoded frame
    "tracking_mode": "mediapipe",
    "timestamp": new Date().toISOString()
};

ws.send(JSON.stringify(message));
```

#### **Receive Format (Server → Client)**
```javascript
{
    "type": "tracking_result",
    "data": {
        "success": true,
        "hand_detected": true,
        "fingertip_coords": {
            "thumb_tip": { "x": 0.324, "y": 0.456, "z": 0.123 },
            "index_tip": { "x": 0.567, "y": 0.234, "z": 0.089 },
            "index_pip": { "x": 0.543, "y": 0.267, "z": 0.098 },
            "index_mcp": { "x": 0.521, "y": 0.298, "z": 0.107 }
        },
        "processing_time_ms": 42,
        "tracking_mode": "mediapipe",
        "timestamp": "2025-09-02T15:30:45.123Z",
        "message": "Hand tracking completed"
    }
}
```

## REST API Implementation

### **Single-Frame Hand Tracking**

For scenarios where real-time WebSocket streaming isn't needed, you can use the REST API for single-frame processing.

#### **POST /api/track**

**Request Format:**
```javascript
const response = await fetch('https://hand-teleop-api.onrender.com/api/track', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        image_data: base64ImageData,  // Base64 encoded JPEG
        robot_type: "so101",          // Optional: robot type
        tracking_mode: "wilor"        // Optional: "wilor" or "mediapipe"
    })
});

const result = await response.json();
```

**Response Format:**
```json
{
    "success": true,
    "timestamp": "2025-09-02T15:30:45.123Z",
    "hand_detected": true,
    "hand_pose": {
        "fingertip_coords": {
            "thumb_tip": { "x": 0.324, "y": 0.456, "z": 0.123 },
            "index_tip": { "x": 0.567, "y": 0.234, "z": 0.089 },
            "index_pip": { "x": 0.543, "y": 0.267, "z": 0.098 },
            "index_mcp": { "x": 0.521, "y": 0.298, "z": 0.107 }
        },
        "gripper_state": "open",
        "confidence": 0.95
    },
    "robot_joints": [0.1, -0.2, 0.3, 0.0, 0.5, -0.1],
    "robot_pose": {
        "position": {"x": 0.5, "y": 0.3, "z": 0.8},
        "orientation": {"x": 0, "y": 0, "z": 0, "w": 1}
    },
    "processing_time_ms": 42.5,
    "message": "Hand tracking completed successfully"
}
```

### **System Health & Status**

#### **GET /api/health**

Monitor system status and dependencies:

```javascript
const health = await fetch('https://hand-teleop-api.onrender.com/api/health');
const status = await health.json();

// Response example:
{
    "status": "healthy",
    "timestamp": "2025-09-02T15:30:45.123Z",
    "version": "1.0.1",
    "git_commit": "abc123def456",
    "dependencies": {
        "opencv": "status: working",
        "numpy": "1.24.3",
        "fastapi": "0.104.1",
        "torch": "2.1.0",
        "mediapipe": "0.10.7"
    }
}
```

#### **GET /api/performance**

Get system performance metrics:

```javascript
const perf = await fetch('https://hand-teleop-api.onrender.com/api/performance');
const metrics = await perf.json();

// Response example:
{
    "stats": {
        "total_requests": 1543,
        "successful_requests": 1521,
        "failed_requests": 22,
        "average_processing_time_ms": 38.2,
        "frames_processed": 15430
    },
    "system_info": {
        "uptime_seconds": 86400,
        "current_connections": 3,
        "robot_config": {
            "robot_type": "so101",
            "settings": {"tracking_mode": "wilor"}
        }
    },
    "timestamp": "2025-09-02T15:30:45.123Z"
}
```

### **Robot Control API**

#### **GET /api/robots**

List available robot types:

```javascript
const robots = await fetch('https://hand-teleop-api.onrender.com/api/robots');
const robotList = await robots.json();

// Response example:
{
    "robots": [
        {
            "id": "so101",
            "name": "SO-101 Gripper",
            "description": "6-DOF robotic gripper with parallel jaws"
        }
    ],
    "current_robot": "so101",
    "total_count": 1
}
```

#### **POST /api/config/robot**

Configure robot settings:

```javascript
const config = await fetch('https://hand-teleop-api.onrender.com/api/config/robot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        robot_type: "so101",
        settings: {
            tracking_mode: "mediapipe",
            smoothing_factor: 0.8
        }
    })
});

const result = await config.json();
// Response: { "success": true, "message": "Robot configured to so101", ... }
```

#### **SO-101 Specific Endpoints**

**GET /api/robot/so101/info** - Robot specifications:
```json
{
    "success": true,
    "robot_info": {
        "name": "SO-101",
        "dof": 6,
        "max_reach": 0.8,
        "joint_limits": [
            {"min": -1.57, "max": 1.57},
            {"min": -1.57, "max": 1.57}
        ]
    },
    "timestamp": "2025-09-02T15:30:45.123Z"
}
```

**GET /api/robot/so101/state** - Current joint positions:
```json
{
    "success": true,
    "joint_state": {
        "positions": [0.1, -0.2, 0.3, 0.0, 0.5, -0.1],
        "velocities": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "effort": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    },
    "timestamp": "2025-09-02T15:30:45.123Z"
}
```

**POST /api/robot/so101/joints** - Set joint positions:
```javascript
const move = await fetch('https://hand-teleop-api.onrender.com/api/robot/so101/joints', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        positions: [0.2, -0.3, 0.4, 0.1, 0.6, -0.2],
        smooth: true  // Optional: smooth motion
    })
});
```

### **Asset Serving**

#### **GET /api/assets/robot/so101/{file_path}**

Serve robot assets (URDF, STL, textures):

```javascript
// Example: Get robot URDF file
const urdfUrl = 'https://hand-teleop-api.onrender.com/api/assets/robot/so101/robot.urdf';

// Example: Get STL mesh files
const baseStl = 'https://hand-teleop-api.onrender.com/api/assets/robot/so101/Base_SO101.stl';
const handleStl = 'https://hand-teleop-api.onrender.com/api/assets/robot/so101/Handle_SO101.stl';
```

### **Error Handling**

All API endpoints return consistent error formats:

```json
{
    "detail": "Error description",
    "status_code": 400
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (endpoint or resource)
- `422` - Validation Error (invalid data format)
- `500` - Internal Server Error
- `503` - Service Unavailable (robot/tracking unavailable)

## Production Integration Examples

### **Complete Hand Cursor Implementation**
```javascript
class HandCursor {
    constructor() {
        this.ws = null;
        this.canvas = null;
        this.video = null;
        this.isTracking = false;
    }

    async connect() {
        try {
            this.ws = new WebSocket('wss://hand-teleop-api.onrender.com/api/tracking/live');
            this.ws.onmessage = this.handleTrackingData.bind(this);
            this.ws.onopen = () => this.startCamera();
        } catch (error) {
            console.error('Connection failed:', error);
        }
    }

    async startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            
            this.video = document.createElement('video');
            this.video.srcObject = stream;
            this.video.play();
            
            // Start frame processing
            this.processFrames();
        } catch (error) {
            console.error('Camera access failed:', error);
        }
    }

    processFrames() {
        if (!this.isTracking) return;

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        
        ctx.drawImage(this.video, 0, 0);
        const dataURL = canvas.toDataURL('image/jpeg', 0.8);
        
        this.ws.send(JSON.stringify({
            type: 'image',
            data: dataURL,
            tracking_mode: 'mediapipe',
            timestamp: new Date().toISOString()
        }));

        // Process at 15 FPS
        setTimeout(() => this.processFrames(), 67);
    }

    handleTrackingData(event) {
        const response = JSON.parse(event.data);
        
        if (response.type === 'tracking_result' && response.data.success) {
            const { fingertip_coords, hand_detected } = response.data;
            
            if (hand_detected && fingertip_coords) {
                // Convert normalized coordinates to screen position
                const indexTip = fingertip_coords.index_tip;
                const screenX = indexTip.x * window.innerWidth;
                const screenY = indexTip.y * window.innerHeight;
                
                // Update cursor position
                this.updateCursor(screenX, screenY);
                
                // Detect pinch gesture
                const thumbTip = fingertip_coords.thumb_tip;
                const distance = this.calculateDistance(indexTip, thumbTip);
                
                if (distance < 0.05) {
                    this.triggerClick(screenX, screenY);
                }
            }
        }
    }

    updateCursor(x, y) {
        // Update custom cursor or highlight elements
        document.documentElement.style.setProperty('--cursor-x', `${x}px`);
        document.documentElement.style.setProperty('--cursor-y', `${y}px`);
    }

    calculateDistance(point1, point2) {
        const dx = point1.x - point2.x;
        const dy = point1.y - point2.y;
        const dz = point1.z - point2.z;
        return Math.sqrt(dx*dx + dy*dy + dz*dz);
    }

    triggerClick(x, y) {
        const element = document.elementFromPoint(x, y);
        if (element && element.click) {
            element.click();
        }
    }
}

// Usage
const handCursor = new HandCursor();
handCursor.connect();
```

### **Portfolio Navigation Integration**
```javascript
// For jonaspetersen.com portfolio sections
class HandPortfolioNav {
    constructor() {
        this.currentSection = 0;
        this.sections = document.querySelectorAll('.portfolio-section');
        this.handCursor = new HandCursor();
        this.setupHandGestures();
    }

    setupHandGestures() {
        this.handCursor.onFingertipUpdate = (coords) => {
            if (!coords.hand_detected) return;

            const indexTip = coords.fingertip_coords.index_tip;
            
            // Horizontal swipe navigation
            if (indexTip.x < 0.2) {
                this.navigateSection(-1); // Previous
            } else if (indexTip.x > 0.8) {
                this.navigateSection(1);  // Next
            }
            
            // Vertical scroll simulation
            const scrollY = indexTip.y * document.body.scrollHeight;
            window.scrollTo({ top: scrollY, behavior: 'smooth' });
        };
    }

    navigateSection(direction) {
        this.currentSection += direction;
        this.currentSection = Math.max(0, Math.min(this.currentSection, this.sections.length - 1));
        
        this.sections[this.currentSection].scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}
```

## Development Workflow

### **Local Development Setup**
```bash
# Clone and setup
git clone https://github.com/7jep7/hand-teleop-system.git
cd hand-teleop-system

# Activate conda environment  
conda activate hand-teleop

# Start development servers (backend + frontend)
python main.py --dev
```

### **Available Development URLs**
```
Backend API:     http://localhost:8000
Testing Demo:    http://localhost:8000/         # Main demo interface
Main Demo:       http://localhost:8000/       # Chrome-safe demo
Testing Tool:    http://localhost:8000/testing.html # Dual-camera testing
API Docs:        http://localhost:8000/docs     # Interactive documentation
Health Check:    http://localhost:8000/api/health
Frontend Server: http://localhost:3000         # Static file server
```

### **Dual Backend Testing**
The testing interface supports switching between:
- **Local Backend**: `ws://localhost:8000/api/tracking/live`
- **Deployed Backend**: `wss://hand-teleop-api.onrender.com/api/tracking/live`

This ensures identical behavior between development and production environments.

## CORS Configuration

```python
# Current backend CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jonaspetersen.com",
        "https://*.jonaspetersen.com", 
        "https://*.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

## Performance & Reliability

### **Optimized Frame Processing**
- **Frame Rate**: 15-20 FPS (optimal balance of responsiveness vs CPU usage)
- **Processing Time**: <50ms typical latency
- **Image Compression**: JPEG 80% quality for WebSocket transmission
- **Error Handling**: Graceful fallbacks for OpenCV/MediaPipe failures

### **Production Deployment**
- **Backend**: Render.com with automatic deployments
- **Docker**: Optimized for headless OpenCV operation
- **Health Monitoring**: `/api/health` endpoint reports system status
- **Fallback Mode**: Mock data when computer vision libraries fail

### **Connection Management**
```javascript
// Robust WebSocket with auto-reconnection
class RobustWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectInterval = 5000;
        this.maxRetries = 5;
        this.retryCount = 0;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('✅ Connected to hand tracking');
            this.retryCount = 0;
        };
        
        this.ws.onclose = () => {
            if (this.retryCount < this.maxRetries) {
                console.log(`🔄 Reconnecting... (${this.retryCount + 1}/${this.maxRetries})`);
                setTimeout(() => {
                    this.retryCount++;
                    this.connect();
                }, this.reconnectInterval);
            } else {
                console.error('❌ Max reconnection attempts reached');
            }
        };
    }
}
```

## Security & Best Practices

### **Camera Permissions**
```javascript
// Graceful camera access handling
async function requestCameraPermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        return stream;
    } catch (error) {
        if (error.name === 'NotAllowedError') {
            showPermissionMessage();
        } else if (error.name === 'NotFoundError') {
            showNoCameraMessage();
        }
        throw error;
    }
}
```

### **Production Environment Variables**
```bash
# Render.com deployment settings
PORT=8000
ENVIRONMENT=production
OPENCV_HEADLESS=1
LOG_LEVEL=warning
```

## Testing & Validation

### **Health Check Endpoint**
```bash
# Test backend connectivity
curl https://hand-teleop-api.onrender.com/api/health

# Expected response:
{
  "status": "healthy",
  "opencv_available": true,
  "mediapipe_available": true,
  "timestamp": "2025-09-02T15:30:45.123Z",
  "version": "1.0.0"
}
```

### **WebSocket Testing**
Use the testing interface at `https://hand-teleop-api.onrender.com/testing.html` to:
- Test WebSocket connectivity
- Monitor real-time data flow
- Debug message formatting
- Measure latency and FPS

### **Frontend Integration Testing**
```javascript
// Simple integration test
async function testHandTracking() {
    const ws = new WebSocket('wss://hand-teleop-api.onrender.com/api/tracking/live');
    
    ws.onopen = () => {
        console.log('✅ WebSocket connected');
        // Send test frame
        ws.send(JSON.stringify({
            type: 'image',
            data: 'data:image/jpeg;base64,test',
            timestamp: new Date().toISOString()
        }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📊 Received:', data);
        ws.close();
    };
}
```

## Repository Structure

```
hand-teleop-system/
├── backend/
│   └── render_backend.py      # FastAPI backend with WebSocket
├── frontend/
│   ├── demo.html             # Main dual-camera demo interface
│   ├── archived/             # Archived old interfaces
│   └── index.html           # Static overview page
├── docs/
│   └── WEB_INTEGRATION.md   # This documentation
├── main.py                  # Development workflow manager
├── Dockerfile              # Production deployment
├── requirements-deploy.txt  # Production dependencies
└── README.md               # Project overview
```

## Quick Integration Checklist

For integrating with jonaspetersen.com:

### **Real-time WebSocket Integration**
- [ ] **Connect WebSocket**: `wss://hand-teleop-api.onrender.com/api/tracking/live`
- [ ] **Request Camera**: Handle permissions gracefully
- [ ] **Send Frames**: Base64 encoded JPEG at 15-20 FPS
- [ ] **Process Response**: Extract `fingertip_coords` from tracking results
- [ ] **Handle Errors**: Implement reconnection and fallback modes
- [ ] **Test Connection**: Use debug tool to validate data flow
- [ ] **Performance Monitor**: Track latency and frame rates

### **REST API Integration**
- [ ] **Health Check**: Test `GET /api/health` for system status
- [ ] **Single Frame**: Use `POST /api/track` for occasional hand detection
- [ ] **Robot Control**: Configure robots via `POST /api/config/robot`
- [ ] **Performance Metrics**: Monitor via `GET /api/performance`
- [ ] **Error Handling**: Implement proper HTTP status code handling
- [ ] **Asset Loading**: Use `/api/assets/robot/so101/*` for 3D models

### **Development & Testing**
- [ ] **Local Testing**: Use `python main.py --dev` for local development
- [ ] **Interactive Docs**: Access `/docs` for API exploration
- [ ] **Main Demo**: Access the dual-camera interface at `/` or `/demo.html`
- [ ] **CORS Validation**: Ensure frontend domain is whitelisted

## Support & Troubleshooting

### **Common Issues**
1. **WebSocket Connection Failed**: Check CORS settings and URL format
2. **Camera Access Denied**: Implement permission request flow
3. **High Latency**: Reduce frame rate or image quality
4. **No Hand Detection**: Ensure good lighting and hand visibility
5. **REST API 422 Error**: Check request data format and required fields
6. **503 Service Unavailable**: Robot/tracking service temporarily down

### **API Usage Patterns**

**When to use WebSocket vs REST API:**

- **WebSocket** (`/api/tracking/live`): 
  - Real-time hand cursor/gesture control
  - Continuous tracking for interactive UIs
  - Live robot teleoperation
  - High-frequency updates (15-30 FPS)

- **REST API** (`/api/track`):
  - Occasional gesture recognition
  - Single-shot hand detection
  - Batch processing
  - Integration with forms/buttons

**Performance Optimization:**
- Use WebSocket for real-time, REST for sporadic use
- Monitor `/api/performance` for system load
- Implement client-side frame rate limiting
- Cache robot configurations via `/api/config/robot`

### **Debug Resources**
- **Main Demo**: https://hand-teleop-api.onrender.com/
- **Interactive API Documentation**: https://hand-teleop-api.onrender.com/docs
- **System Health Check**: https://hand-teleop-api.onrender.com/api/health
- **Performance Metrics**: https://hand-teleop-api.onrender.com/api/performance
- **Deployment Info**: https://hand-teleop-api.onrender.com/api/deployment-info
- **Available Robots**: https://hand-teleop-api.onrender.com/api/robots

---

*Last updated: September 2, 2025*
*Backend Version: Production-ready with OpenCV fallbacks*
*Frontend: Cleaned and streamlined for minimal testing interface*