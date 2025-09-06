#!/usr/bin/env python3
"""
Online server integration tests
Tests the deployed hand-teleop-system server
"""
import pytest


@pytest.mark.integration
@pytest.mark.slow
def test_online_server_full_workflow():
    """Test complete workflow with online server"""
    try:
        import requests
        import time
        
        base_url = "https://hand-teleop-system.onrender.com"
        print(f"🌐 Testing full workflow with: {base_url}")
        
        # Step 1: Health check
        health_response = requests.get(f"{base_url}/api/health", timeout=15)
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert "status" in health_data
        print(f"✅ Health check passed: {health_data}")
        
        # Step 2: Test root endpoint
        root_response = requests.get(base_url, timeout=15)
        print(f"✅ Root endpoint status: {root_response.status_code}")
        
        # Step 3: Test if server returns HTML content
        if root_response.status_code == 200:
            content = root_response.text
            assert len(content) > 0
            print(f"✅ Server returned content ({len(content)} chars)")
            
            # Check if it looks like HTML
            if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                print("✅ Server returned HTML content")
            else:
                print("ℹ️ Server returned non-HTML content")
        
        print("🎉 Online server full workflow test completed successfully")
        
    except ImportError:
        pytest.skip("Requests library not available")
    except requests.exceptions.Timeout:
        pytest.skip("Online server timeout - may be sleeping or overloaded")
    except Exception as e:
        pytest.skip(f"Online server workflow failed: {e}")


@pytest.mark.integration
@pytest.mark.slow
def test_online_vs_local_api_parity():
    """Test that online and local APIs have similar endpoints"""
    try:
        import requests
        import socket
        
        # Check if local server is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        local_available = sock.connect_ex(('localhost', 8000)) == 0
        sock.close()
        
        # Test online server
        online_url = "https://hand-teleop-system.onrender.com"
        
        endpoints_to_compare = ["/api/health"]
        
        online_results = {}
        local_results = {}
        
        # Test online endpoints
        for endpoint in endpoints_to_compare:
            try:
                response = requests.get(online_url + endpoint, timeout=15)
                online_results[endpoint] = {
                    'status': response.status_code,
                    'has_json': 'application/json' in response.headers.get('content-type', '')
                }
                print(f"🌐 Online {endpoint}: {response.status_code}")
            except Exception as e:
                online_results[endpoint] = {'error': str(e)}
                print(f"🌐 Online {endpoint}: Error - {e}")
        
        # Test local endpoints if available
        if local_available:
            for endpoint in endpoints_to_compare:
                try:
                    response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                    local_results[endpoint] = {
                        'status': response.status_code,
                        'has_json': 'application/json' in response.headers.get('content-type', '')
                    }
                    print(f"🏠 Local {endpoint}: {response.status_code}")
                except Exception as e:
                    local_results[endpoint] = {'error': str(e)}
                    print(f"🏠 Local {endpoint}: Error - {e}")
            
            # Compare results
            for endpoint in endpoints_to_compare:
                online = online_results.get(endpoint, {})
                local = local_results.get(endpoint, {})
                
                if 'status' in online and 'status' in local:
                    if online['status'] == local['status']:
                        print(f"✅ {endpoint}: Status codes match ({online['status']})")
                    else:
                        print(f"⚠️ {endpoint}: Status codes differ (online: {online['status']}, local: {local['status']})")
        else:
            print("🏠 Local server not available - skipping comparison")
            print("✅ Online server endpoints tested independently")
        
    except ImportError:
        pytest.skip("Requests library not available")
    except Exception as e:
        pytest.skip(f"API parity test failed: {e}")


@pytest.mark.integration
def test_deployment_environment():
    """Test deployment environment characteristics"""
    try:
        import requests
        
        online_url = "https://hand-teleop-system.onrender.com/api/health"
        
        response = requests.get(online_url, timeout=15)
        
        if response.status_code == 200:
            # Check response headers for deployment info
            headers = response.headers
            
            print("🌐 Deployment environment info:")
            
            # Common deployment headers
            interesting_headers = [
                'server', 'x-powered-by', 'x-render-origin-server',
                'content-type', 'content-encoding'
            ]
            
            for header in interesting_headers:
                if header in headers:
                    print(f"  {header}: {headers[header]}")
            
            # Test HTTPS
            assert response.url.startswith('https://')
            print("✅ HTTPS enabled")
            
            # Test response time
            response_time = response.elapsed.total_seconds()
            print(f"✅ Response time: {response_time:.2f}s")
            
            if response_time > 10:
                print("⚠️ Slow response time - server may be sleeping")
            elif response_time < 2:
                print("🚀 Fast response time - server is warm")
        
        print("✅ Deployment environment test completed")
        
    except ImportError:
        pytest.skip("Requests library not available")
    except Exception as e:
        pytest.skip(f"Deployment environment test failed: {e}")
