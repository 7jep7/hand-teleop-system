#!/usr/bin/env python3
"""
Quick WebSocket test for the Hand Teleop API
"""
import asyncio
import websockets
import json
import base64
import numpy as np
import cv2

async def test_websocket():
    uri = "ws://localhost:8000/api/tracking/live"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket connected successfully")
            
            # Test ping
            ping_msg = json.dumps({"type": "ping"})
            await websocket.send(ping_msg)
            
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            pong_data = json.loads(response)
            
            if pong_data.get("type") == "pong":
                print("✓ Ping-pong test successful")
            else:
                print("✗ Unexpected ping response:", pong_data)
            
            # Test image processing
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            _, buffer = cv2.imencode('.jpg', test_img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            image_msg = json.dumps({
                "type": "image",
                "data": img_base64,
                "robot_type": "so101"
            })
            
            await websocket.send(image_msg)
            print("✓ Test image sent")
            
            # Wait for tracking result
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            result_data = json.loads(response)
            
            if result_data.get("type") == "tracking_result":
                print("✓ Tracking result received")
                data = result_data["data"]
                print(f"  - Success: {data['success']}")
                print(f"  - Hand detected: {data['hand_detected']}")
                print(f"  - Processing time: {data['processing_time_ms']:.1f}ms")
            else:
                print("✗ Unexpected tracking response:", result_data)
                
    except asyncio.TimeoutError:
        print("✗ WebSocket test timed out")
    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
