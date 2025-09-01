#!/usr/bin/env python3
"""
WebSocket Connection Test for Both Backends
Tests both local and deployed WebSocket endpoints
"""
import asyncio
import websockets
import json
import sys

async def test_websocket(url, name):
    """Test WebSocket connection to a specific endpoint"""
    print(f"\n🔄 Testing {name}: {url}")
    
    try:
        # Connect to WebSocket
        async with websockets.connect(url, timeout=10) as websocket:
            print(f"✅ {name}: Connected successfully!")
            
            # Send ping message
            ping_msg = {"type": "ping", "timestamp": "test"}
            await websocket.send(json.dumps(ping_msg))
            print(f"📤 {name}: Sent ping message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                print(f"📥 {name}: Received response: {data}")
                return True
                
            except asyncio.TimeoutError:
                print(f"⏰ {name}: Timeout waiting for response")
                return False
                
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ {name}: Connection closed unexpectedly")
        return False
    except websockets.exceptions.InvalidURI:
        print(f"❌ {name}: Invalid WebSocket URI")
        return False
    except Exception as e:
        print(f"❌ {name}: Connection failed - {str(e)}")
        return False

async def main():
    """Test both local and deployed WebSocket endpoints"""
    print("🧪 WebSocket Backend Connectivity Test")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("ws://localhost:8000/api/tracking/live", "Local Backend"),
        ("wss://hand-teleop-api.onrender.com/api/tracking/live", "Deployed Backend")
    ]
    
    results = []
    for url, name in endpoints:
        success = await test_websocket(url, name)
        results.append((name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Both backends are working.")
        print("💡 Frontend can now be tested against either backend.")
    else:
        print("\n⚠️  Some tests failed. Check backend status.")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
