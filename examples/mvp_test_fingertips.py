#!/usr/bin/env python3
"""
MVP Test Script: Minimal Fingertip Detection
Test thumb tip, index PIP, and index tip extraction from MediaPipe
"""

import cv2
import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hand_pose.estimators.mediapipe import MediaPipeEstimator

def main():
    print("🚀 MVP Task 1: Testing Minimal Fingertip Detection")
    print("Extract thumb tip (#4), index PIP (#6), and index tip (#8)")
    print("Press 'q' to quit\n")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        return
    
    # Initialize MediaPipe estimator
    try:
        estimator = MediaPipeEstimator(num_hands=1)
        print("✅ MediaPipe estimator initialized")
    except Exception as e:
        print(f"❌ Error initializing MediaPipe: {e}")
        return
    
    # Camera parameters (approximate)
    f_px = 600.0  # focal length in pixels (approximate)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
            
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        try:
            hand_predictions = estimator(frame_rgb, f_px)
            
            # Display frame info every 30 frames
            if frame_count % 30 == 0:
                if hand_predictions:
                    print(f"\n📱 Frame {frame_count}: {len(hand_predictions)} hand(s) detected")
                else:
                    print(f"\n📱 Frame {frame_count}: No hands detected")
                    
        except Exception as e:
            print(f"❌ Error processing frame: {e}")
            
        # Display frame
        cv2.imshow('MVP Fingertip Detection', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        frame_count += 1
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ MVP Test completed!")

if __name__ == "__main__":
    main()
