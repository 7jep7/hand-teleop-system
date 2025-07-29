#!/usr/bin/env python3
"""
Debug script to capture a real hand image and test WiLoR processing
"""

import cv2
import numpy as np
import json
import traceback

def capture_and_test():
    """Load existing hand image and test WiLoR processing"""
    try:
        print("🔍 Starting hand image WiLoR test...")
        
        # Use existing hand image
        image_path = "captured_hand.jpg"
        print(f"📷 Loading existing image: {image_path}")
        
        frame = cv2.imread(image_path)
        if frame is None:
            print("❌ Could not load image")
            return
            
        print("✅ Hand image loaded successfully")
        
        # Load WiLoR
        print("🔄 Loading WiLoR...")
        from hand_teleop.hand_pose.factory import create_estimator
        estimator = create_estimator("wilor")
        print("✅ WiLoR loaded successfully")
        
        # Process the captured frame
        print("🔄 Processing captured frame...")
        result = estimator.pipe.predict(frame, hand="right")
        print(f"✅ WiLoR processing completed - result type: {type(result)}")
        print(f"📊 Result length: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            print("🤚 Hand detected! Analyzing data structure...")
            hand = result[0]
            print(f"🤚 Hand data type: {type(hand)}")
            print(f"🔍 Hand keys: {list(hand.keys()) if hasattr(hand, 'keys') else 'No keys'}")
            
            # Deep analysis of problematic data
            for key, value in hand.items():
                print(f"\n🔍 Key '{key}':")
                print(f"   Type: {type(value)}")
                print(f"   Hashable test:", end=" ")
                try:
                    # Test if this value can be used as a dict key
                    test_hash = hash(str(value))
                    print("✅ OK")
                except Exception as e:
                    print(f"❌ ERROR: {e}")
                
                # Special handling for tensors/arrays
                if hasattr(value, 'cpu'):
                    print(f"   Has .cpu() method (likely PyTorch tensor)")
                    try:
                        cpu_value = value.cpu()
                        print(f"   CPU version type: {type(cpu_value)}")
                    except Exception as e:
                        print(f"   CPU conversion error: {e}")
                
                if hasattr(value, 'numpy'):
                    print(f"   Has .numpy() method")
                    try:
                        numpy_value = value.numpy()
                        print(f"   Numpy version type: {type(numpy_value)}")
                    except Exception as e:
                        print(f"   Numpy conversion error: {e}")
            
            # Test the specific operations that might fail
            print("\n🧪 Testing potentially problematic operations...")
            
            # Test bbox operations
            if 'hand_bbox' in hand:
                bbox = hand['hand_bbox']
                print(f"📦 Testing bbox operations...")
                try:
                    # This is what the web API does
                    if hasattr(bbox, '__iter__') and len(bbox) >= 4:
                        if hasattr(bbox, 'cpu'):
                            bbox = bbox.cpu().numpy()
                        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                        print(f"   ✅ Bbox conversion successful: [{x1}, {y1}, {x2}, {y2}]")
                except Exception as e:
                    print(f"   ❌ Bbox conversion error: {e}")
                    traceback.print_exc()
            
            # Test keypoints operations
            if 'wilor_preds' in hand and hand['wilor_preds'] is not None:
                wilor_data = hand['wilor_preds']
                print(f"🎯 Testing keypoints operations...")
                try:
                    if 'pred_keypoints_2d' in wilor_data and wilor_data['pred_keypoints_2d'] is not None:
                        keypoints_raw = wilor_data['pred_keypoints_2d']
                        print(f"   Keypoints raw type: {type(keypoints_raw)}")
                        
                        # This is what the web API does
                        if hasattr(keypoints_raw, 'cpu'):  # PyTorch tensor
                            points = keypoints_raw.cpu().numpy()[0]
                        elif hasattr(keypoints_raw, '__iter__'):  # List or numpy array
                            points = np.array(keypoints_raw[0]) if len(keypoints_raw) > 0 else []
                        else:
                            points = []
                        
                        print(f"   ✅ Keypoints conversion successful: {len(points)} points")
                        
                        # Test point iteration
                        for i, point in enumerate(points[:3]):  # Test first 3 points
                            x, y = float(point[0]), float(point[1])
                            print(f"   Point {i}: ({x}, {y})")
                            
                except Exception as e:
                    print(f"   ❌ Keypoints conversion error: {e}")
                    traceback.print_exc()
            
            # Test JSON serialization
            print("\n📄 Testing JSON serialization...")
            try:
                hand_data = {"bbox": None, "keypoints_2d": []}
                
                # Add bbox if available
                if 'hand_bbox' in hand and hand['hand_bbox'] is not None:
                    bbox = hand['hand_bbox']
                    if hasattr(bbox, 'cpu'):
                        bbox = bbox.cpu().numpy()
                    if hasattr(bbox, '__iter__') and len(bbox) >= 4:
                        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
                        hand_data['bbox'] = [x1, y1, x2, y2]
                
                # Add keypoints if available
                if 'wilor_preds' in hand and hand['wilor_preds'] is not None:
                    wilor_data = hand['wilor_preds']
                    if 'pred_keypoints_2d' in wilor_data and wilor_data['pred_keypoints_2d'] is not None:
                        keypoints_raw = wilor_data['pred_keypoints_2d']
                        if hasattr(keypoints_raw, 'cpu'):
                            points = keypoints_raw.cpu().numpy()[0]
                        elif hasattr(keypoints_raw, '__iter__'):
                            points = np.array(keypoints_raw[0]) if len(keypoints_raw) > 0 else []
                        else:
                            points = []
                        
                        keypoints_2d = []
                        for point in points:
                            x, y = float(point[0]), float(point[1])
                            keypoints_2d.append([x, y])
                        
                        hand_data['keypoints_2d'] = keypoints_2d
                
                # Test JSON serialization
                json_str = json.dumps(hand_data)
                print(f"   ✅ JSON serialization successful: {len(json_str)} chars")
                
                # Test JSON deserialization
                restored_data = json.loads(json_str)
                print(f"   ✅ JSON deserialization successful")
                
            except Exception as e:
                print(f"   ❌ JSON error: {e}")
                traceback.print_exc()
                
        else:
            print("🤷 No hand detected in captured frame")
        
        print("✅ Debug test completed successfully")
        
    except Exception as e:
        print(f"💥 Error in debug test: {e}")
        print(f"📍 Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    capture_and_test()
