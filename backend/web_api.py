"""
WiLoR Hand Tracking Web API
FastAPI backend for hand pose estimation with camera integration
Designed for integration with jonaspetersen.com (Remix + Tailwind)
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import json
import os
import tempfile
import gc
import subprocess
import sys
from typing import Dict, Any
import uvicorn

app = FastAPI(title="WiLoR Hand Tracking API", version="1.0.0")

# Enable CORS for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jonaspetersen.com",
        "https://www.jonaspetersen.com",
        "http://localhost:3000",  # For local development
        "http://localhost:5173"   # For Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
async def get_index():
    """Serve the main web interface"""
    return FileResponse("frontend/web/web_interface.html")

@app.get("/diagnostics")
async def get_diagnostics():
    """Serve camera diagnostics page"""
    return FileResponse("frontend/web/camera_diagnostics.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "WiLoR Hand Tracking API is running"}

@app.post("/api/process-hand")
async def process_hand(file: UploadFile = File(...)):
    """
    Process uploaded image for hand pose estimation
    Returns overlay image and hand data
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Save image temporarily for processing
        temp_input = "temp_web_input.jpg"
        temp_output = "temp_web_output.jpg"
        cv2.imwrite(temp_input, frame)
        
        # Create WiLoR processing script (runs in hand-teleop environment)
        script_content = """
import cv2
import sys
import os
import json
import numpy as np
import time

# Add project root to Python path
sys.path.insert(0, '/home/jonas-petersen/dev/hand-teleop')

# Configure resource management before importing heavy modules
from core.resource_manager import configure_torch_for_safety, SystemResourceMonitor
configure_torch_for_safety()

def progress_callback(message, percent):
    '''Progress callback for monitoring'''
    if percent >= 0:
        print(f"PROGRESS: {percent}% - {message}")
    else:
        print(f"ERROR: {message}")

def process_frame():
    monitor = SystemResourceMonitor()
    monitor.start_monitoring()
    
    try:
        print("STARTING: WiLoR processing with professional resource management")
        
        # Load image
        progress_callback("Loading input image", 5)
        frame = cv2.imread("temp_web_input.jpg")
        if frame is None:
            print("ERROR: Could not load image")
            return
        
        # Load WiLoR with resource management
        progress_callback("Initializing WiLoR estimator", 15)
        from core.hand_pose.factory import create_estimator
        estimator = create_estimator("wilor")
        
        # Process with progress tracking
        progress_callback("Processing hand detection", 30)
        result = estimator.pipe.predict(frame, hand="right")
        
        progress_callback("Analyzing results", 70)
        
        if not result or len(result) == 0:
            print("NO_HAND_DETECTED")
            return
            
        hand = result[0]
        print("HAND_DETECTED")
        
        # Create overlay with progress
        progress_callback("Creating visualization overlay", 80)
        overlay = frame.copy()
        hand_data = {"bbox": None, "keypoints_2d": []}
        
        # Draw bounding box safely
        if 'hand_bbox' in hand and hand['hand_bbox'] is not None:
            try:
                bbox = hand['hand_bbox']
                if hasattr(bbox, '__iter__') and len(bbox) >= 4:
                    # Convert tensor to numpy if needed
                    if hasattr(bbox, 'cpu'):
                        bbox = bbox.cpu().numpy()
                    x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(overlay, "RIGHT HAND", (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    hand_data['bbox'] = [x1, y1, x2, y2]
            except Exception as bbox_error:
                print("BBOX_ERROR: " + str(bbox_error))
        
        # Draw keypoints safely
        keypoints_2d = []
        if 'wilor_preds' in hand and hand['wilor_preds'] is not None:
            try:
                wilor_data = hand['wilor_preds']
                if 'pred_keypoints_2d' in wilor_data and wilor_data['pred_keypoints_2d'] is not None:
                    keypoints_raw = wilor_data['pred_keypoints_2d']
                    
                    # Handle different data structures
                    if hasattr(keypoints_raw, 'cpu'):  # PyTorch tensor
                        points = keypoints_raw.cpu().numpy()[0]
                    elif hasattr(keypoints_raw, '__iter__'):  # List or numpy array
                        points = np.array(keypoints_raw[0]) if len(keypoints_raw) > 0 else []
                    else:
                        points = []
                    
                    for i, point in enumerate(points):
                        try:
                            x, y = float(point[0]), float(point[1])
                            keypoints_2d.append([x, y])
                            
                            if i in [4, 8, 12, 16, 20]:  # Fingertips
                                color = (0, 255, 255)  # Yellow
                                radius = 8
                            else:  # Other joints
                                color = (255, 255, 0)  # Blue
                                radius = 5
                                
                            cv2.circle(overlay, (int(x), int(y)), radius, color, -1)
                        except Exception as point_error:
                            print("POINT_ERROR: " + str(point_error))
                            continue
                            
            except Exception as keypoint_error:
                print("KEYPOINT_ERROR: " + str(keypoint_error))
        
        hand_data['keypoints_2d'] = keypoints_2d
        
        # Save overlay and data
        cv2.imwrite("temp_web_output.jpg", overlay)
        with open("temp_web_data.json", "w") as f:
            json.dump(hand_data, f)
        
        print("PROCESSING_COMPLETE")
        print("KEYPOINTS_COUNT: " + str(len(keypoints_2d)))
        
        # Clean up
        del estimator
        import gc
        gc.collect()
        
    except Exception as e:
        import traceback
        print("ERROR: " + str(e))
        print("TRACEBACK: " + str(traceback.format_exc()))

if __name__ == "__main__":
    process_frame()
"""
        
        # Write and execute processing script
        script_path = "temp_web_process.py"
        with open(script_path, "w") as f:
            f.write(script_content)
        
        # Run WiLoR processing in hand-teleop environment
        cmd = ["/mnt/nvme0n1p8/conda-envs/hand-teleop/bin/python", script_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, 
                              cwd="/home/jonas-petersen/dev/hand-teleop")
        
        # Check results
        if "NO_HAND_DETECTED" in result.stdout:
            return {
                "success": False,
                "message": "No hand detected in image",
                "hand_detected": False
            }
        elif "PROCESSING_COMPLETE" not in result.stdout:
            error_msg = result.stderr if result.stderr else "Processing failed"
            stdout_msg = result.stdout if result.stdout else "No output"
            print(f"DEBUG - Return code: {result.returncode}")
            print(f"DEBUG - STDOUT: {stdout_msg}")
            print(f"DEBUG - STDERR: {error_msg}")
            raise HTTPException(status_code=500, detail=f"WiLoR processing error: {error_msg} | STDOUT: {stdout_msg[:200]}")
        
        # Load results
        if not os.path.exists(temp_output):
            raise HTTPException(status_code=500, detail="Overlay image not generated")
            
        overlay = cv2.imread(temp_output)
        
        # Load hand data
        hand_data = {}
        if os.path.exists("temp_web_data.json"):
            with open("temp_web_data.json", "r") as f:
                hand_data = json.load(f)
        
        keypoints_2d = hand_data.get('keypoints_2d', [])
        
        # Convert overlay to base64 for web transfer
        _, buffer = cv2.imencode('.jpg', overlay)
        overlay_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Clean up temporary files
        for temp_file in [temp_input, temp_output, script_path, "temp_web_data.json"]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        # Clean up memory
        del frame, overlay
        gc.collect()
        
        return {
            "success": True,
            "message": "Hand detected and processed successfully",
            "hand_detected": True,
            "overlay_image": f"data:image/jpeg;base64,{overlay_base64}",
            "hand_data": hand_data,
            "keypoint_count": len(keypoints_2d)
        }
        
    except Exception as e:
        print(f"Error processing hand: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/process-webcam")
async def process_webcam_frame():
    """
    Capture frame from webcam and process
    Note: This is a simplified version - in production you'd want to handle
    webcam access differently for security
    """
    try:
        # Capture frame from default camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Could not access webcam")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        # Save temporarily and process
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, frame)
            
            # Read as upload file format
            with open(tmp_file.name, 'rb') as f:
                file_data = f.read()
            
            # Clean up temp file
            os.unlink(tmp_file.name)
        
        # Create mock UploadFile
        class MockUploadFile:
            def __init__(self, data):
                self.file_data = data
                self.content_type = "image/jpeg"
            
            async def read(self):
                return self.file_data
        
        mock_file = MockUploadFile(file_data)
        return await process_hand(mock_file)
        
    except Exception as e:
        print(f"Error with webcam capture: {e}")
        raise HTTPException(status_code=500, detail=f"Webcam error: {str(e)}")

# Mount static files (for CSS, JS, etc.)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("web_api:app", host="0.0.0.0", port=8000, reload=False)
