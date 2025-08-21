#!/usr/bin/env python3
"""
Local Test Script for Hand Teleop System API
Tests the API endpoints locally before deployment
"""
import requests
import json
import base64
import numpy as np
import cv2
import time

def create_test_image():
    """Create a simple test image with a hand-like shape"""
    # Create a black image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Draw a simple hand-like shape (rectangle with fingers)
    # Palm
    cv2.rectangle(img, (200, 200), (350, 350), (255, 255, 255), -1)
    
    # Fingers
    cv2.rectangle(img, (180, 150), (200, 200), (255, 255, 255), -1)  # Thumb
    cv2.rectangle(img, (220, 120), (240, 200), (255, 255, 255), -1)  # Index
    cv2.rectangle(img, (260, 110), (280, 200), (255, 255, 255), -1)  # Middle
    cv2.rectangle(img, (300, 120), (320, 200), (255, 255, 255), -1)  # Ring
    cv2.rectangle(img, (340, 140), (360, 200), (255, 255, 255), -1)  # Pinky
    
    # Encode as base64
    _, buffer = cv2.imencode('.jpg', img)
    image_b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_b64}"

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test all API endpoints"""
    print("🧪 Testing Hand Teleop System API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing /api/health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Health: {health['status']} - Version: {health['version']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: List Robots
    print("2. Testing /api/robots...")
    try:
        response = requests.get(f"{base_url}/api/robots")
        if response.status_code == 200:
            robots = response.json()
            print(f"   ✅ Found {robots['total_count']} robot types")
            print(f"   Current: {robots['current_robot']}")
        else:
            print(f"   ❌ Robot list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Robot list error: {e}")
        return False
    
    # Test 3: Configure Robot
    print("3. Testing /api/config/robot...")
    try:
        config_data = {"robot_type": "so101", "settings": {"test": True}}
        response = requests.post(
            f"{base_url}/api/config/robot",
            json=config_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            config = response.json()
            print(f"   ✅ Robot configured: {config['message']}")
        else:
            print(f"   ❌ Robot config failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Robot config error: {e}")
        return False
    
    # Test 4: Hand Tracking
    print("4. Testing /api/track...")
    try:
        test_image = create_test_image()
        tracking_data = {
            "image_data": test_image,
            "robot_type": "so101",
            "tracking_mode": "mediapipe"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/track",
            json=tracking_data,
            headers={"Content-Type": "application/json"}
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Hand tracking completed in {response_time:.1f}ms")
            print(f"   Hand detected: {result['hand_detected']}")
            print(f"   Processing time: {result['processing_time_ms']:.1f}ms")
            if result['robot_joints']:
                print(f"   Robot joints: {len(result['robot_joints'])} values")
        else:
            print(f"   ❌ Hand tracking failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Hand tracking error: {e}")
        return False
    
    # Test 5: Demo Interface
    print("5. Testing /demo...")
    try:
        response = requests.get(f"{base_url}/demo")
        if response.status_code == 200 and "Hand Teleop System" in response.text:
            print(f"   ✅ Demo interface loaded ({len(response.text)} bytes)")
        else:
            print(f"   ❌ Demo interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Demo interface error: {e}")
        return False
    
    # Test 6: Legacy endpoints
    print("6. Testing legacy endpoints...")
    try:
        # Test root redirect
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if response.status_code in [200, 302]:
            print(f"   ✅ Root endpoint working")
        
        # Test legacy health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"   ✅ Legacy health endpoint working")
        
    except Exception as e:
        print(f"   ❌ Legacy endpoints error: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print(f"🌐 API is running successfully at {base_url}")
    print(f"📱 Demo interface: {base_url}/demo")
    return True

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the server is running with: python3 backend/render_backend.py")
    print()
    
    # Wait a moment for user to start server
    input("Press Enter when the server is running...")
    
    success = test_api_endpoints()
    
    if success:
        print("\n✅ API is ready for deployment!")
        print("\n📋 Integration URLs for jonaspetersen.com:")
        print("   API Base: https://your-render-url.com")
        print("   Health: https://your-render-url.com/api/health")
        print("   Demo: https://your-render-url.com/demo")
        print("   WebSocket: wss://your-render-url.com/api/tracking/live")
    else:
        print("\n❌ Some tests failed. Check the server logs.")
