#!/usr/bin/env python3
"""
SO-101 Robot Simulation Test Script
Tests the complete SO-101 system: backend API, WebSocket, and mock data
"""

import asyncio
import websockets
import json
import time
import requests
from pathlib import Path
import sys

# Add core modules to path
sys.path.append(str(Path(__file__).parent.parent))

from core.robot_control.mock_hand_data import get_mock_hand_data


class SO101TestClient:
    """Test client for SO-101 robot simulation."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws") + "/api/robot/so101/simulation"
        self.session = requests.Session()
        
    def test_api_endpoints(self):
        """Test REST API endpoints."""
        print("🔧 Testing SO-101 REST API Endpoints")
        print("=" * 50)
        
        # Test robot info endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/robot/so101/info")
            if response.status_code == 200:
                info = response.json()
                print(f"✅ Robot info: {info['robot_info']['name']} ({info['robot_info']['dof']} DOF)")
            else:
                print(f"❌ Robot info failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Robot info error: {e}")
        
        # Test robot state endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/robot/so101/state")
            if response.status_code == 200:
                state = response.json()
                positions = state['joint_state']['positions']
                print(f"✅ Robot state: {len(positions)} joints, positions: {[round(p, 2) for p in positions]}")
            else:
                print(f"❌ Robot state failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Robot state error: {e}")
        
        # Test setting joint positions
        try:
            test_positions = [0.1, -0.2, 0.3, -0.1, 0.5, 0.0]
            response = self.session.post(
                f"{self.base_url}/api/robot/so101/joints",
                json={"positions": test_positions, "smooth": True}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Set joints: {result['message']}")
            else:
                print(f"❌ Set joints failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Set joints error: {e}")
        
        # Test hand pose conversion
        try:
            mock_hand = get_mock_hand_data("wave")
            response = self.session.post(
                f"{self.base_url}/api/robot/so101/hand-pose",
                json={
                    "hand_landmarks": mock_hand["hand_landmarks"],
                    "apply": False
                }
            )
            if response.status_code == 200:
                result = response.json()
                joint_angles = result['joint_angles']
                print(f"✅ Hand pose conversion: {[round(a, 2) for a in joint_angles]}")
            else:
                print(f"❌ Hand pose conversion failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Hand pose conversion error: {e}")
    
    async def test_websocket(self):
        """Test WebSocket communication."""
        print("\n🌐 Testing SO-101 WebSocket Communication")
        print("=" * 50)
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                print("✅ WebSocket connected")
                
                # Test ping
                await websocket.send(json.dumps({"type": "ping"}))
                response = await websocket.recv()
                msg = json.loads(response)
                if msg["type"] == "pong":
                    print("✅ Ping/pong successful")
                
                # Test get robot info
                await websocket.send(json.dumps({"type": "get_info"}))
                response = await websocket.recv()
                msg = json.loads(response)
                if msg["type"] == "robot_info":
                    print(f"✅ Robot info via WebSocket: {msg['data']['name']}")
                
                # Test joint control
                test_joints = [0.2, -0.3, 0.4, -0.2, 0.6, 0.1]
                await websocket.send(json.dumps({
                    "type": "set_joints",
                    "positions": test_joints,
                    "smooth": True
                }))
                response = await websocket.recv()
                msg = json.loads(response)
                if msg["type"] == "joint_response" and msg["success"]:
                    print("✅ Joint control via WebSocket successful")
                
                # Test hand pose streaming
                print("🤚 Testing hand pose streaming...")
                motion_types = ["wave", "point", "grab"]
                
                for motion in motion_types:
                    mock_hand = get_mock_hand_data(motion)
                    await websocket.send(json.dumps({
                        "type": "hand_pose",
                        "hand_landmarks": mock_hand["hand_landmarks"]
                    }))
                    
                    response = await websocket.recv()
                    msg = json.loads(response)
                    if msg["type"] == "hand_pose_response" and msg["success"]:
                        joint_angles = msg["joint_angles"]
                        print(f"  ✅ {motion} motion → joints: {[round(a, 2) for a in joint_angles]}")
                    
                    # Small delay between motions
                    await asyncio.sleep(0.5)
                
                # Listen for robot state updates
                print("📊 Listening for robot state updates...")
                update_count = 0
                start_time = time.time()
                
                while update_count < 10 and (time.time() - start_time) < 5:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        msg = json.loads(response)
                        
                        if msg["type"] == "robot_state":
                            update_count += 1
                            if update_count == 1:
                                print("  ✅ Receiving real-time robot state updates")
                            elif update_count == 10:
                                fps = update_count / (time.time() - start_time)
                                print(f"  ✅ Update rate: {fps:.1f} Hz")
                                
                    except asyncio.TimeoutError:
                        break
                
                print("✅ WebSocket testing completed")
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    async def test_performance(self):
        """Test system performance and latency."""
        print("\n⚡ Testing Performance and Latency")
        print("=" * 50)
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Measure round-trip latency
                latencies = []
                
                for i in range(10):
                    start_time = time.time()
                    await websocket.send(json.dumps({"type": "ping"}))
                    response = await websocket.recv()
                    end_time = time.time()
                    
                    msg = json.loads(response)
                    if msg["type"] == "pong":
                        latency = (end_time - start_time) * 1000  # Convert to ms
                        latencies.append(latency)
                    
                    await asyncio.sleep(0.1)
                
                if latencies:
                    avg_latency = sum(latencies) / len(latencies)
                    min_latency = min(latencies)
                    max_latency = max(latencies)
                    
                    print(f"✅ Average latency: {avg_latency:.1f}ms")
                    print(f"   Min: {min_latency:.1f}ms, Max: {max_latency:.1f}ms")
                    
                    if avg_latency < 50:
                        print("   🟢 Excellent latency for real-time control")
                    elif avg_latency < 100:
                        print("   🟡 Good latency for real-time control")
                    else:
                        print("   🔴 High latency - may affect real-time performance")
                
                # Test throughput with hand pose data
                print("📈 Testing hand pose processing throughput...")
                
                start_time = time.time()
                processed_count = 0
                
                for i in range(50):
                    mock_hand = get_mock_hand_data("wave")
                    await websocket.send(json.dumps({
                        "type": "hand_pose",
                        "hand_landmarks": mock_hand["hand_landmarks"]
                    }))
                    
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        msg = json.loads(response)
                        if msg["type"] == "hand_pose_response" and msg["success"]:
                            processed_count += 1
                    except asyncio.TimeoutError:
                        break
                
                end_time = time.time()
                duration = end_time - start_time
                throughput = processed_count / duration
                
                print(f"✅ Hand pose throughput: {throughput:.1f} poses/second")
                
                if throughput >= 30:
                    print("   🟢 Excellent throughput for real-time hand tracking")
                elif throughput >= 15:
                    print("   🟡 Good throughput for hand tracking")
                else:
                    print("   🔴 Low throughput - may affect responsiveness")
                
        except Exception as e:
            print(f"❌ Performance test error: {e}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🤖 SO-101 Robot Simulation Test Suite")
        print("=" * 60)
        print(f"Testing server at: {self.base_url}")
        print(f"WebSocket endpoint: {self.ws_url}")
        print()
        
        # Test REST API
        self.test_api_endpoints()
        
        # Test WebSocket (async)
        asyncio.run(self.test_websocket())
        
        # Test performance (async)
        asyncio.run(self.test_performance())
        
        print("\n" + "=" * 60)
        print("✅ SO-101 Test Suite Completed!")
        print("\nNext steps:")
        print("1. Open http://localhost:8000/frontend/web/so101_simulation.html")
        print("2. Verify 3D robot visualization loads")
        print("3. Test joint controls and WebSocket connection")
        print("4. Real STL meshes now loaded for accurate robot rendering!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SO-101 Robot Simulation")
    parser.add_argument("--url", default="http://localhost:8000", 
                        help="Base URL of the server (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    # Run tests
    client = SO101TestClient(args.url)
    client.run_all_tests()
