#!/usr/bin/env python3
"""
MVP Backend Bridge - Connects MediaPipe fingertip detection to web UI
Real-time WebSocket integration for live demo
"""

import asyncio
import websockets
import json
import cv2
import numpy as np
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hand_pose.factory import HandPoseEstimatorFactory
from core.hand_pose.types import TrackedHandKeypoints


class MVPBackendBridge:
    def __init__(self):
        self.estimator = None
        self.cap = None
        self.running = False
        self.clients = set()
        
        # Performance tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = datetime.now()
        
    async def initialize(self):
        """Initialize MediaPipe and webcam"""
        try:
            # Initialize hand pose estimator (MediaPipe)
            self.estimator = HandPoseEstimatorFactory.create_estimator('mediapipe')
            print("✓ MediaPipe estimator initialized")
            
            # Initialize webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("Cannot open webcam")
            
            # Set webcam properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("✓ Webcam initialized (640x480 @ 30fps)")
            return True
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            return False
    
    async def process_frame(self):
        """Process single frame and extract fingertips"""
        if not self.cap or not self.estimator:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        try:
            # Run hand pose estimation
            result = self.estimator.estimate(frame)
            
            if result and result.hands and len(result.hands) > 0:
                # Get first detected hand
                hand = result.hands[0]
                
                # Extract our MVP fingertips
                fingertips = {
                    'thumb_tip': {
                        'x': float(hand.thumb_tip[0]) if hand.thumb_tip else 0,
                        'y': float(hand.thumb_tip[1]) if hand.thumb_tip else 0,
                        'z': float(hand.thumb_tip[2]) if hand.thumb_tip and len(hand.thumb_tip) > 2 else 0
                    },
                    'index_pip': {
                        'x': float(hand.index_pip[0]) if hand.index_pip else 0,
                        'y': float(hand.index_pip[1]) if hand.index_pip else 0,
                        'z': float(hand.index_pip[2]) if hand.index_pip and len(hand.index_pip) > 2 else 0
                    },
                    'index_tip': {
                        'x': float(hand.index_tip[0]) if hand.index_tip else 0,
                        'y': float(hand.index_tip[1]) if hand.index_tip else 0,
                        'z': float(hand.index_tip[2]) if hand.index_tip and len(hand.index_tip) > 2 else 0
                    }
                }
                
                # Update performance metrics
                self.update_fps()
                
                return {
                    'type': 'fingertips',
                    'timestamp': datetime.now().isoformat(),
                    'fps': self.fps,
                    'fingertips': fingertips,
                    'frame_size': {'width': frame.shape[1], 'height': frame.shape[0]}
                }
                
            else:
                # No hand detected
                return {
                    'type': 'no_hand',
                    'timestamp': datetime.now().isoformat(),
                    'fps': self.fps
                }
                
        except Exception as e:
            print(f"Frame processing error: {e}")
            return {
                'type': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def update_fps(self):
        """Calculate and update FPS"""
        self.frame_count += 1
        now = datetime.now()
        
        if (now - self.last_fps_time).total_seconds() >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = now
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections from frontend"""
        print(f"New client connected: {websocket.remote_address}")
        self.clients.add(websocket)
        
        try:
            # Send initial status
            await websocket.send(json.dumps({
                'type': 'status',
                'message': 'Connected to MVP backend',
                'timestamp': datetime.now().isoformat()
            }))
            
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON message'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {websocket.remote_address}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def handle_client_message(self, websocket, data):
        """Handle messages from frontend clients"""
        msg_type = data.get('type')
        
        if msg_type == 'start_tracking':
            self.running = True
            await websocket.send(json.dumps({
                'type': 'tracking_started',
                'message': 'Hand tracking started',
                'timestamp': datetime.now().isoformat()
            }))
            
        elif msg_type == 'stop_tracking':
            self.running = False
            await websocket.send(json.dumps({
                'type': 'tracking_stopped',
                'message': 'Hand tracking stopped',
                'timestamp': datetime.now().isoformat()
            }))
            
        elif msg_type == 'get_status':
            await websocket.send(json.dumps({
                'type': 'status_response',
                'running': self.running,
                'fps': self.fps,
                'clients': len(self.clients),
                'timestamp': datetime.now().isoformat()
            }))
    
    async def broadcast_data(self, data):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return
            
        message = json.dumps(data)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                print(f"Broadcast error to {client.remote_address}: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected
    
    async def main_loop(self):
        """Main processing loop"""
        print("Starting MVP backend bridge...")
        
        if not await self.initialize():
            print("Failed to initialize. Exiting.")
            return
        
        # Start WebSocket server
        server = await websockets.serve(
            self.websocket_handler,
            "localhost",
            8765,
            ping_interval=20,
            ping_timeout=10
        )
        
        print("✓ WebSocket server started on ws://localhost:8765")
        print("✓ MVP Backend Bridge ready!")
        print("\nTo test:")
        print("1. Open frontend/mvp-interface.html in a browser")
        print("2. Click 'Start Hand Tracking'")
        print("3. Show your hand to the webcam")
        print("\nPress Ctrl+C to stop")
        
        try:
            # Main processing loop
            while True:
                if self.running and self.clients:
                    # Process frame and send to clients
                    frame_data = await self.process_frame()
                    if frame_data:
                        await self.broadcast_data(frame_data)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.033)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            # Cleanup
            if self.cap:
                self.cap.release()
            server.close()
            await server.wait_closed()
            print("✓ Cleanup complete")


if __name__ == "__main__":
    bridge = MVPBackendBridge()
    try:
        asyncio.run(bridge.main_loop())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
