#!/usr/bin/env python3
"""
Debug script to find the exact source of the 'unhashable type: dict' error
"""

import cv2
import numpy as np
import json
import traceback

def test_wilor_processing():
    """Test WiLoR processing step by step to find the error"""
    try:
        print("🔍 Starting WiLoR debug test...")
        
        # Create a simple test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_image, "Test Image", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.imwrite("debug_test_image.jpg", test_image)
        print("✅ Test image created")
        
        # Load WiLoR
        print("🔄 Loading WiLoR...")
        from hand_teleop.hand_pose.factory import create_estimator
        estimator = create_estimator("wilor")
        print("✅ WiLoR loaded successfully")
        
        # Test with the test image
        print("🔄 Processing test image...")
        frame = cv2.imread("debug_test_image.jpg")
        result = estimator.pipe.predict(frame, hand="right")
        print(f"✅ WiLoR processing completed - result type: {type(result)}")
        print(f"📊 Result length: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            hand = result[0]
            print(f"🤚 Hand data type: {type(hand)}")
            print(f"🔍 Hand keys: {list(hand.keys()) if hasattr(hand, 'keys') else 'No keys'}")
            
            # Test each component that might cause issues
            if 'hand_bbox' in hand:
                bbox = hand['hand_bbox']
                print(f"📦 Bbox type: {type(bbox)}")
                print(f"📦 Bbox value: {bbox}")
                
                # Try to use bbox in a dict/set (this might trigger the error)
                try:
                    test_dict = {bbox: "test"}
                    print("✅ Bbox is hashable")
                except Exception as bbox_error:
                    print(f"❌ Bbox error: {bbox_error}")
            
            if 'wilor_preds' in hand:
                wilor_data = hand['wilor_preds']
                print(f"🎯 WiLoR preds type: {type(wilor_data)}")
                print(f"🎯 WiLoR preds keys: {list(wilor_data.keys()) if hasattr(wilor_data, 'keys') else 'No keys'}")
                
                if 'pred_keypoints_2d' in wilor_data:
                    keypoints = wilor_data['pred_keypoints_2d']
                    print(f"🔑 Keypoints type: {type(keypoints)}")
                    
                    # Try to use keypoints in a dict/set (this might trigger the error)
                    try:
                        test_dict = {str(keypoints): "test"}
                        print("✅ Keypoints are hashable as string")
                    except Exception as kp_error:
                        print(f"❌ Keypoints error: {kp_error}")
            
            # Try the whole hand object
            try:
                test_dict = {str(hand): "test"}
                print("✅ Hand object is hashable as string")
            except Exception as hand_error:
                print(f"❌ Hand object error: {hand_error}")
                
        else:
            print("🤷 No hand detected in test image")
        
        print("✅ Debug test completed successfully")
        
    except Exception as e:
        print(f"💥 Error in debug test: {e}")
        print(f"📍 Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_wilor_processing()
