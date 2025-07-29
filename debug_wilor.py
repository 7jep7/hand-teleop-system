#!/usr/bin/env python3
"""
Debug script to understand WiLoR data structure
"""
import cv2
import json
import sys
import traceback

def debug_wilor():
    try:
        print("🔍 Starting WiLoR debug...")
        
        # Load WiLoR
        from hand_teleop.hand_pose.factory import create_estimator
        print("✅ WiLoR factory imported")
        
        estimator = create_estimator("wilor")
        print("✅ WiLoR estimator created")
        
        # Create a simple test image
        import numpy as np
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a simple white rectangle to simulate a hand
        cv2.rectangle(test_frame, (200, 150), (400, 350), (255, 255, 255), -1)
        
        print("✅ Test frame created")
        
        # Process with WiLoR
        result = estimator.pipe.predict(test_frame, hand="right")
        print(f"✅ WiLoR prediction complete. Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if result else 'None'}")
        
        if result and len(result) > 0:
            hand = result[0]
            print(f"📋 Hand data type: {type(hand)}")
            print(f"📋 Hand keys: {list(hand.keys()) if isinstance(hand, dict) else 'Not a dict'}")
            
            # Check hand_bbox
            if 'hand_bbox' in hand:
                bbox = hand['hand_bbox']
                print(f"📦 Bbox type: {type(bbox)}")
                print(f"📦 Bbox value: {bbox}")
                print(f"📦 Bbox repr: {repr(bbox)}")
                
            # Check wilor_preds
            if 'wilor_preds' in hand:
                wilor_data = hand['wilor_preds']
                print(f"🎯 WiLoR preds type: {type(wilor_data)}")
                print(f"🎯 WiLoR preds keys: {list(wilor_data.keys()) if isinstance(wilor_data, dict) else 'Not a dict'}")
                
                if 'pred_keypoints_2d' in wilor_data:
                    keypoints = wilor_data['pred_keypoints_2d']
                    print(f"🔑 Keypoints type: {type(keypoints)}")
                    print(f"🔑 Keypoints shape: {keypoints.shape if hasattr(keypoints, 'shape') else 'No shape'}")
                    print(f"🔑 Keypoints repr: {repr(keypoints)}")
                    
                    # Try to access first element
                    if hasattr(keypoints, '__len__') and len(keypoints) > 0:
                        first_elem = keypoints[0]
                        print(f"🔑 First element type: {type(first_elem)}")
                        print(f"🔑 First element shape: {first_elem.shape if hasattr(first_elem, 'shape') else 'No shape'}")
                        
        else:
            print("❌ No hand detected or empty result")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        print(f"📚 Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_wilor()
