#!/usr/bin/env python3
"""
Minimal WiLoR test - lightweight version to avoid crashes
"""
import cv2
import numpy as np
from core.hand_pose.factory import create_estimator
import sys

def main():
    print("🤖 Minimal WiLoR Test")
    print("=" * 30)
    
    try:
        # Initialize camera
        print("📷 Opening camera...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return False
        
        # Take a quick photo
        print("📸 Capturing frame...")
        ret, frame = cap.read()
        cap.release()  # Release camera immediately
        
        if not ret:
            print("❌ Error: Could not capture frame")
            return False
        
        print("✅ Frame captured, saving...")
        cv2.imwrite("test_frame.jpg", frame)
        
        # Initialize WiLoR (this is the heavy part)
        print("🧠 Loading WiLoR model (this may take time)...")
        estimator = create_estimator("wilor")
        print("✅ WiLoR loaded!")
        
        # Process the frame
        print("🔄 Processing frame...")
        result = estimator.pipe.predict(frame, hand="right")
        
        if result and len(result) > 0:
            print("✅ Hand detected!")
            hand_result = result[0]
            
            # Just print basic info to avoid complexity
            print(f"📊 Hand type: {'RIGHT' if hand_result.get('is_right', 0) > 0.5 else 'LEFT'}")
            print(f"📊 Bounding box: {hand_result.get('hand_bbox', 'N/A')}")
            
            if 'wilor_preds' in hand_result:
                wilor_data = hand_result['wilor_preds']
                if 'pred_keypoints_3d' in wilor_data:
                    kp3d = wilor_data['pred_keypoints_3d'][0]
                    print(f"🖐️  3D keypoints shape: {kp3d.shape}")
                    print(f"📍 Index fingertip: {kp3d[8]}")
            
            print("💾 Results saved to test_frame.jpg")
            return True
        else:
            print("❌ No hand detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
