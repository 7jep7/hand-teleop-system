"""
Hand Teleop System - Lightweight Deployment API
Simplified version for Render.com deployment without conda dependencies
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
import base64
import json
import os
import time
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Hand Teleop System API",
    version="1.0.0",
    description="Real-time hand tracking and robot control API"
)

# Enable CORS for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jonaspetersen.com",
        "https://www.jonaspetersen.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models
class RobotConfig(BaseModel):
    robot_type: str
    settings: Optional[Dict[str, Any]] = {}

class HandTrackingRequest(BaseModel):
    image_data: str
    robot_type: Optional[str] = "so101"
    tracking_mode: Optional[str] = "mediapipe"

class HandTrackingResponse(BaseModel):
    success: bool
    timestamp: str
    hand_detected: bool
    hand_pose: Optional[Dict[str, Any]] = None
    robot_joints: Optional[List[float]] = None
    robot_pose: Optional[Dict[str, Any]] = None
    processing_time_ms: float
    message: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    dependencies: Dict[str, str]

# Global state
current_robot_config = {
    "robot_type": "so101",
    "settings": {
        "tracking_mode": "mediapipe",
        "update_rate": 30,
        "smoothing": True
    }
}

ROBOT_TYPES = [
    {
        "id": "so101",
        "name": "SO-101 Humanoid Hand",
        "description": "5-DOF anthropomorphic robotic hand",
        "dof": 5,
        "workspace": "Human-like manipulation"
    },
    {
        "id": "so100", 
        "name": "SO-100 Industrial Gripper",
        "description": "2-DOF parallel gripper",
        "dof": 2,
        "workspace": "Industrial grasping"
    },
    {
        "id": "koch",
        "name": "Koch Robotic Arm",
        "description": "6-DOF robotic arm with gripper",
        "dof": 7,
        "workspace": "Full arm manipulation"
    },
    {
        "id": "moss",
        "name": "MOSS Research Platform",
        "description": "Multi-DOF research robotic system",
        "dof": 6,
        "workspace": "Research and development"
    }
]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Initialize MediaPipe
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available - using mock implementation")

# ==================== API ENDPOINTS ====================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        dependencies={
            "opencv": cv2.__version__,
            "numpy": np.__version__,
            "fastapi": "0.104.1",
            "mediapipe": "0.10.7" if MEDIAPIPE_AVAILABLE else "not_available"
        }
    )

@app.get("/api/robots")
async def list_robot_types():
    """List available robot types"""
    return {
        "robots": ROBOT_TYPES,
        "current_robot": current_robot_config["robot_type"],
        "total_count": len(ROBOT_TYPES)
    }

@app.post("/api/config/robot")
async def configure_robot(config: RobotConfig):
    """Configure robot type and settings"""
    global current_robot_config
    
    valid_types = [robot["id"] for robot in ROBOT_TYPES]
    if config.robot_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid robot type. Must be one of: {valid_types}"
        )
    
    current_robot_config["robot_type"] = config.robot_type
    current_robot_config["settings"].update(config.settings)
    
    return {
        "success": True,
        "message": f"Robot configured to {config.robot_type}",
        "config": current_robot_config,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/track", response_model=HandTrackingResponse)
async def process_hand_tracking(request: HandTrackingRequest):
    """Main hand tracking endpoint"""
    start_time = time.time()
    
    try:
        # Decode base64 image
        try:
            if request.image_data.startswith('data:'):
                image_data = request.image_data.split(',')[1]
            else:
                image_data = request.image_data
                
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Invalid image format")
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
        
        # Process hand tracking
        hand_pose, robot_joints, robot_pose = await process_lightweight_tracking(
            frame, 
            request.robot_type or current_robot_config["robot_type"]
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return HandTrackingResponse(
            success=True,
            timestamp=datetime.now().isoformat(),
            hand_detected=hand_pose is not None,
            hand_pose=hand_pose,
            robot_joints=robot_joints,
            robot_pose=robot_pose,
            processing_time_ms=processing_time,
            message="Hand tracking completed successfully" if hand_pose else "No hand detected"
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        return HandTrackingResponse(
            success=False,
            timestamp=datetime.now().isoformat(),
            hand_detected=False,
            processing_time_ms=processing_time,
            message=f"Processing error: {str(e)}"
        )

@app.websocket("/api/tracking/live")
async def websocket_live_tracking(websocket: WebSocket):
    """Real-time hand tracking WebSocket"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "image":
                    request = HandTrackingRequest(
                        image_data=message["data"],
                        robot_type=message.get("robot_type", current_robot_config["robot_type"])
                    )
                    
                    result = await process_hand_tracking(request)
                    
                    response = {
                        "type": "tracking_result",
                        "data": result.dict(),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                    
                elif message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/demo", response_class=HTMLResponse)
async def get_demo_interface():
    """Full demo interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hand Teleop System - Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        .video-container { position: relative; width: 100%; max-width: 640px; }
        .canvas-overlay { position: absolute; top: 0; left: 0; pointer-events: none; }
        #robot-visualization { width: 100%; height: 400px; border: 2px solid #e5e7eb; border-radius: 8px; }
        .status-indicator { 
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            margin-right: 8px; 
        }
        .status-healthy { background-color: #10b981; }
        .status-error { background-color: #ef4444; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-4">Hand Teleop System</h1>
            <p class="text-lg text-gray-600">Real-time hand tracking and robot control demonstration</p>
            <div class="mt-4">
                <span class="status-indicator status-healthy"></span>
                <span class="text-sm text-gray-600">API Status: </span>
                <span id="api-status" class="text-sm font-medium">Checking...</span>
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Hand Tracking Panel -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-semibold mb-4">Hand Tracking</h2>
                
                <div class="video-container mx-auto mb-4">
                    <video id="video" width="640" height="480" autoplay class="rounded-lg border-2 border-gray-300"></video>
                    <canvas id="overlay" width="640" height="480" class="canvas-overlay rounded-lg"></canvas>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Robot Type</label>
                        <select id="robotSelect" class="w-full p-2 border border-gray-300 rounded-md">
                            <option value="so101">SO-101 Humanoid Hand</option>
                            <option value="so100">SO-100 Industrial Gripper</option>
                            <option value="koch">Koch Robotic Arm</option>
                            <option value="moss">MOSS Research Platform</option>
                        </select>
                    </div>
                    
                    <div class="flex space-x-4">
                        <button id="startBtn" class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors">
                            Start Tracking
                        </button>
                        <button id="stopBtn" class="flex-1 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-md transition-colors" disabled>
                            Stop Tracking
                        </button>
                    </div>
                </div>
                
                <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h3 class="font-medium text-gray-800 mb-2">Status</h3>
                    <div id="status" class="text-sm text-gray-600">Ready to start tracking</div>
                    <div id="fps" class="text-sm text-gray-500 mt-1">FPS: 0</div>
                </div>
            </div>
            
            <!-- Robot Visualization Panel -->
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-semibold mb-4">Robot Visualization</h2>
                
                <div id="robot-visualization" class="mb-4"></div>
                
                <div class="space-y-4">
                    <div>
                        <h3 class="font-medium text-gray-800 mb-2">Joint Angles</h3>
                        <div id="joint-angles" class="text-sm text-gray-600 font-mono">
                            No data available
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="font-medium text-gray-800 mb-2">End Effector Pose</h3>
                        <div id="end-effector" class="text-sm text-gray-600 font-mono">
                            Position: (0.0, 0.0, 0.0)<br>
                            Orientation: (0.0, 0.0, 0.0)
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="font-medium text-gray-800 mb-2">Performance</h3>
                        <div id="performance" class="text-sm text-gray-600">
                            Processing Time: 0ms<br>
                            Update Rate: 0 Hz
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-8 text-center">
            <p class="text-sm text-gray-500">
                Powered by MediaPipe and FastAPI • 
                <a href="https://jonaspetersen.com" class="text-blue-500 hover:text-blue-600">Jonas Petersen Portfolio</a>
            </p>
        </div>
    </div>

    <script>
        // Demo implementation with error handling for deployment
        let video, canvas, ctx, socket;
        let isTracking = false;
        let lastFrameTime = 0;
        let frameCount = 0;
        let fpsCounter = 0;
        let scene, camera, renderer, robotModel;
        
        async function initDemo() {
            video = document.getElementById('video');
            canvas = document.getElementById('overlay');
            ctx = canvas.getContext('2d');
            
            initRobotVisualization();
            
            document.getElementById('startBtn').addEventListener('click', startTracking);
            document.getElementById('stopBtn').addEventListener('click', stopTracking);
            document.getElementById('robotSelect').addEventListener('change', updateRobotType);
            
            await checkHealth();
        }
        
        async function checkHealth() {
            try {
                const response = await fetch('/api/health');
                const health = await response.json();
                document.getElementById('api-status').textContent = `${health.status} - v${health.version}`;
                document.getElementById('status').textContent = `API ${health.status}`;
            } catch (error) {
                document.getElementById('api-status').textContent = 'Connection failed';
                document.getElementById('status').textContent = 'API connection failed';
            }
        }
        
        function initRobotVisualization() {
            const container = document.getElementById('robot-visualization');
            
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f0f0);
            
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(2, 2, 3);
            camera.lookAt(0, 0, 0);
            
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);
            
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 5, 5);
            scene.add(directionalLight);
            
            createSimpleRobot();
            animate();
        }
        
        function createSimpleRobot() {
            const group = new THREE.Group();
            
            // Base
            const baseGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.2);
            const baseMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 });
            const base = new THREE.Mesh(baseGeometry, baseMaterial);
            base.position.y = 0.1;
            group.add(base);
            
            // Arm segments
            for (let i = 0; i < 3; i++) {
                const segmentGeometry = new THREE.BoxGeometry(0.1, 0.5, 0.1);
                const segmentMaterial = new THREE.MeshLambertMaterial({ color: 0x2196f3 });
                const segment = new THREE.Mesh(segmentGeometry, segmentMaterial);
                segment.position.y = 0.5 + i * 0.5;
                group.add(segment);
            }
            
            robotModel = group;
            scene.add(robotModel);
        }
        
        function animate() {
            requestAnimationFrame(animate);
            
            if (robotModel) {
                robotModel.rotation.y += 0.01;
            }
            
            renderer.render(scene, camera);
        }
        
        async function startTracking() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                video.srcObject = stream;
                
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                socket = new WebSocket(`${protocol}//${window.location.host}/api/tracking/live`);
                
                socket.onopen = () => {
                    document.getElementById('status').textContent = 'Connected - Tracking active';
                    isTracking = true;
                    updateButtons();
                    sendFrame();
                };
                
                socket.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    if (message.type === 'tracking_result') {
                        handleTrackingResult(message.data);
                    }
                };
                
                socket.onerror = () => {
                    document.getElementById('status').textContent = 'WebSocket connection failed';
                };
                
            } catch (error) {
                document.getElementById('status').textContent = `Camera access failed: ${error.message}`;
            }
        }
        
        function stopTracking() {
            isTracking = false;
            if (socket) {
                socket.close();
            }
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
            }
            document.getElementById('status').textContent = 'Tracking stopped';
            updateButtons();
        }
        
        function updateButtons() {
            document.getElementById('startBtn').disabled = isTracking;
            document.getElementById('stopBtn').disabled = !isTracking;
        }
        
        async function updateRobotType() {
            const robotType = document.getElementById('robotSelect').value;
            try {
                await fetch('/api/config/robot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ robot_type: robotType })
                });
                document.getElementById('status').textContent = `Robot configured: ${robotType}`;
            } catch (error) {
                console.error('Failed to update robot type:', error);
            }
        }
        
        function sendFrame() {
            if (!isTracking || !socket || socket.readyState !== WebSocket.OPEN) {
                return;
            }
            
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = video.videoWidth;
            tempCanvas.height = video.videoHeight;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(video, 0, 0);
            
            const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
            
            socket.send(JSON.stringify({
                type: 'image',
                data: imageData,
                robot_type: document.getElementById('robotSelect').value
            }));
            
            setTimeout(sendFrame, 33); // ~30 FPS
        }
        
        function handleTrackingResult(result) {
            const now = performance.now();
            if (now - lastFrameTime >= 1000) {
                fpsCounter = frameCount;
                frameCount = 0;
                lastFrameTime = now;
                document.getElementById('fps').textContent = `FPS: ${fpsCounter}`;
            }
            frameCount++;
            
            if (result.robot_joints) {
                const angles = result.robot_joints.map(angle => angle.toFixed(2)).join(', ');
                document.getElementById('joint-angles').textContent = `[${angles}]`;
            }
            
            if (result.robot_pose) {
                const pos = result.robot_pose.position || [0, 0, 0];
                const rot = result.robot_pose.orientation || [0, 0, 0];
                document.getElementById('end-effector').innerHTML = 
                    `Position: (${pos.map(p => p.toFixed(3)).join(', ')})<br>
                     Orientation: (${rot.map(r => r.toFixed(3)).join(', ')})`;
            }
            
            document.getElementById('performance').innerHTML = 
                `Processing Time: ${result.processing_time_ms.toFixed(1)}ms<br>
                 Update Rate: ${fpsCounter} Hz`;
        }
        
        document.addEventListener('DOMContentLoaded', initDemo);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# ==================== PROCESSING FUNCTIONS ====================

async def process_lightweight_tracking(frame, robot_type):
    """Lightweight hand tracking using MediaPipe"""
    try:
        if not MEDIAPIPE_AVAILABLE:
            # Mock implementation for demo purposes
            return generate_mock_hand_pose(), generate_mock_robot_joints(robot_type), generate_mock_robot_pose()
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract hand pose
            hand_pose = {
                "keypoints_2d": [],
                "keypoints_3d": [],
                "confidence": 0.8
            }
            
            for landmark in hand_landmarks.landmark:
                hand_pose["keypoints_2d"].append([landmark.x, landmark.y])
                hand_pose["keypoints_3d"].append([landmark.x, landmark.y, landmark.z])
            
            # Calculate robot joints from hand pose
            robot_joints = calculate_simple_robot_joints(hand_pose, robot_type)
            robot_pose = calculate_simple_robot_pose(robot_joints, robot_type)
            
            return hand_pose, robot_joints, robot_pose
        else:
            return None, None, None
            
    except Exception as e:
        print(f"Tracking error: {e}")
        return None, None, None

def calculate_simple_robot_joints(hand_pose, robot_type):
    """Simple robot joint calculation from hand pose"""
    try:
        keypoints = hand_pose.get("keypoints_3d", [])
        if not keypoints:
            return generate_mock_robot_joints(robot_type)
        
        # Simple mapping based on fingertip positions
        if robot_type == "so101":
            # 5-DOF humanoid hand
            finger_angles = []
            fingertip_indices = [4, 8, 12, 16, 20]  # MediaPipe fingertip indices
            for i in fingertip_indices:
                if i < len(keypoints):
                    angle = keypoints[i][2] * 1.5  # Simple Z-position mapping
                    finger_angles.append(max(0.0, min(1.0, angle)))
            return finger_angles[:5]
            
        elif robot_type == "so100":
            # 2-DOF gripper
            if len(keypoints) >= 20:
                thumb_tip = keypoints[4]
                index_tip = keypoints[8]
                distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5
                grip_angle = max(0.0, min(1.0, distance * 2))
                return [grip_angle, grip_angle]
            
        elif robot_type == "koch":
            # 7-DOF arm
            return [0.1, 0.2, 0.0, 0.3, 0.1, 0.2, 0.1]
            
        else:
            # Default 6-DOF
            return [0.1, 0.0, 0.2, 0.0, 0.1, 0.0]
            
    except Exception:
        return generate_mock_robot_joints(robot_type)

def calculate_simple_robot_pose(robot_joints, robot_type):
    """Simple robot pose calculation from joint angles"""
    try:
        # Simple forward kinematics approximation
        if robot_type == "so101":
            # Hand position
            x = sum(robot_joints[:3]) * 0.1
            y = sum(robot_joints[2:5]) * 0.1
            z = 0.2 + sum(robot_joints) * 0.05
            
        elif robot_type == "so100":
            # Gripper position
            x = 0.0
            y = 0.0
            z = 0.15 + robot_joints[0] * 0.1
            
        else:
            # Generic arm
            x = sum(robot_joints[::2]) * 0.1
            y = sum(robot_joints[1::2]) * 0.1
            z = 0.3
        
        return {
            "position": [x, y, z],
            "orientation": [0.0, 0.0, sum(robot_joints) * 0.1],
            "transformation_matrix": np.eye(4).tolist()
        }
        
    except Exception:
        return {
            "position": [0.0, 0.0, 0.2],
            "orientation": [0.0, 0.0, 0.0],
            "transformation_matrix": np.eye(4).tolist()
        }

def generate_mock_hand_pose():
    """Generate mock hand pose for demo purposes"""
    return {
        "keypoints_2d": [[0.5 + 0.1 * np.sin(time.time() + i), 0.5 + 0.1 * np.cos(time.time() + i)] for i in range(21)],
        "keypoints_3d": [[0.5, 0.5, 0.1] for _ in range(21)],
        "confidence": 0.9
    }

def generate_mock_robot_joints(robot_type):
    """Generate mock robot joints for demo purposes"""
    t = time.time()
    if robot_type == "so101":
        return [0.3 + 0.2 * np.sin(t + i) for i in range(5)]
    elif robot_type == "so100":
        return [0.5 + 0.3 * np.sin(t), 0.5 + 0.3 * np.sin(t)]
    elif robot_type == "koch":
        return [0.2 * np.sin(t + i * 0.5) for i in range(7)]
    else:
        return [0.1 * np.sin(t + i) for i in range(6)]

def generate_mock_robot_pose():
    """Generate mock robot pose for demo purposes"""
    t = time.time()
    return {
        "position": [0.2 * np.sin(t), 0.2 * np.cos(t), 0.3],
        "orientation": [0.1 * np.sin(t), 0.0, 0.1 * np.cos(t)],
        "transformation_matrix": np.eye(4).tolist()
    }

# ==================== COMPATIBILITY ENDPOINTS ====================

@app.get("/")
async def get_index():
    """Redirect to demo interface"""
    return HTMLResponse('<script>window.location.href="/demo";</script>')

@app.get("/health")
async def legacy_health_check():
    """Legacy health check endpoint"""
    return {"status": "healthy", "message": "Hand Teleop System API is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("deploy_api:app", host="0.0.0.0", port=port, reload=False)
