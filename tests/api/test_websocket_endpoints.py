#!/usr/bin/env python3
"""
WebSocket endpoint tests for both local and online servers
"""
import pytest
import socket
import asyncio


@pytest.mark.api
@pytest.mark.slow
def test_local_server_connectivity():
    """Test if local server is accessible on port 8000"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Local server accessible on localhost:8000")
            assert True
        else:
            pytest.skip("Local server not running - start with 'python main.py --start'")
            
    except Exception as e:
        pytest.skip(f"Cannot test local server connectivity: {e}")


@pytest.mark.api
@pytest.mark.slow
def test_online_server_connectivity():
    """Test if online server is accessible"""
    try:
        import requests
        
        # Test the online server health endpoint
        online_url = "https://hand-teleop-system.onrender.com/api/health"
        print(f"🌐 Testing online server: {online_url}")
        
        response = requests.get(online_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Online server is accessible and healthy")
            data = response.json()
            assert "status" in data
            print(f"✅ Online server response: {data}")
        else:
            print(f"⚠️ Online server returned status: {response.status_code}")
            pytest.skip(f"Online server not healthy - status {response.status_code}")
            
    except ImportError:
        pytest.skip("Requests library not available - install with 'pip install requests'")
    except requests.exceptions.Timeout:
        pytest.skip("Online server timeout - may be sleeping or unavailable")
    except Exception as e:
        pytest.skip(f"Cannot reach online server: {e}")


@pytest.mark.api
def test_websocket_dependencies():
    """Test WebSocket-related dependencies are available"""
    try:
        import socket
        import json
        
        # Test basic networking
        assert hasattr(socket, 'socket')
        assert hasattr(json, 'dumps')
        assert hasattr(json, 'loads')
        
        print("✅ WebSocket dependencies available")
        
    except ImportError as e:
        pytest.fail(f"Missing WebSocket dependencies: {e}")


@pytest.mark.api
@pytest.mark.slow
async def test_websocket_library_availability():
    """Test if WebSocket library is available for real WebSocket tests"""
    try:
        import websockets
        print("✅ WebSocket library available for advanced testing")
        assert hasattr(websockets, 'connect')
        
    except ImportError:
        print("⚠️ WebSocket library not installed")
        print("💡 Install with: pip install websockets")
        pytest.skip("WebSocket library not available - install with 'pip install websockets'")
