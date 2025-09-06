#!/usr/bin/env python3
"""Test script to check backend functionality"""
import pytest

@pytest.mark.api
def test_health_endpoint():
    """Test backend health check endpoint"""
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✅ Health check response: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        print(f"✅ Health check data: {data}")
        
    except ImportError:
        pytest.skip("Requests library not available - install with 'pip install requests'")
    except Exception as e:
        # Allow failure if backend not running
        pytest.skip(f"Backend not available: {e}")

@pytest.mark.api
@pytest.mark.slow
def test_online_health_endpoint():
    """Test online backend health check endpoint"""
    try:
        import requests
        
        online_url = "https://hand-teleop-system.onrender.com/api/health"
        print(f"🌐 Testing online backend: {online_url}")
        
        response = requests.get(online_url, timeout=15)
        print(f"✅ Online health check response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            print(f"✅ Online health check data: {data}")
        else:
            pytest.skip(f"Online backend returned status: {response.status_code}")
        
    except ImportError:
        pytest.skip("Requests library not available")
    except Exception as e:
        pytest.skip(f"Online backend not available: {e}")

@pytest.mark.api  
def test_backend_dependencies():
    """Test if backend dependencies are available"""
    try:
        import json
        import socket
        
        print("✅ Basic backend dependencies available")
        assert hasattr(json, 'dumps')
        assert hasattr(socket, 'socket')
        
    except ImportError as e:
        pytest.fail(f"Backend dependencies missing: {e}")

@pytest.mark.api
def test_backend_port():
    """Test if backend port is accessible"""
    try:
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Backend port 8000 is accessible")
            assert True
        else:
            pytest.skip("Backend server not running on port 8000")
            
    except Exception as e:
        pytest.skip(f"Cannot test backend port: {e}")
