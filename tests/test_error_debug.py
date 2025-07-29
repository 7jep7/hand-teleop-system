#!/usr/bin/env python3
"""
Minimal test to identify the exact error location
"""
import cv2
import json
import numpy as np

def test_minimal_error():
    try:
        # Create test image with hand-like shape
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some features that might trigger hand detection
        cv2.rectangle(frame, (200, 150), (400, 350), (200, 200, 200), -1)  # Hand palm
        cv2.circle(frame, (220, 120), 20, (180, 180, 180), -1)  # Finger 1
        cv2.circle(frame, (260, 110), 20, (180, 180, 180), -1)  # Finger 2
        cv2.circle(frame, (300, 120), 20, (180, 180, 180), -1)  # Finger 3
        cv2.circle(frame, (340, 130), 20, (180, 180, 180), -1)  # Finger 4
        cv2.circle(frame, (380, 150), 20, (180, 180, 180), -1)  # Thumb
        
        cv2.imwrite("test_hand_image.jpg", frame)
        print("✅ Test image created")
        
        # Load WiLoR
        from hand_teleop.hand_pose.factory import create_estimator
        estimator = create_estimator("wilor")
        print("✅ WiLoR loaded")
        
        # Process
        result = estimator.pipe.predict(frame, hand="right")
        print(f"✅ Prediction complete: {len(result) if result else 0} hands detected")
        
        if result and len(result) > 0:
            hand = result[0]
            print("✅ Hand detected, testing data access...")
            
            # Test each access pattern that might cause the error
            print("🔍 Testing hand_bbox access...")
            if 'hand_bbox' in hand:
                bbox = hand['hand_bbox']
                print(f"  - bbox type: {type(bbox)}")
                print(f"  - bbox: {bbox}")
                
                # Test conversion - this might be where the error occurs
                try:
                    bbox_list = [int(x) for x in bbox]
                    print(f"  - bbox converted: {bbox_list}")
                except Exception as e:
                    print(f"  - bbox conversion error: {e}")
                    print(f"  - trying alternative conversion...")
                    try:
                        if hasattr(bbox, 'cpu'):
                            bbox_numpy = bbox.cpu().numpy()
                            bbox_list = [int(x) for x in bbox_numpy]
                            print(f"  - bbox tensor converted: {bbox_list}")
                    except Exception as e2:
                        print(f"  - tensor conversion also failed: {e2}")
            
            print("🔍 Testing wilor_preds access...")
            if 'wilor_preds' in hand:
                wilor_data = hand['wilor_preds']
                print(f"  - wilor_data type: {type(wilor_data)}")
                
                if 'pred_keypoints_2d' in wilor_data:
                    keypoints = wilor_data['pred_keypoints_2d']
                    print(f"  - keypoints type: {type(keypoints)}")
                    
                    # Test keypoint access - this might also cause issues
                    try:
                        if hasattr(keypoints, 'cpu'):
                            keypoints_numpy = keypoints.cpu().numpy()
                            print(f"  - keypoints shape: {keypoints_numpy.shape}")
                            if len(keypoints_numpy) > 0:
                                points = keypoints_numpy[0]
                                print(f"  - first hand points shape: {points.shape}")
                                for i, (x, y) in enumerate(points[:3]):  # Test first 3 points
                                    print(f"    - point {i}: ({float(x)}, {float(y)})")
                        else:
                            points = keypoints[0]
                            print(f"  - direct points shape: {points.shape if hasattr(points, 'shape') else 'no shape'}")
                    except Exception as e:
                        print(f"  - keypoints access error: {e}")
                        import traceback
                        traceback.print_exc()
                        
        else:
            print("❌ No hand detected")
            
    except Exception as e:
        print(f"💥 Main error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal_error()
