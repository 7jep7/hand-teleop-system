#!/usr/bin/env python3
"""
Test script for the fixed backend functionality
Tests all critical endpoints and WebSocket functionality
"""

import requests
import json
import base64
import cv2
import numpy as np
import asyncio
import websockets
import time

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/tracking/live"

def create_test_image():
    """Create a simple test image for testing"""
    # Create a 640x480 test image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Draw a simple hand-like shape for testing
    cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)  # Palm
    cv2.circle(img, (280, 200), 15, (255, 255, 255), -1)  # Finger 1
    cv2.circle(img, (300, 180), 15, (255, 255, 255), -1)  # Finger 2
    cv2.circle(img, (320, 170), 15, (255, 255, 255), -1)  # Finger 3
    cv2.circle(img, (340, 180), 15, (255, 255, 255), -1)  # Finger 4
    cv2.circle(img, (360, 200), 15, (255, 255, 255), -1)  # Finger 5
    
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_robots_endpoint():
    """Test the robots list endpoint"""
    print("🤖 Testing robots endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/robots")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_count']} robot types")
            print(f"   Current robot: {data['current_robot']}")
            return True
        else:
            print(f"❌ Robots endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Robots endpoint error: {e}")
        return False

def test_robot_config():
    """Test robot configuration endpoint"""
    print("⚙️ Testing robot configuration...")
    try:
        config_data = {
            "robot_type": "so101",
            "settings": {
                "tracking_mode": "wilor",
                "smoothing": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/config/robot",
            json=config_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Robot configured: {data['message']}")
            return True
        else:
            print(f"❌ Robot config failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Robot config error: {e}")
        return False

def test_hand_tracking():
    """Test the main hand tracking endpoint"""
    print("👋 Testing hand tracking endpoint...")
    try:
        test_image = create_test_image()
        
        track_data = {
            "image_data": test_image,
            "robot_type": "so101",
            "tracking_mode": "wilor"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/track",
            json=track_data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Allow more time for processing
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Hand tracking successful: {data['success']}")
            print(f"   Hand detected: {data['hand_detected']}")
            print(f"   Processing time: {data['processing_time_ms']:.1f}ms")
            print(f"   Message: {data['message']}")
            if data['robot_joints']:
                print(f"   Robot joints: {data['robot_joints']}")
            return True
        else:
            print(f"❌ Hand tracking failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Hand tracking error: {e}")
        return False

def test_performance_endpoint():
    """Test the performance monitoring endpoint"""
    print("📊 Testing performance endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/performance")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"✅ Performance stats retrieved")
            print(f"   Total requests: {stats['total_requests']}")
            print(f"   Successful: {stats['successful_requests']}")
            print(f"   Failed: {stats['failed_requests']}")
            print(f"   Avg processing time: {stats['average_processing_time']:.1f}ms")
            return True
        else:
            print(f"❌ Performance endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Performance endpoint error: {e}")
        return False

async def test_websocket():
    """Test WebSocket real-time tracking"""
    print("🔌 Testing WebSocket connection...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket connected")
            
            # Send ping
            ping_message = {
                "type": "ping"
            }
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            pong_data = json.loads(response)
            
            if pong_data.get("type") == "pong":
                print("✅ WebSocket ping/pong working")
            
            # Send test image
            test_image = create_test_image()
            image_message = {
                "type": "image",
                "data": test_image,
                "robot_type": "so101"
            }
            
            await websocket.send(json.dumps(image_message))
            
            # Wait for tracking result
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            result_data = json.loads(response)
            
            if result_data.get("type") == "tracking_result":
                tracking_data = result_data["data"]
                print("✅ WebSocket tracking successful")
                print(f"   Hand detected: {tracking_data.get('hand_detected')}")
                print(f"   Success: {tracking_data.get('success')}")
                return True
            else:
                print(f"❌ Unexpected WebSocket response: {result_data}")
                return False
                
    except asyncio.TimeoutError:
        print("❌ WebSocket timeout")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

def test_demo_page():
    """Test the demo page endpoint"""
    print("🎨 Testing demo page...")
    try:
        response = requests.get(f"{BASE_URL}/demo")
        if response.status_code == 200 and "Hand Teleop System" in response.text:
            print("✅ Demo page accessible")
            return True
        else:
            print(f"❌ Demo page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Demo page error: {e}")
        return False

async def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting backend functionality tests...\n")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Robots List", test_robots_endpoint),
        ("Robot Config", test_robot_config),
        ("Hand Tracking", test_hand_tracking),
        ("Performance Stats", test_performance_endpoint),
        ("Demo Page", test_demo_page),
    ]
    
    results = {}
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        print()  # Empty line for readability
    
    # Run WebSocket test separately
    try:
        print("Running WebSocket test...")
        results["WebSocket"] = await test_websocket()
    except Exception as e:
        print(f"❌ WebSocket test crashed: {e}")
        results["WebSocket"] = False
    
    print("\n" + "="*50)
    print("📋 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready for production.")
    else:
        print("⚠️  Some tests failed. Check the backend implementation.")
    
    return passed == total

if __name__ == "__main__":
    print("Backend Test Suite")
    print("Make sure the backend is running with: python backend/render_backend.py")
    print()
    
    # Run the tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
