#!/usr/bin/env python3
"""
Debug script with webcam capture
"""
import cv2
import json
import sys
import traceback

def debug_with_webcam():
    try:
        print("🔍 Starting webcam debug...")
        
        # Capture from webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open webcam")
            return
            
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("❌ Could not capture frame")
            return
            
        print("✅ Frame captured from webcam")
        cv2.imwrite("debug_capture.jpg", frame)
        
        # Load WiLoR
        from hand_teleop.hand_pose.factory import create_estimator
        print("✅ WiLoR factory imported")
        
        estimator = create_estimator("wilor")
        print("✅ WiLoR estimator created")
        
        # Process with WiLoR
        result = estimator.pipe.predict(frame, hand="right")
        print(f"✅ WiLoR prediction complete. Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if result else 'None'}")
        
        if result and len(result) > 0:
            hand = result[0]
            print(f"📋 Hand data type: {type(hand)}")
            print(f"📋 Hand keys: {list(hand.keys()) if isinstance(hand, dict) else 'Not a dict'}")
            
            # Save the hand data structure to JSON for inspection
            try:
                # Convert any tensors to lists for JSON serialization
                hand_copy = {}
                for key, value in hand.items():
                    try:
                        if hasattr(value, 'cpu'):  # PyTorch tensor
                            hand_copy[key] = value.cpu().numpy().tolist()
                        elif hasattr(value, 'tolist'):  # NumPy array
                            hand_copy[key] = value.tolist()
                        elif isinstance(value, dict):
                            # Handle nested dicts
                            nested_dict = {}
                            for nested_key, nested_value in value.items():
                                if hasattr(nested_value, 'cpu'):
                                    nested_dict[nested_key] = nested_value.cpu().numpy().tolist()
                                elif hasattr(nested_value, 'tolist'):
                                    nested_dict[nested_key] = nested_value.tolist()
                                else:
                                    nested_dict[nested_key] = str(nested_value)
                            hand_copy[key] = nested_dict
                        else:
                            hand_copy[key] = str(value)
                    except Exception as convert_error:
                        hand_copy[key] = f"Error converting: {convert_error}"
                        
                with open("debug_hand_data.json", "w") as f:
                    json.dump(hand_copy, f, indent=2)
                print("✅ Hand data saved to debug_hand_data.json")
            except Exception as json_error:
                print(f"❌ Could not save to JSON: {json_error}")
            
            # Check hand_bbox specifically
            if 'hand_bbox' in hand:
                bbox = hand['hand_bbox']
                print(f"📦 Bbox type: {type(bbox)}")
                print(f"📦 Bbox value: {bbox}")
                print(f"📦 Bbox repr: {repr(bbox)}")
                
                # Try to convert bbox
                try:
                    if hasattr(bbox, 'cpu'):
                        bbox_converted = bbox.cpu().numpy()
                        print(f"📦 Bbox converted: {bbox_converted}")
                    elif hasattr(bbox, '__iter__'):
                        bbox_list = list(bbox)
                        print(f"📦 Bbox as list: {bbox_list}")
                except Exception as bbox_error:
                    print(f"📦 Bbox conversion error: {bbox_error}")
                
            # Check wilor_preds
            if 'wilor_preds' in hand:
                wilor_data = hand['wilor_preds']
                print(f"🎯 WiLoR preds type: {type(wilor_data)}")
                if isinstance(wilor_data, dict):
                    print(f"🎯 WiLoR preds keys: {list(wilor_data.keys())}")
                    
                    if 'pred_keypoints_2d' in wilor_data:
                        keypoints = wilor_data['pred_keypoints_2d']
                        print(f"🔑 Keypoints type: {type(keypoints)}")
                        print(f"🔑 Keypoints shape: {keypoints.shape if hasattr(keypoints, 'shape') else 'No shape'}")
                        
                        # Try to convert keypoints
                        try:
                            if hasattr(keypoints, 'cpu'):
                                keypoints_converted = keypoints.cpu().numpy()
                                print(f"🔑 Keypoints converted shape: {keypoints_converted.shape}")
                                print(f"🔑 First few keypoints: {keypoints_converted[0][:5] if len(keypoints_converted) > 0 else 'Empty'}")
                        except Exception as keypoint_error:
                            print(f"🔑 Keypoint conversion error: {keypoint_error}")
                            
        else:
            print("❌ No hand detected or empty result")
            print("💡 Make sure your RIGHT hand is visible in the camera")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        print(f"📚 Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_with_webcam()
