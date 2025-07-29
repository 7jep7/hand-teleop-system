#!/usr/bin/env python3
"""
Ultra-simple WiLoR test: Take photo -> Process -> Save overlay
"""
import cv2
import sys

def main():
    print("📸 1) Taking photo...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera error")
        return
    
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("❌ Photo capture failed")
        return
    
    # Save original immediately
    cv2.imwrite("photo_original.jpg", frame)
    print("✅ Photo saved: photo_original.jpg")
    
    print("🧠 2) Loading WiLoR (this may take 30 seconds)...")
    try:
        from hand_teleop.hand_pose.factory import create_estimator
        estimator = create_estimator("wilor")
        print("✅ WiLoR loaded")
    except Exception as e:
        print(f"❌ WiLoR error: {e}")
        return
    
    print("🔄 3) Processing hand pose...")
    try:
        result = estimator.pipe.predict(frame, hand="right")
        
        if not result or len(result) == 0:
            print("❌ No hand detected")
            return
        
        hand = result[0]
        print("✅ Hand detected!")
        
        # Create overlay
        overlay = frame.copy()
        
        # Draw bounding box
        if 'hand_bbox' in hand:
            x1, y1, x2, y2 = [int(x) for x in hand['hand_bbox']]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(overlay, "RIGHT HAND", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw keypoints
        if 'wilor_preds' in hand and 'pred_keypoints_2d' in hand['wilor_preds']:
            points = hand['wilor_preds']['pred_keypoints_2d'][0]
            for i, (x, y) in enumerate(points):
                color = (0, 255, 255) if i in [4, 8, 12, 16, 20] else (255, 255, 0)  # Yellow for fingertips
                cv2.circle(overlay, (int(x), int(y)), 5, color, -1)
        
        # Save overlay immediately
        cv2.imwrite("photo_overlay.jpg", overlay)
        print("✅ Overlay saved: photo_overlay.jpg")
        
        # Clean up to prevent crashes
        del estimator
        import gc
        gc.collect()
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return
    
    print("🎉 Complete! Check photo_overlay.jpg")

if __name__ == "__main__":
    main()