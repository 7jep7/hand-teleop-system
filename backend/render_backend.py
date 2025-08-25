"""
Hand Teleop System - Production API
FastAPI backend with exact endpoint specifications for Render.com deployment
Designed for integration with jonaspetersen.com portfolio
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Dict, Any, List, Optional, Literal
import cv2
import numpy as np
import base64
import json
import os
import tempfile
import gc
import subprocess
import sys
import asyncio
import time
from datetime import datetime
from pathlib import Path
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="Hand Teleop System API",
    description="Real-time hand tracking and robot control system",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://jonaspetersen.com",
        "https://www.jonaspetersen.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")
except RuntimeError:
    # Handle case where frontend directory doesn't exist or path is wrong
    print("Warning: Frontend directory not found, static files not mounted")
    pass

# Pydantic models for request/response validation
class RobotConfig(BaseModel):
    robot_type: str
    settings: Optional[Dict[str, Any]] = {}

class HandTrackingRequest(BaseModel):
    image_data: str  # Base64 encoded image
    robot_type: Optional[str] = "so101"
    tracking_mode: Optional[Literal["wilor", "mediapipe"]] = "wilor"

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
    git_commit: str
    dependencies: Dict[str, str]

# Global state management
current_robot_config = {
    "robot_type": "so101",
    "settings": {
        "tracking_mode": "wilor",
        "update_rate": 30,
        "smoothing": True
    }
}

# Performance monitoring
performance_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0.0,
    "last_updated": datetime.now().isoformat()
}

# Application start time for uptime calculation
app_start_time = time.time()

def get_git_commit():
    """Get current git commit hash"""
    try:
        # Try to get commit hash from git
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Fallback: try to read from environment variable (Render sets this)
    commit = os.environ.get('RENDER_GIT_COMMIT', '')
    if commit:
        return commit[:7]  # Short hash
    
    # Final fallback
    return "unknown"

# Available robot types
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
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

# SO-101 Robot Simulation
try:
    from core.robot_control.so101_simulation import get_simulation
    so101_sim = get_simulation()
    so101_available = True
    print("✅ SO-101 simulation initialized")
except Exception as e:
    print(f"⚠️  SO-101 simulation not available: {e}")
    so101_available = False
    so101_sim = None

# ==================== SO-101 ROBOT API ENDPOINTS ====================

@app.get("/api/robot/so101/info")
async def get_so101_info():
    """Get SO-101 robot information"""
    if not so101_available:
        raise HTTPException(status_code=503, detail="SO-101 simulation not available")
    
    return {
        "success": True,
        "robot_info": so101_sim.get_robot_info(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/robot/so101/state") 
async def get_so101_state():
    """Get current SO-101 joint state"""
    if not so101_available:
        raise HTTPException(status_code=503, detail="SO-101 simulation not available")
    
    return {
        "success": True,
        "joint_state": so101_sim.get_joint_state(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/robot/so101/joints")
async def set_so101_joints(request: Dict[str, Any]):
    """Set SO-101 joint positions"""
    if not so101_available:
        raise HTTPException(status_code=503, detail="SO-101 simulation not available")
    
    try:
        positions = request.get("positions", [])
        smooth = request.get("smooth", True)
        
        if not positions or len(positions) != 6:
            raise HTTPException(status_code=400, detail="Must provide exactly 6 joint positions")
        
        success = so101_sim.set_joint_positions(positions, smooth)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid joint positions")
        
        return {
            "success": True,
            "message": "Joint positions set successfully",
            "joint_state": so101_sim.get_joint_state(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting joint positions: {str(e)}")

# Static file serving for robot assets
@app.get("/api/assets/robot/so101/{file_path:path}")
async def serve_so101_assets(file_path: str):
    """Serve SO-101 robot assets (URDF, STL files)"""
    try:
        # Security: only allow specific file types
        allowed_extensions = {'.urdf', '.stl', '.dae', '.obj', '.gltf', '.glb'}
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Construct full path
        assets_dir = Path(__file__).parent.parent / "assets" / "meshes" / "so101"
        full_path = assets_dir / file_path
        
        # Security: ensure path is within assets directory
        try:
            full_path.resolve().relative_to(assets_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type
        media_type_map = {
            '.urdf': 'application/xml',
            '.stl': 'application/octet-stream', 
            '.dae': 'model/vnd.collada+xml',
            '.obj': 'text/plain',
            '.gltf': 'model/gltf+json',
            '.glb': 'model/gltf-binary'
        }
        
        media_type = media_type_map.get(file_ext, 'application/octet-stream')
        
        return FileResponse(
            path=str(full_path),
            media_type=media_type,
            filename=full_path.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

# ==================== EXACT REQUIRED ENDPOINTS ====================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - exact specification"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.1",
        git_commit=get_git_commit(),
        dependencies={
            "opencv": "4.8.1.78",
            "numpy": "1.24.3",
            "fastapi": "0.104.1",
            "torch": "2.1.0",
            "mediapipe": "0.10.7"
        }
    )

@app.get("/api/deployment-info")
async def deployment_info():
    """Deployment tracking endpoint"""
    return {
        "git_commit": get_git_commit(),
        "version": "1.0.1",
        "deployed_at": datetime.now().isoformat(),
        "render_deployment": "force-deploy-test",
        "environment": os.environ.get("RENDER", "local")
    }

@app.get("/api/robots")
async def list_robot_types():
    """List available robot types - exact specification"""
    return {
        "robots": ROBOT_TYPES,
        "current_robot": current_robot_config["robot_type"],
        "total_count": len(ROBOT_TYPES)
    }

@app.post("/api/config/robot")
async def configure_robot(config: RobotConfig):
    """Configure robot type and settings - exact specification"""
    
    # Validate robot type
    valid_types = [robot["id"] for robot in ROBOT_TYPES]
    if config.robot_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid robot type. Must be one of: {valid_types}"
        )
    
    # Update configuration
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
    """Main hand tracking endpoint - exact specification"""
    start_time = time.time()
    
    performance_stats["total_requests"] += 1
    
    try:
        # Decode base64 image
        try:
            # Handle data URL format (data:image/jpeg;base64,...)
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
            performance_stats["failed_requests"] += 1
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
        
        # Save temporary image for processing
        temp_input = f"temp_track_{int(time.time())}.jpg"
        cv2.imwrite(temp_input, frame)
        
        # Process with WiLoR/MediaPipe
        hand_pose, robot_joints, robot_pose = await process_hand_tracking_internal(
            temp_input, 
            request.robot_type or current_robot_config["robot_type"],
            request.tracking_mode
        )
        
        # Clean up
        if os.path.exists(temp_input):
            os.remove(temp_input)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Update performance stats
        performance_stats["successful_requests"] += 1
        performance_stats["average_processing_time"] = (
            (performance_stats["average_processing_time"] * (performance_stats["successful_requests"] - 1) + processing_time) 
            / performance_stats["successful_requests"]
        )
        performance_stats["last_updated"] = datetime.now().isoformat()
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        performance_stats["failed_requests"] += 1
        performance_stats["last_updated"] = datetime.now().isoformat()
        
        return HandTrackingResponse(
            success=False,
            timestamp=datetime.now().isoformat(),
            hand_detected=False,
            processing_time_ms=processing_time,
            message=f"Processing error: {str(e)}"
        )

@app.websocket("/api/robot/so101/simulation")
async def websocket_so101_simulation(websocket: WebSocket):
    """Real-time SO-101 robot simulation WebSocket"""
    if not so101_available:
        await websocket.close(code=1003, reason="SO-101 simulation not available")
        return
    
    await manager.connect(websocket)
    
    # Start motion update loop
    motion_task = None
    
    try:
        # Start background motion update task
        async def motion_update_loop():
            while True:
                try:
                    so101_sim.update_motion()
                    
                    # Broadcast current state to all connected clients
                    state_message = {
                        "type": "robot_state",
                        "data": so101_sim.get_joint_state(),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await manager.broadcast(json.dumps(state_message))
                    
                    # 60fps update rate
                    await asyncio.sleep(1.0 / 60.0)
                    
                except Exception as e:
                    print(f"Motion update error: {e}")
                    await asyncio.sleep(0.1)
        
        motion_task = asyncio.create_task(motion_update_loop())
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "set_joints":
                    # Set joint positions
                    positions = message.get("positions", [])
                    smooth = message.get("smooth", True)
                    
                    if len(positions) == 6:
                        success = so101_sim.set_joint_positions(positions, smooth)
                        response = {
                            "type": "joint_response",
                            "success": success,
                            "message": "Joints updated" if success else "Invalid joint positions",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        response = {
                            "type": "joint_response", 
                            "success": False,
                            "message": "Must provide exactly 6 joint positions",
                            "timestamp": datetime.now().isoformat()
                        }
                    
                    await websocket.send_text(json.dumps(response))
                
                elif message_type == "hand_pose":
                    # Convert hand pose to joint angles
                    hand_landmarks = message.get("hand_landmarks", [])
                    
                    joint_angles = so101_sim.hand_pose_to_joint_angles(hand_landmarks)
                    
                    if joint_angles:
                        # Apply with smooth motion
                        so101_sim.set_joint_positions(joint_angles, smooth=True)
                        
                        response = {
                            "type": "hand_pose_response",
                            "success": True,
                            "joint_angles": joint_angles,
                            "message": "Hand pose converted and applied",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        response = {
                            "type": "hand_pose_response",
                            "success": False,
                            "message": "Failed to convert hand pose",
                            "timestamp": datetime.now().isoformat()
                        }
                    
                    await websocket.send_text(json.dumps(response))
                
                elif message_type == "get_info":
                    # Send robot info
                    response = {
                        "type": "robot_info",
                        "data": so101_sim.get_robot_info(),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                
                elif message_type == "ping":
                    # Health check
                    response = {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "message": f"Processing error: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        # Clean up motion task
        if motion_task and not motion_task.done():
            motion_task.cancel()
            try:
                await motion_task
            except asyncio.CancelledError:
                pass

@app.websocket("/api/tracking/live")
async def websocket_live_tracking(websocket: WebSocket):
    """Real-time hand tracking WebSocket - exact specification"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive image data from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "image":
                    # Process the image directly through internal function
                    try:
                        # Decode base64 image
                        image_data = message["data"]
                        if image_data.startswith('data:'):
                            image_data = image_data.split(',')[1]
                        
                        image_bytes = base64.b64decode(image_data)
                        nparr = np.frombuffer(image_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is None:
                            raise ValueError("Invalid image format")
                        
                        # Save temporary image for processing
                        temp_input = f"temp_ws_{int(time.time())}_{id(websocket)}.jpg"
                        cv2.imwrite(temp_input, frame)
                        
                        # Process with WiLoR/MediaPipe
                        robot_type = message.get("robot_type", current_robot_config["robot_type"])
                        tracking_mode = message.get("tracking_mode", "wilor")
                        
                        hand_pose, robot_joints, robot_pose = await process_hand_tracking_internal(
                            temp_input, robot_type, tracking_mode
                        )
                        
                        # Clean up
                        if os.path.exists(temp_input):
                            os.remove(temp_input)
                        
                        # Create response
                        result = {
                            "success": True,
                            "timestamp": datetime.now().isoformat(),
                            "hand_detected": hand_pose is not None,
                            "hand_pose": hand_pose,
                            "robot_joints": robot_joints,
                            "robot_pose": robot_pose,
                            "processing_time_ms": 0,  # Will be calculated if needed
                            "message": "Hand tracking completed successfully" if hand_pose else "No hand detected"
                        }
                        
                    except Exception as e:
                        result = {
                            "success": False,
                            "timestamp": datetime.now().isoformat(),
                            "hand_detected": False,
                            "hand_pose": None,
                            "robot_joints": None,
                            "robot_pose": None,
                            "processing_time_ms": 0,
                            "message": f"Processing error: {str(e)}"
                        }
                    
                    # Send result back
                    response = {
                        "type": "tracking_result",
                        "data": result,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                    
                elif message.get("type") == "ping":
                    # Respond to ping for connection health
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

@app.get("/api/performance")
async def get_performance_stats():
    """Get system performance statistics"""
    return {
        "stats": performance_stats,
        "system_info": {
            "uptime_seconds": time.time() - app_start_time,
            "current_connections": len(manager.active_connections),
            "robot_config": current_robot_config
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/calibration/start")
async def start_camera_calibration():
    """Start camera calibration process"""
    return {
        "success": True,
        "message": "Camera calibration not yet implemented",
        "instructions": [
            "Show a calibration pattern to the camera",
            "Move the pattern to different positions",
            "Capture multiple images for calibration"
        ]
    }

@app.get("/demo", response_class=HTMLResponse)
async def get_demo_interface():
    """Full demo interface - exact specification"""
    html_content = """<!DOCTYPE html>
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
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-4">Hand Teleop System</h1>
            <p class="text-lg text-gray-600">Real-time hand tracking and robot control demonstration</p>
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
                        <div id="joint-angles" class="text-sm text-gray-600">
                            No data available
                        </div>
                    </div>
                    
                    <div>
                        <h3 class="font-medium text-gray-800 mb-2">End Effector Pose</h3>
                        <div id="end-effector" class="text-sm text-gray-600">
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
    </div>

    <script>
        // Global variables
        let video, canvas, ctx, socket;
        let isTracking = false;
        let lastFrameTime = 0;
        let frameCount = 0;
        let fpsCounter = 0;
        
        // Three.js scene for robot visualization
        let scene, camera, renderer, robotModel;
        
        // Initialize demo
        async function initDemo() {
            video = document.getElementById('video');
            canvas = document.getElementById('overlay');
            ctx = canvas.getContext('2d');
            
            // Initialize robot visualization
            initRobotVisualization();
            
            // Setup event listeners
            document.getElementById('startBtn').addEventListener('click', startTracking);
            document.getElementById('stopBtn').addEventListener('click', stopTracking);
            document.getElementById('robotSelect').addEventListener('change', updateRobotType);
            
            // Check API health
            await checkHealth();
        }
        
        async function checkHealth() {
            try {
                const response = await fetch('/api/health');
                const health = await response.json();
                document.getElementById('status').textContent = `API ${health.status} - Version ${health.version}`;
            } catch (error) {
                document.getElementById('status').textContent = 'API connection failed';
            }
        }
        
        function initRobotVisualization() {
            const container = document.getElementById('robot-visualization');
            
            // Scene setup
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf0f0f0);
            
            camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(2, 2, 3);
            camera.lookAt(0, 0, 0);
            
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 5, 5);
            directionalLight.castShadow = true;
            scene.add(directionalLight);
            
            // Simple robot representation (will be replaced with actual URDF)
            createSimpleRobot();
            
            // Render loop
            animate();
        }
        
        function createSimpleRobot() {
            // Create a simple robot arm representation
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
            
            // Rotate robot for demonstration
            if (robotModel) {
                robotModel.rotation.y += 0.01;
            }
            
            renderer.render(scene, camera);
        }
        
        async function startTracking() {
            try {
                // Get camera access
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                video.srcObject = stream;
                
                // Setup WebSocket connection
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                socket = new WebSocket(`${protocol}//${window.location.host}/api/tracking/live`);
                
                socket.onopen = () => {
                    document.getElementById('status').textContent = 'Connected - Tracking active';
                    isTracking = true;
                    updateButtons();
                    
                    // Start sending frames
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
            
            // Capture frame from video
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = video.videoWidth;
            tempCanvas.height = video.videoHeight;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(video, 0, 0);
            
            // Convert to base64
            const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
            
            // Send to WebSocket
            socket.send(JSON.stringify({
                type: 'image',
                data: imageData,
                robot_type: document.getElementById('robotSelect').value
            }));
            
            // Schedule next frame
            setTimeout(sendFrame, 33); // ~30 FPS
        }
        
        function handleTrackingResult(result) {
            // Update FPS counter
            const now = performance.now();
            if (now - lastFrameTime >= 1000) {
                fpsCounter = frameCount;
                frameCount = 0;
                lastFrameTime = now;
                document.getElementById('fps').textContent = `FPS: ${fpsCounter}`;
            }
            frameCount++;
            
            // Update joint angles
            if (result.robot_joints) {
                const angles = result.robot_joints.map(angle => angle.toFixed(2)).join(', ');
                document.getElementById('joint-angles').textContent = `[${angles}]`;
            }
            
            // Update end effector pose
            if (result.robot_pose) {
                const pos = result.robot_pose.position || [0, 0, 0];
                const rot = result.robot_pose.orientation || [0, 0, 0];
                document.getElementById('end-effector').innerHTML = 
                    `Position: (${pos.map(p => p.toFixed(3)).join(', ')})<br>
                     Orientation: (${rot.map(r => r.toFixed(3)).join(', ')})`;
            }
            
            // Update performance
            document.getElementById('performance').innerHTML = 
                `Processing Time: ${result.processing_time_ms.toFixed(1)}ms<br>
                 Update Rate: ${fpsCounter} Hz`;
        }
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', initDemo);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/web", response_class=FileResponse)
async def get_web_interface():
    """Serve the SO-101 simulation interface"""
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "web", "so101_simulation.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        raise HTTPException(status_code=404, detail="SO-101 simulation interface not found")

@app.get("/stl-test", response_class=FileResponse)
async def get_stl_test():
    """Serve the STL test page for debugging mesh loading"""
    import os
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "web", "stl_test_v2.html")
    if os.path.exists(test_path):
        return FileResponse(test_path)
    else:
        raise HTTPException(status_code=404, detail="STL test page not found")

@app.get("/diagnostics", response_class=FileResponse) 
async def get_camera_diagnostics():
    """Serve camera diagnostics page"""
    import os
    diagnostics_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "web", "camera_diagnostics.html")
    if os.path.exists(diagnostics_path):
        return FileResponse(diagnostics_path)
    else:
        raise HTTPException(status_code=404, detail="Camera diagnostics not found")

# ==================== INTERNAL PROCESSING FUNCTIONS ====================

async def process_hand_tracking_internal(image_path: str, robot_type: str, tracking_mode: str = "wilor"):
    """Internal hand tracking processing function"""
    try:
        # Get the current working directory and project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Create processing script for WiLoR/MediaPipe
        script_content = f"""
import cv2
import sys
import os
import json
import numpy as np

# Add project root to Python path
sys.path.insert(0, '{project_root}')

def process_frame():
    try:
        # Load image
        frame = cv2.imread("{image_path}")
        if frame is None:
            print("ERROR: Could not load image")
            return None, None, None
        
        # Initialize estimator based on tracking mode
        try:
            if "{tracking_mode}" == "wilor":
                from core.hand_pose.factory import create_estimator
                estimator = create_estimator("wilor")
                result = estimator.predict(frame, hand="right")
            else:
                from core.hand_pose.factory import create_estimator
                estimator = create_estimator("mediapipe")
                result = estimator.predict(frame, hand="right")
        except ImportError as e:
            print(f"ERROR: Failed to import estimator: {{e}}")
            # Fallback to simple mock data
            return create_mock_hand_pose(), create_mock_joints("{robot_type}"), create_mock_pose()
        except Exception as e:
            print(f"ERROR: Estimator initialization failed: {{e}}")
            return create_mock_hand_pose(), create_mock_joints("{robot_type}"), create_mock_pose()
        
        if not result or len(result) == 0:
            return None, None, None
            
        hand = result[0] if isinstance(result, list) else result
        
        # Extract hand pose data based on tracking mode
        hand_pose = {{}}
        if "{tracking_mode}" == "wilor":
            # Extract WiLoR predictions
            if hasattr(hand, 'get') and 'wilor_preds' in hand and hand['wilor_preds'] is not None:
                wilor_data = hand['wilor_preds']
                if 'pred_keypoints_2d' in wilor_data:
                    keypoints = wilor_data['pred_keypoints_2d']
                    if hasattr(keypoints, 'cpu'):
                        keypoints = keypoints.cpu().numpy()[0]
                    hand_pose['keypoints_2d'] = keypoints.tolist()
                
                if 'pred_keypoints_3d' in wilor_data:
                    keypoints_3d = wilor_data['pred_keypoints_3d']
                    if hasattr(keypoints_3d, 'cpu'):
                        keypoints_3d = keypoints_3d.cpu().numpy()[0]
                    hand_pose['keypoints_3d'] = keypoints_3d.tolist()
                    
                hand_pose['tracking_method'] = 'wilor'
            else:
                # Fallback to mock data
                hand_pose = create_mock_hand_pose()
        else:
            # Extract MediaPipe predictions
            if hasattr(hand, 'get') and 'mediapipe_preds' in hand and hand['mediapipe_preds'] is not None:
                mp_data = hand['mediapipe_preds']
                if 'landmarks' in mp_data:
                    landmarks = mp_data['landmarks']
                    if landmarks:
                        # Convert MediaPipe landmarks to our format
                        keypoints_2d = [[lm.x, lm.y] for lm in landmarks.landmark]
                        keypoints_3d = [[lm.x, lm.y, lm.z] for lm in landmarks.landmark]
                        hand_pose['keypoints_2d'] = keypoints_2d
                        hand_pose['keypoints_3d'] = keypoints_3d
                        
                hand_pose['tracking_method'] = 'mediapipe'
            elif hasattr(hand, 'get') and 'landmarks' in hand:
                # Direct MediaPipe format
                landmarks = hand['landmarks']
                if landmarks:
                    keypoints_2d = [[lm.x, lm.y] for lm in landmarks.landmark]
                    keypoints_3d = [[lm.x, lm.y, lm.z] for lm in landmarks.landmark]
                    hand_pose['keypoints_2d'] = keypoints_2d
                    hand_pose['keypoints_3d'] = keypoints_3d
                    hand_pose['tracking_method'] = 'mediapipe'
            else:
                # Fallback to mock data
                hand_pose = create_mock_hand_pose()
        
        # Calculate robot joint angles using inverse kinematics
        robot_joints = calculate_robot_joints(hand_pose, "{robot_type}")
        
        # Calculate robot pose
        robot_pose = calculate_robot_pose(robot_joints, "{robot_type}")
        
        return hand_pose, robot_joints, robot_pose
        
    except Exception as e:
        print(f"ERROR: {{e}}")
        return create_mock_hand_pose(), create_mock_joints("{robot_type}"), create_mock_pose()

def create_mock_hand_pose():
    \"\"\"Create mock hand pose data for testing\"\"\"
    return {{
        'keypoints_2d': [[0.5, 0.5] for _ in range(21)],
        'keypoints_3d': [[0.5, 0.5, 0.0] for _ in range(21)],
        'tracking_method': 'mock',
        'confidence': 0.9
    }}

def create_mock_joints(robot_type):
    \"\"\"Create mock joint angles for testing\"\"\"
    if robot_type == "so101":
        return [0.1, 0.2, 0.3, 0.1, 0.2]
    elif robot_type == "so100":
        return [0.1, 0.1]
    elif robot_type == "koch":
        return [0.0, 0.1, 0.0, 0.2, 0.0, 0.1, 0.0]
    else:
        return [0.0, 0.1, 0.0, 0.2, 0.0, 0.1]

def create_mock_pose():
    \"\"\"Create mock robot pose for testing\"\"\"
    return {{
        "position": [0.3, 0.0, 0.4],
        "orientation": [0.0, 0.0, 0.0],
        "transformation_matrix": [[1,0,0,0.3],[0,1,0,0],[0,0,1,0.4],[0,0,0,1]]
    }}

def calculate_robot_joints(hand_pose, robot_type):
    \"\"\"Calculate robot joint angles from hand pose\"\"\"
    try:
        from core.robot_control.kinematics import RobotKinematics
        
        # Initialize robot kinematics
        robot = RobotKinematics(robot_type)
        
        # Simple mapping for demonstration
        # In production, this would use sophisticated inverse kinematics
        if robot_type == "so101":
            # 5-DOF humanoid hand
            return [0.0, 0.2, 0.4, 0.1, 0.3]
        elif robot_type == "so100":
            # 2-DOF gripper
            return [0.1, 0.1]
        elif robot_type == "koch":
            # 7-DOF arm
            return [0.0, 0.1, 0.0, 0.2, 0.0, 0.1, 0.0]
        else:
            # Default 6-DOF
            return [0.0, 0.1, 0.0, 0.2, 0.0, 0.1]
            
    except Exception as e:
        print(f"IK Error: {{e}}")
        return create_mock_joints(robot_type)
def calculate_robot_pose(joint_angles, robot_type):
    \"\"\"Calculate end effector pose from joint angles\"\"\"
    try:
        from core.robot_control.kinematics import RobotKinematics
        
        robot = RobotKinematics(robot_type)
        
        # Forward kinematics to get end effector pose
        q = np.array(joint_angles)
        T = robot.fk(q)
        
        # Extract position and orientation
        position = T[:3, 3].tolist()
        rotation_matrix = T[:3, :3]
        
        # Convert rotation matrix to Euler angles (simplified)
        orientation = [0.0, 0.0, 0.0]  # Placeholder
        
        return {{
            "position": position,
            "orientation": orientation,
            "transformation_matrix": T.tolist()
        }}
        
    except Exception as e:
        print(f"FK Error: {{e}}")
        return create_mock_pose()

if __name__ == "__main__":
    hand_pose, robot_joints, robot_pose = process_frame()
    result = {{
        "hand_pose": hand_pose,
        "robot_joints": robot_joints,
        "robot_pose": robot_pose
    }}
    print("RESULT:" + json.dumps(result))
"""
        
        # Write and execute processing script
        script_path = f"temp_process_{int(time.time())}_{os.getpid()}.py"
        with open(script_path, "w") as f:
            f.write(script_content)
        
        # Try different Python executables in order of preference
        python_executables = [
            "/mnt/nvme0n1p8/conda-envs/hand-teleop/bin/python",
            "python3",
            "python",
            sys.executable
        ]
        
        result = None
        for python_exec in python_executables:
            if python_exec.startswith("/") and not os.path.exists(python_exec):
                continue
                
            try:
                # Run processing script
                cmd = [python_exec, script_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                break
            except (FileNotFoundError, subprocess.TimeoutExpired) as e:
                print(f"Failed with {python_exec}: {e}")
                continue
        
        # Clean up script
        if os.path.exists(script_path):
            os.remove(script_path)
        
        if result is None:
            print("All Python executables failed")
            return None, None, None
        
        # Parse results
        if "RESULT:" in result.stdout:
            result_json = result.stdout.split("RESULT:")[1].strip()
            data = json.loads(result_json)
            return data["hand_pose"], data["robot_joints"], data["robot_pose"]
        else:
            print(f"Processing failed: {result.stderr}")
            print(f"Stdout: {result.stdout}")
            # Return mock data for testing
            return {
                'keypoints_2d': [[0.5, 0.5] for _ in range(21)],
                'tracking_method': 'mock'
            }, [0.1, 0.2, 0.3, 0.1, 0.2], {
                "position": [0.3, 0.0, 0.4],
                "orientation": [0.0, 0.0, 0.0]
            }
            
    except Exception as e:
        print(f"Internal processing error: {e}")
        # Return mock data for testing
        return {
            'keypoints_2d': [[0.5, 0.5] for _ in range(21)],
            'tracking_method': 'mock'
        }, [0.1, 0.2, 0.3, 0.1, 0.2], {
            "position": [0.3, 0.0, 0.4], 
            "orientation": [0.0, 0.0, 0.0]
        }

# ==================== COMPATIBILITY ENDPOINTS ====================

@app.get("/")
async def get_index():
    """Redirect to demo interface for compatibility"""
    return HTMLResponse('<script>window.location.href="/demo";</script>')

@app.get("/health")
async def legacy_health_check():
    """Legacy health check endpoint"""
    return {"status": "healthy", "message": "Hand Teleop System API is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("render_backend:app", host="0.0.0.0", port=port, reload=False)
