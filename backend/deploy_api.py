"""
Simplified Web API for deployment
Uses MediaPipe for hand detection with PIL instead of OpenCV for better compatibility
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import base64
import json
import os
import mediapipe as mp
import uvicorn
from typing import Dict, Any
from PIL import Image, ImageDraw
import io

app = FastAPI(title="Hand Tracking API", version="1.0.0")

# Enable CORS for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jonaspetersen.com",
        "https://www.jonaspetersen.com",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

@app.get("/")
async def root():
    return {"message": "Hand Tracking API - Deployment Version", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Hand Tracking API is running"}

@app.post("/api/process-hand")
async def process_hand(file: UploadFile = File(...)):
    """
    Process uploaded image for hand detection using MediaPipe
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await file.read()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for MediaPipe
        image_np = np.array(image)
        
        # Process with MediaPipe
        results = hands.process(image_np)
        
        # Create overlay using PIL
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        hand_data = {"bbox": None, "keypoints_2d": []}
        
        if results.multi_hand_landmarks:
            # Hand detected
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract keypoints
            h, w = image.size[1], image.size[0]  # height, width
            keypoints_2d = []
            x_coords, y_coords = [], []
            
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                keypoints_2d.append([x, y])
                x_coords.append(x)
                y_coords.append(y)
                
                # Draw keypoint
                draw.ellipse([x-3, y-3, x+3, y+3], fill='yellow', outline='red', width=2)
            
            # Calculate bounding box
            if x_coords and y_coords:
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                padding = 20
                bbox = [
                    max(0, x_min - padding),
                    max(0, y_min - padding),
                    min(w, x_max + padding),
                    min(h, y_max + padding)
                ]
                hand_data['bbox'] = bbox
                
                # Draw bounding box
                draw.rectangle(bbox, outline='green', width=3)
                draw.text((bbox[0], bbox[1]-20), "HAND DETECTED", fill='green')
            
            # Draw connections between keypoints
            connections = mp_hands.HAND_CONNECTIONS
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(keypoints_2d) and end_idx < len(keypoints_2d):
                    start_point = keypoints_2d[start_idx]
                    end_point = keypoints_2d[end_idx]
                    draw.line([start_point[0], start_point[1], end_point[0], end_point[1]], 
                             fill='blue', width=2)
            
            hand_data['keypoints_2d'] = keypoints_2d
            
            # Convert overlay to base64
            buffer = io.BytesIO()
            overlay.save(buffer, format='JPEG')
            overlay_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                "success": True,
                "message": "Hand detected and processed successfully",
                "hand_detected": True,
                "overlay_image": f"data:image/jpeg;base64,{overlay_base64}",
                "hand_data": hand_data,
                "keypoint_count": len(keypoints_2d),
                "method": "MediaPipe"
            }
        else:
            # No hand detected
            return {
                "success": False,
                "message": "No hand detected in image",
                "hand_detected": False,
                "method": "MediaPipe"
            }
            
    except Exception as e:
        print(f"Error processing hand: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("deploy_api:app", host="0.0.0.0", port=port, reload=False)
