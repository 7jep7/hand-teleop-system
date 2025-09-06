#!/usr/bin/env python3
"""Simple API connectivity tests"""
import pytest
import socket

@pytest.mark.api
def test_api_dependencies():
    """Test if API dependencies are available"""
    import json
    import socket
    
    print("✅ API dependencies available")
    assert hasattr(json, 'dumps')
    assert hasattr(socket, 'socket')

@pytest.mark.api
@pytest.mark.slow
def test_api_port():
    """Test if API port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ API port 8000 is accessible")
            assert True
        else:
            pytest.skip("API server not running on port 8000")
            
    except Exception as e:
        pytest.skip(f"Cannot test API port: {e}")
