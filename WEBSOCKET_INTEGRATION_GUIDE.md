# 🎯 **Step-by-Step Guide: Getting Fingertip Data via WebSocket**

## 📍 **Problem Summary**
This guide provides precise instructions to integrate real-time hand tracking with your website (jonaspetersen.com) via WebSocket. You'll get:
- **Fingertip coordinates** (thumb_tip, index_tip, index_pip, index_mcp) - normalized 0-1
- **Hand visibility** (hand_detected: true/false) 
- **Gripper state** (open/closed based on thumb-index distance)
- **Processing metrics** (processing_time_ms, success status)
- **Robot integration** (optional robot joints and pose data)

---

## 🔗 **WebSocket Endpoint**
```
ws://localhost:8000/api/tracking/live
```

**Production URL:** Replace `localhost:8000` with your deployed server domain.

---

## 🚀 **Quick Start (Minimal Example)**

```javascript
// Minimal working example for jonaspetersen.com
const ws = new WebSocket('ws://your-server.com:8000/api/tracking/live');

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    if (response.type === 'tracking_result' && response.data.hand_detected) {
        const fingertips = response.data.fingertip_coords;
        
        // Move cursor with index finger (normalized coordinates)
        const x = fingertips.index_tip.x * window.innerWidth;
        const y = fingertips.index_tip.y * window.innerHeight;
        updateCursor(x, y);
        
        // Detect pinch gesture for selection
        const distance = Math.sqrt(
            Math.pow(fingertips.thumb_tip.x - fingertips.index_tip.x, 2) +
            Math.pow(fingertips.thumb_tip.y - fingertips.index_tip.y, 2)
        );
        if (distance < 0.05) triggerSelection(); // Pinch detected
    }
};

// Send camera frames (see full example below)
ws.send(JSON.stringify({
    type: 'image',
    data: 'data:image/jpeg;base64,...', // base64 image
    tracking_mode: 'mediapipe'
}));
```

---

## 📡 **Step 1: Connect to WebSocket**

### JavaScript Connection:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/tracking/live');

ws.onopen = () => {
    console.log('Connected to hand tracking server');
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('Received:', response);
    
    // Handle the tracking result
    if (response.type === 'tracking_result') {
        handleTrackingResult(response.data);
    }
};
```

---

## 📸 **Step 2: Send Camera Frame**

You need to send a JSON message with your camera frame as base64 image data:

```javascript
// Capture frame from video element
function captureAndSendFrame(videoElement) {
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0, 640, 480);
    
    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    // Send to WebSocket
    const message = {
        type: 'image',
        data: imageData,
        tracking_mode: 'mediapipe',  // or 'wilor' 
        robot_type: 'so101',
        timestamp: new Date().toISOString()
    };
    
    ws.send(JSON.stringify(message));
}
```

---

## 📊 **Step 3: Parse the Response**

The WebSocket returns this **exact structure** (verified with current backend):

```javascript
{
    "type": "tracking_result",
    "data": {
        "success": true,
        "timestamp": "2025-08-31T10:30:00.123456",
        "hand_detected": true,          // ✅ HAND VISIBLE/NOT VISIBLE
        "fingertip_coords": {           // ✅ FINGERTIP DATA (normalized 0-1)
            "thumb_tip": {
                "x": 0.234,             // 0-1 (left to right)
                "y": 0.567,             // 0-1 (top to bottom)  
                "z": 0.012              // depth (relative)
            },
            "index_tip": {
                "x": 0.445,
                "y": 0.334,
                "z": 0.008
            },
            "index_pip": {              // index middle joint
                "x": 0.423,
                "y": 0.356,
                "z": 0.015
            },
            "index_mcp": {              // index base joint
                "x": 0.398,
                "y": 0.378,
                "z": 0.022
            }
        },
        "hand_pose": {                  // Full MediaPipe landmarks (21 points)
            "landmarks": [...],         // All 21 hand landmarks
            "score": 0.95              // Detection confidence
        },
        "tracking_mode": "mediapipe",   // or "wilor"
        "robot_joints": [...],          // Optional: robot joint angles
        "robot_pose": {...},           // Optional: robot pose data
        "annotated_frame": "data:image/jpeg;base64,...", // Processed image
        "processing_time_ms": 45.2,
        "message": "Hand tracking completed"
    },
    "timestamp": "2025-08-31T10:30:00.123456"
}
```

**When no hand detected:**
```javascript
{
    "type": "tracking_result", 
    "data": {
        "success": true,
        "hand_detected": false,
        "fingertip_coords": null,   // ❌ No fingertip data
        "message": "No hand detected"
    }
}
```
```

---

## 🎯 **Step 4: Extract Data You Need**

```javascript
function handleTrackingResult(data) {
    // ✅ Hand visible/not visible
    const handVisible = data.hand_detected;
    console.log('Hand visible:', handVisible);
    
    // ✅ Fingertip coordinates (normalized 0-1)
    if (handVisible && data.fingertip_coords) {
        const fingertips = data.fingertip_coords;
        
        console.log('Thumb tip:', fingertips.thumb_tip);
        console.log('Index tip:', fingertips.index_tip);
        console.log('Index PIP:', fingertips.index_pip);
        console.log('Index MCP:', fingertips.index_mcp);
        
        // ✅ Calculate gripper open/closed
        const gripperState = calculateGripperState(fingertips);
        console.log('Gripper:', gripperState);
        
        // Use in your jonaspetersen.com interface
        updateYourInterface({
            handVisible,
            fingertips,
            gripperState,
            processingTime: data.processing_time_ms
        });
    }
}

function calculateGripperState(fingertips) {
    if (!fingertips.thumb_tip || !fingertips.index_tip) {
        return 'unknown';
    }
    
    // Calculate distance between thumb and index
    const dx = fingertips.thumb_tip.x - fingertips.index_tip.x;
    const dy = fingertips.thumb_tip.y - fingertips.index_tip.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // Threshold for pinch gesture (adjust as needed)
    return distance < 0.05 ? 'closed' : 'open';
}
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: No `fingertip_coords` in response**
**Cause:** Hand not detected or poor tracking conditions.
**Solution:** 
```javascript
ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('Full response:', JSON.stringify(response, null, 2));
    
    if (response.data.hand_detected) {
        // Use fingertip_coords directly
        const fingertips = response.data.fingertip_coords;
        console.log('Fingertips available:', fingertips);
    } else {
        console.log('No hand detected:', response.data.message);
        
        // Optionally extract from full hand_pose.landmarks
        if (response.data.hand_pose?.landmarks) {
            const landmarks = response.data.hand_pose.landmarks;
            const fingertips = {
                thumb_tip: landmarks[4],     // landmark 4
                index_tip: landmarks[8],     // landmark 8  
                index_pip: landmarks[6],     // landmark 6
                index_mcp: landmarks[5]      // landmark 5
            };
        }
    }
};
```

### **Issue 2: `hand_detected` always false**
**Causes & Solutions:**
- **Poor lighting:** Ensure bright, even lighting
- **Hand not in frame:** Position hand clearly in camera view  
- **Wrong camera:** Check camera permissions and selection
- **Processing lag:** Check `processing_time_ms` (should be <100ms)
- **Tracking mode:** Try both `"mediapipe"` and `"wilor"` modes

### **Issue 3: Coordinates seem wrong**
**Cause:** Coordinates are normalized (0-1), not pixel coordinates.
**Solution:**
```javascript
// Convert normalized coordinates to screen/element coordinates
function normalizedToScreen(fingertip, element = document.body) {
    const rect = element.getBoundingClientRect();
    return {
        x: fingertip.x * rect.width + rect.left,
        y: fingertip.y * rect.height + rect.top
    };
}

// Example usage
const screenPos = normalizedToScreen(fingertips.index_tip);
updateCursor(screenPos.x, screenPos.y);
```

### **Issue 4: WebSocket connection fails**
**Causes & Solutions:**
- **CORS/CSP errors:** Ensure same origin or proper CORS setup
- **Server not running:** Check `http://localhost:8000/api/health`
- **Wrong URL:** Verify WebSocket URL (ws:// not http://)
- **Network issues:** Check firewall/proxy settings

### **Issue 5: High latency or dropped frames**
**Solutions:**
- Reduce frame rate: Send frames every 100-200ms instead of 60fps
- Lower image quality: Use `canvas.toDataURL('image/jpeg', 0.6)`
- Smaller image: Resize to 320x240 before sending
- Check `processing_time_ms` in response

---

## 🧪 **Step 5: Test Your Integration**

### **Method 1: Use Built-in Test Tool**
```bash
# Start the development server
python3 main.py --dev

# Open test interface
http://localhost:3000/test_websocket.html
```
This provides a complete test interface with camera, connection status, and real-time fingertip data display.

### **Method 2: Quick Test Script**
```javascript
// Test WebSocket connection and basic functionality
const ws = new WebSocket('ws://localhost:8000/api/tracking/live');

ws.onopen = () => {
    console.log('✅ Connected to hand tracking');
    
    // Test ping
    ws.send(JSON.stringify({ type: 'ping' }));
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('📨 Response type:', response.type);
    
    if (response.type === 'pong') {
        console.log('✅ Ping successful - server responding');
    } else if (response.type === 'tracking_result') {
        console.log('✅ Tracking data received');
        console.log('   Hand detected:', response.data.hand_detected);
        console.log('   Fingertips available:', !!response.data.fingertip_coords);
        console.log('   Processing time:', response.data.processing_time_ms + 'ms');
        
        if (response.data.fingertip_coords) {
            const index = response.data.fingertip_coords.index_tip;
            console.log(`   Index finger: (${index.x.toFixed(3)}, ${index.y.toFixed(3)})`);
        }
    }
};

ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};
```

### **Method 3: Validate Response Structure**
```javascript
function validateResponse(response) {
    const checks = {
        hasType: !!response.type,
        hasData: !!response.data,
        hasTimestamp: !!response.timestamp,
        hasHandDetected: typeof response.data?.hand_detected === 'boolean',
        hasFingertips: response.data?.hand_detected ? !!response.data?.fingertip_coords : true,
        hasProcessingTime: typeof response.data?.processing_time_ms === 'number'
    };
    
    console.log('Response validation:', checks);
    const isValid = Object.values(checks).every(check => check);
    console.log(isValid ? '✅ Response structure valid' : '❌ Response structure invalid');
    
    return isValid;
}
```

---

## 🔧 **Step 6: Backend Verification & Deployment**

### **Development Testing**
1. **Check backend health:**
   ```bash
   curl -I http://localhost:8000/api/health
   # Should return 200 OK
   ```

2. **Test built-in demos:**
   ```bash
   # Start development environment
   python3 main.py --dev
   
   # Test these URLs:
   http://localhost:3000/mvp-demo.html          # MVP hand tracking demo
   http://localhost:3000/test_websocket.html    # WebSocket test tool
   http://localhost:3000/web/web_interface.html # Full interface
   ```

3. **Check backend logs for errors:**
   - Look for WebSocket connection messages
   - Monitor processing times
   - Check for MediaPipe/tracking errors

### **Production Deployment**

#### **Option 1: Docker Deployment**
```bash
# Build and run with Docker
docker build -t hand-teleop .
docker run -p 8000:8000 hand-teleop

# WebSocket endpoint available at:
ws://your-domain.com:8000/api/tracking/live
```

#### **Option 2: Direct Deployment**
```bash
# Install dependencies
conda env create -f environment.yml
conda activate hand-teleop

# Start production server
python3 main.py --start

# Configure reverse proxy (nginx example):
upstream hand_teleop {
    server localhost:8000;
}

server {
    location /api/tracking/live {
        proxy_pass http://hand_teleop;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### **Option 3: Cloud Deployment**
The system includes `render.yaml` for Render.com deployment:
```bash
# Push to GitHub and connect to Render
git push origin main

# WebSocket will be available at:
wss://your-app.onrender.com/api/tracking/live
```

### **Environment Variables**
```bash
# Optional configuration
export OMP_NUM_THREADS=4        # CPU optimization
export CUDA_VISIBLE_DEVICES=0   # GPU selection
export PORT=8000                # Server port
```

### **Performance Optimization**
- **CPU cores:** System auto-detects and optimizes
- **Memory usage:** Built-in resource management
- **GPU acceleration:** Automatic CUDA detection
- **Frame rate:** Adjust based on your needs (10-30 FPS recommended)

---

## 🎯 **Final jonaspetersen.com Integration**

### **Complete Production Example**
```javascript
// Complete integration class for jonaspetersen.com
class HandTrackingPortfolio {
    constructor(serverUrl = 'wss://your-server.com/api/tracking/live') {
        this.serverUrl = serverUrl;
        this.ws = null;
        this.isConnected = false;
        this.video = null;
        this.canvas = null;
        this.isTracking = false;
        
        // Callbacks
        this.onHandDetected = null;
        this.onHandLost = null;
        this.onFingerMove = null;
        this.onPinchGesture = null;
        this.onConnectionChange = null;
    }
    
    async init() {
        try {
            await this.connectWebSocket();
            await this.setupCamera();
            this.startTracking();
            return true;
        } catch (error) {
            console.error('Failed to initialize hand tracking:', error);
            return false;
        }
    }
    
    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.serverUrl);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                console.log('✅ Hand tracking connected');
                if (this.onConnectionChange) this.onConnectionChange(true);
                resolve();
            };
            
            this.ws.onclose = () => {
                this.isConnected = false;
                if (this.onConnectionChange) this.onConnectionChange(false);
            };
            
            this.ws.onerror = (error) => reject(error);
            
            this.ws.onmessage = (event) => this.handleMessage(event);
        });
    }
    
    async setupCamera() {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480, facingMode: 'user' }
        });
        
        this.video = document.createElement('video');
        this.video.srcObject = stream;
        this.video.autoplay = true;
        this.video.muted = true;
        
        this.canvas = document.createElement('canvas');
        this.canvas.width = 640;
        this.canvas.height = 480;
        
        return new Promise(resolve => {
            this.video.onloadedmetadata = () => resolve();
        });
    }
    
    startTracking() {
        if (!this.isConnected || !this.video || this.isTracking) return;
        
        this.isTracking = true;
        this.trackingInterval = setInterval(() => {
            this.sendFrame();
        }, 67); // ~15 FPS for smooth experience
    }
    
    stopTracking() {
        this.isTracking = false;
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
    }
    
    sendFrame() {
        if (!this.ws || !this.video || !this.canvas) return;
        
        const ctx = this.canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0, 640, 480);
        
        const imageData = this.canvas.toDataURL('image/jpeg', 0.7);
        
        this.ws.send(JSON.stringify({
            type: 'image',
            data: imageData,
            tracking_mode: 'mediapipe',
            robot_type: 'so101',
            timestamp: new Date().toISOString()
        }));
    }
    
    handleMessage(event) {
        const response = JSON.parse(event.data);
        
        if (response.type === 'tracking_result') {
            const data = response.data;
            
            if (data.hand_detected && data.fingertip_coords) {
                // Hand detected
                if (this.onHandDetected) this.onHandDetected(data);
                
                // Finger movement
                if (this.onFingerMove) {
                    this.onFingerMove(data.fingertip_coords.index_tip);
                }
                
                // Pinch gesture detection
                const pinchDistance = this.calculatePinchDistance(data.fingertip_coords);
                if (pinchDistance < 0.05 && this.onPinchGesture) {
                    this.onPinchGesture(data.fingertip_coords);
                }
                
            } else {
                // Hand lost
                if (this.onHandLost) this.onHandLost();
            }
        }
    }
    
    calculatePinchDistance(fingertips) {
        const dx = fingertips.thumb_tip.x - fingertips.index_tip.x;
        const dy = fingertips.thumb_tip.y - fingertips.index_tip.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    // Utility methods
    normalizedToScreen(point, element = document.body) {
        const rect = element.getBoundingClientRect();
        return {
            x: point.x * rect.width + rect.left,
            y: point.y * rect.height + rect.top
        };
    }
    
    destroy() {
        this.stopTracking();
        if (this.video && this.video.srcObject) {
            this.video.srcObject.getTracks().forEach(track => track.stop());
        }
        if (this.ws) this.ws.close();
    }
}

// Usage example for jonaspetersen.com
async function initPortfolioHandTracking() {
    const handTracking = new HandTrackingPortfolio('wss://your-server.com/api/tracking/live');
    
    // Set up event handlers
    handTracking.onFingerMove = (indexTip) => {
        // Move custom cursor
        const cursor = document.getElementById('hand-cursor');
        const pos = handTracking.normalizedToScreen(indexTip);
        cursor.style.left = pos.x + 'px';
        cursor.style.top = pos.y + 'px';
        cursor.style.display = 'block';
        
        // Check portfolio item hovering
        checkPortfolioHover(pos);
    };
    
    handTracking.onPinchGesture = () => {
        // Trigger selection
        triggerPortfolioSelection();
    };
    
    handTracking.onHandLost = () => {
        // Hide cursor
        document.getElementById('hand-cursor').style.display = 'none';
    };
    
    handTracking.onConnectionChange = (connected) => {
        updateConnectionStatus(connected);
    };
    
    // Initialize
    const success = await handTracking.init();
    if (success) {
        console.log('🎉 Hand tracking ready for portfolio interaction!');
    }
    
    return handTracking;
}

// Portfolio-specific functions
function checkPortfolioHover(cursorPos) {
    document.querySelectorAll('.portfolio-item').forEach(item => {
        const rect = item.getBoundingClientRect();
        const isHovering = cursorPos.x >= rect.left && cursorPos.x <= rect.right &&
                          cursorPos.y >= rect.top && cursorPos.y <= rect.bottom;
        
        item.classList.toggle('hand-hover', isHovering);
    });
}

function triggerPortfolioSelection() {
    const hoveredItem = document.querySelector('.portfolio-item.hand-hover');
    if (hoveredItem) {
        hoveredItem.click(); // Trigger selection
        console.log('✋ Hand selection:', hoveredItem.textContent);
    }
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('hand-tracking-status');
    if (status) {
        status.textContent = connected ? 'Hand tracking active' : 'Hand tracking offline';
        status.className = connected ? 'connected' : 'disconnected';
    }
}
```

### **CSS for Hand Cursor**
```css
#hand-cursor {
    position: fixed;
    width: 20px;
    height: 20px;
    background: radial-gradient(circle, #ff6b6b 0%, #ff5252 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 10000;
    display: none;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 20px rgba(255, 107, 107, 0.6);
    transition: all 0.1s ease;
}

.portfolio-item {
    transition: all 0.3s ease;
}

.portfolio-item.hand-hover {
    transform: scale(1.05);
    box-shadow: 0 10px 30px rgba(0, 123, 255, 0.3);
    border: 2px solid #007bff;
}

.hand-tracking-status.connected {
    color: #28a745;
}

.hand-tracking-status.disconnected {
    color: #dc3545;
}
```

---

## ✅ **Expected Results & Performance**

After following this guide, you should achieve:

### **Functionality**
- ✅ Real-time hand detection (`hand_detected: true/false`)
- ✅ 4 precise fingertip coordinates (normalized 0-1 coordinates):
  - `thumb_tip` - For pinch gestures
  - `index_tip` - Primary cursor control  
  - `index_pip` - Middle joint (gesture analysis)
  - `index_mcp` - Base joint (hand orientation)
- ✅ Pinch gesture detection (thumb-index distance < 0.05)
- ✅ Smooth cursor movement with finger tracking
- ✅ Portfolio item hover/selection with hand gestures

### **Performance Targets**
- **Latency:** <100ms end-to-end (camera → WebSocket → UI)
- **Frame rate:** 10-30 FPS (adjustable based on needs)
- **Processing time:** 20-80ms per frame (depends on hardware)
- **Accuracy:** >95% hand detection in good lighting
- **Stability:** Smooth tracking without jitter

### **System Requirements**
- **Client:** Modern browser with WebRTC camera access
- **Server:** Python 3.8+, 4GB+ RAM, CPU or GPU acceleration
- **Network:** Low-latency connection for real-time performance
- **Camera:** Standard webcam (640x480 minimum resolution)

### **Production Checklist**
- [ ] WebSocket endpoint deployed and accessible
- [ ] HTTPS/WSS for production (security requirement)
- [ ] CORS configured for your domain
- [ ] Error handling for network interruptions
- [ ] Fallback UI when hand tracking unavailable
- [ ] Performance monitoring and optimization
- [ ] User consent for camera access
- [ ] Mobile device compatibility testing

### **Troubleshooting Quick Reference**
| Issue | Solution |
|-------|----------|
| No connection | Check server status: `curl http://server/api/health` |
| No hand detected | Improve lighting, position hand in frame |
| High latency | Reduce frame rate, lower image quality |
| Jittery movement | Add smoothing/filtering to coordinates |
| Connection drops | Implement auto-reconnection logic |
| Mobile issues | Test camera permissions and orientation |

The WebSocket integration provides enterprise-grade real-time hand tracking with sub-100ms latency for smooth, interactive portfolio experiences! 🚀

---

## 📚 **Additional Resources**

- **[📖 Complete Documentation](DOCS.md)** - Full system documentation
- **[🧪 Test Interface](http://localhost:3000/test_websocket.html)** - Built-in testing tool  
- **[🎯 MVP Demo](http://localhost:3000/mvp-demo.html)** - Working example
- **[🤖 GitHub Repository](https://github.com/7jep7/hand-teleop-system)** - Source code
- **[⚡ API Health Check](http://localhost:8000/api/health)** - Server status

**Last Updated:** August 31, 2025 | **Version:** Production Ready
