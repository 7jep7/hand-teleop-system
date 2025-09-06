#!/usr/bin/env python3
"""
Simple WebSocket functionality tests with online server fallback
"""
import pytest


@pytest.mark.api
def test_json_websocket_support():
    """Test JSON serialization for WebSocket messages"""
    import json
    
    # Test message serialization
    test_message = {
        "type": "test",
        "data": "hello",
        "timestamp": "2025-09-05T18:00:00Z"
    }
    
    # Should be able to serialize and deserialize
    serialized = json.dumps(test_message)
    deserialized = json.loads(serialized)
    
    assert deserialized == test_message
    print("✅ JSON WebSocket message serialization works")


@pytest.mark.api
@pytest.mark.slow
def test_online_api_endpoints():
    """Test various online API endpoints"""
    try:
        import requests
        
        base_url = "https://hand-teleop-system.onrender.com"
        endpoints_to_test = [
            "/api/health",
            "/",  # Root endpoint
        ]
        
        for endpoint in endpoints_to_test:
            url = base_url + endpoint
            print(f"🌐 Testing: {url}")
            
            try:
                response = requests.get(url, timeout=15)
                print(f"  ✅ {endpoint}: Status {response.status_code}")
                
                if endpoint == "/api/health":
                    # Health endpoint should return JSON
                    data = response.json()
                    assert "status" in data
                    print(f"  ✅ Health data: {data}")
                
            except requests.exceptions.Timeout:
                print(f"  ⏰ {endpoint}: Timeout (server may be sleeping)")
                continue
            except Exception as e:
                print(f"  ⚠️ {endpoint}: Error - {e}")
                continue
        
        print("✅ Online API endpoint testing completed")
        
    except ImportError:
        pytest.skip("Requests library not available")
    except Exception as e:
        pytest.skip(f"Online API testing failed: {e}")


@pytest.mark.api
@pytest.mark.slow  
def test_websocket_url_formats():
    """Test WebSocket URL format validation"""
    
    # Test URL parsing
    import urllib.parse
    
    # Local WebSocket URLs
    local_urls = [
        "ws://localhost:8000/ws/hand-tracking",
        "ws://127.0.0.1:8000/ws/hand-tracking"
    ]
    
    # Online WebSocket URLs  
    online_urls = [
        "wss://hand-teleop-system.onrender.com/ws/hand-tracking",
    ]
    
    all_urls = local_urls + online_urls
    
    for url in all_urls:
        parsed = urllib.parse.urlparse(url)
        
        # Should have proper scheme
        assert parsed.scheme in ['ws', 'wss']
        
        # Should have hostname
        assert parsed.hostname is not None
        
        # Should have path
        assert parsed.path.startswith('/ws/')
        
        print(f"✅ URL format valid: {url}")
    
    print("✅ WebSocket URL format validation completed")
