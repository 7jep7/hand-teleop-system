#!/usr/bin/env python3
"""
Simple test for the hand tracking endpoint
"""
import requests
import json
import base64
import cv2
import numpy as np

def create_test_image():
    """Create a simple test image"""
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a simple hand-like shape
    cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)  # Palm
    cv2.circle(img, (280, 200), 15, (255, 255, 255), -1)  # Fingers
    cv2.circle(img, (300, 180), 15, (255, 255, 255), -1)
    cv2.circle(img, (320, 170), 15, (255, 255, 255), -1)
    cv2.circle(img, (340, 180), 15, (255, 255, 255), -1)
    cv2.circle(img, (360, 200), 15, (255, 255, 255), -1)
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"

def test_tracking():
    """Test the hand tracking endpoint"""
    print("Testing hand tracking endpoint...")
    
    test_image = create_test_image()
    
    track_data = {
        "image_data": test_image,
        "robot_type": "so101",
        "tracking_mode": "wilor"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/track",
            json=track_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Hand tracking successful!")
            print(f"   Success: {data['success']}")
            print(f"   Hand detected: {data['hand_detected']}")
            print(f"   Processing time: {data['processing_time_ms']:.1f}ms")
            print(f"   Message: {data['message']}")
            if data['robot_joints']:
                print(f"   Robot joints: {data['robot_joints']}")
            if data['hand_pose']:
                print(f"   Hand pose method: {data['hand_pose'].get('tracking_method', 'unknown')}")
            return True
        else:
            print(f"❌ Hand tracking failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Hand tracking error: {e}")
        return False

if __name__ == "__main__":
    test_tracking()
