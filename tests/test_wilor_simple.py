#!/usr/bin/env python3
"""
Simple WiLoR test - takes one photo and shows hand pose estimation with visualization
"""
import cv2
import numpy as np
from core.hand_pose.factory import create_estimator

def main():
    print("🤖 Simple WiLoR Hand Pose Test with Visualization")
    print("=" * 50)
    
    # Initialize camera
    print("📷 Opening camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return
    
    # Initialize WiLoR
    print("🧠 Loading WiLoR model...")
    print("⏳ This may take 20-30 seconds on first run (downloading model)...")
    print("🖥️  Your screen may freeze briefly - this is normal!")
    try:
        estimator = create_estimator("wilor")
        print("✅ WiLoR loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading WiLoR: {e}")
        print(f"🔍 Full error details:")
        import traceback
        traceback.print_exc()
        cap.release()
        return
    
    print("\n📸 Taking photo in 3 seconds...")
    print("Position your RIGHT hand in front of the camera!")
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"   {i}...")
        cv2.waitKey(1000)
    
    # Capture frame
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Could not capture frame")
        cap.release()
        return
    
    print("📸 Photo captured!")
    
    # Process with WiLoR
    print("🔄 Processing with WiLoR...")
    try:
        result = estimator.pipe.predict(frame, hand="right")
        
        if result is None or len(result) == 0:
            print("❌ No hand detected in the image")
        else:
            print("✅ Hand detected!")
            print(f"📊 Result type: {type(result)}")
            print(f"📊 Number of hands detected: {len(result)}")
            
            # Look at the first hand detection
            hand_result = result[0]
            print(f"📊 Hand result type: {type(hand_result)}")
            print(f"📊 Hand result keys: {list(hand_result.keys()) if isinstance(hand_result, dict) else 'Not a dict'}")
            
            # Check what's in the result
            if isinstance(hand_result, dict):
                for key, value in hand_result.items():
                    print(f"   {key}: {type(value)} - {getattr(value, 'shape', 'no shape') if hasattr(value, 'shape') else value}")
                    
                # If there are keypoints, show some details
                if 'wilor_preds' in hand_result and 'pred_keypoints_3d' in hand_result['wilor_preds']:
                    keypoints = hand_result['wilor_preds']['pred_keypoints_3d'][0]
                    print(f"\n🖐️  3D Keypoints shape: {keypoints.shape}")
                    print(f"📍 Sample keypoint (tip of index finger): {keypoints[8]}")  # Index finger tip
                    print(f"📈 Hand pose statistics:")
                    print(f"   X range: {keypoints[:, 0].min():.3f} to {keypoints[:, 0].max():.3f}")
                    print(f"   Y range: {keypoints[:, 1].min():.3f} to {keypoints[:, 1].max():.3f}")
                    print(f"   Z range: {keypoints[:, 2].min():.3f} to {keypoints[:, 2].max():.3f}")
                
                # Create visualization with overlays
                print("\n🎨 Creating visualization with WiLoR predictions...")
                viz_frame = frame.copy()
                
                # Draw bounding box
                if 'hand_bbox' in hand_result:
                    bbox = hand_result['hand_bbox']
                    x1, y1, x2, y2 = [int(coord) for coord in bbox]
                    cv2.rectangle(viz_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    
                    # Add hand type label
                    hand_type = "RIGHT" if hand_result.get('is_right', 0) > 0.5 else "LEFT"
                    cv2.putText(viz_frame, f"{hand_type} HAND", (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Draw 2D keypoints
                if 'wilor_preds' in hand_result and 'pred_keypoints_2d' in hand_result['wilor_preds']:
                    keypoints_2d = hand_result['wilor_preds']['pred_keypoints_2d'][0]  # First hand
                    
                    # Define hand landmark connections (MANO hand model)
                    connections = [
                        # Thumb
                        (0, 1), (1, 2), (2, 3), (3, 4),
                        # Index finger  
                        (0, 5), (5, 6), (6, 7), (7, 8),
                        # Middle finger
                        (0, 9), (9, 10), (10, 11), (11, 12),
                        # Ring finger
                        (0, 13), (13, 14), (14, 15), (15, 16),
                        # Pinky
                        (0, 17), (17, 18), (18, 19), (19, 20)
                    ]
                    
                    # Draw connections (bones)
                    for start_idx, end_idx in connections:
                        if start_idx < len(keypoints_2d) and end_idx < len(keypoints_2d):
                            start_point = tuple(map(int, keypoints_2d[start_idx]))
                            end_point = tuple(map(int, keypoints_2d[end_idx]))
                            cv2.line(viz_frame, start_point, end_point, (255, 0, 0), 2)
                    
                    # Draw keypoints
                    for i, (x, y) in enumerate(keypoints_2d):
                        x, y = int(x), int(y)
                        # Different colors for different finger parts
                        if i == 0:  # Wrist
                            color = (0, 0, 255)  # Red
                            radius = 8
                        elif i in [4, 8, 12, 16, 20]:  # Fingertips
                            color = (0, 255, 255)  # Yellow
                            radius = 6
                        else:  # Other joints
                            color = (255, 255, 0)  # Cyan
                            radius = 4
                        
                        cv2.circle(viz_frame, (x, y), radius, color, -1)
                        # Add point number for debugging
                        cv2.putText(viz_frame, str(i), (x+5, y-5), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                
                # Save the visualization
                cv2.imwrite("wilor_visualization.jpg", viz_frame)
                print("🎨 Saved visualization with WiLoR predictions as 'wilor_visualization.jpg'")
                
            else:
                print(f"   Hand result: {hand_result}")
                
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    
    # Save the captured image
    cv2.imwrite("captured_hand.jpg", frame)
    print("💾 Saved captured image as 'captured_hand.jpg'")
    
    # Cleanup
    cap.release()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()