#!/usr/bin/env python3
"""
Integration Test Suite for Hand Teleop System
Tests frontend-backend communication and performance
"""

import requests
import time
import json
import base64
import cv2
import numpy as np
from datetime import datetime

def test_backend_health():
    """Test if backend is healthy and responsive"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   Dependencies: {len(data.get('dependencies', {}))} loaded")
            return True
        else:
            print(f"❌ Backend unhealthy (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_frontend_server():
    """Test if frontend server is accessible"""
    print("\n🌐 Testing frontend server...")
    try:
        response = requests.get("http://localhost:3000/web/web_interface.html", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is accessible!")
            print(f"   HTML size: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ Frontend server error (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_api_tracking():
    """Test the hand tracking API with sample image"""
    print("\n🤖 Testing hand tracking API...")
    try:
        # Create a simple test image (640x480 black image)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some white squares to simulate hand-like features
        cv2.rectangle(test_image, (200, 200), (250, 250), (255, 255, 255), -1)
        cv2.rectangle(test_image, (300, 180), (330, 220), (255, 255, 255), -1)
        cv2.rectangle(test_image, (350, 160), (380, 200), (255, 255, 255), -1)
        
        # Encode to base64
        _, buffer = cv2.imencode('.jpg', test_image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Test API
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/api/track",
            json={
                "image_data": f"data:image/jpeg;base64,{image_b64}",
                "robot_type": "so101",
                "tracking_mode": "mediapipe"
            },
            timeout=10
        )
        processing_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API tracking successful!")
            print(f"   Processing time: {processing_time:.1f}ms")
            print(f"   Backend time: {result.get('processing_time_ms', 'unknown')}ms")
            print(f"   Hand detected: {result.get('hand_detected', False)}")
            return True
        else:
            print(f"❌ API tracking failed (status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API tracking error: {e}")
        return False

def test_performance_metrics():
    """Test multiple API calls to check performance"""
    print("\n⚡ Testing performance with multiple calls...")
    try:
        # Simple test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(test_image, (320, 240), 50, (255, 255, 255), -1)
        
        _, buffer = cv2.imencode('.jpg', test_image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        times = []
        successes = 0
        
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.post(
                    "http://localhost:8000/api/track",
                    json={
                        "image_data": f"data:image/jpeg;base64,{image_b64}",
                        "robot_type": "so101",
                        "tracking_mode": "mediapipe"
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    successes += 1
                times.append((time.time() - start_time) * 1000)
            except:
                times.append(5000)  # Timeout
            
            time.sleep(0.1)  # Small delay between calls
        
        avg_time = sum(times) / len(times)
        print(f"✅ Performance test complete!")
        print(f"   Success rate: {successes}/5 ({successes*20}%)")
        print(f"   Average time: {avg_time:.1f}ms")
        print(f"   Times: {[f'{t:.1f}ms' for t in times]}")
        
        return successes >= 3  # At least 60% success rate
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def test_static_assets():
    """Test if static assets are accessible"""
    print("\n📁 Testing static assets...")
    assets_to_test = [
        "http://localhost:3000/web/web_interface.html",
        "http://localhost:3000/assets/urdf_loader.js",
        "http://localhost:3000/mvp-ui.js"
    ]
    
    successes = 0
    for asset in assets_to_test:
        try:
            response = requests.get(asset, timeout=3)
            if response.status_code == 200:
                print(f"   ✅ {asset.split('/')[-1]}")
                successes += 1
            else:
                print(f"   ❌ {asset.split('/')[-1]} (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ {asset.split('/')[-1]} (error: {e})")
    
    print(f"✅ Static assets: {successes}/{len(assets_to_test)} accessible")
    return successes >= len(assets_to_test) // 2

def main():
    """Run all integration tests"""
    print("🚀 Hand Teleop System - Integration Test Suite")
    print("=" * 50)
    print(f"📅 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Server", test_frontend_server),
        ("API Tracking", test_api_tracking),
        ("Performance", test_performance_metrics),
        ("Static Assets", test_static_assets)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Frontend and backend are working together!")
        print("\n🌐 Ready for testing:")
        print("   Frontend: http://localhost:3000/web/web_interface.html")
        print("   Backend API: http://localhost:8000/docs")
        print("   Health Check: http://localhost:8000/api/health")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
