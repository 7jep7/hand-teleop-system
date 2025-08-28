#!/usr/bin/env python3
"""
Test script for SO-101 robot hand teleoperation
"""
import argparse
import time
import numpy as np
from scipy.spatial.transform import Rotation as R

from core.robot_control.gripper_pose import GripperPose
from core.tracking.tracker import HandTracker

# SO-101 specific safe operating ranges (adjust based on your robot)
SO101_SAFE_RANGE = {
    "x": (0.10, 0.40),    # Forward/backward reach
    "y": (-0.25, 0.25),   # Left/right reach  
    "z": (0.005, 0.30),   # Up/down reach
    "g": (0, 90),         # Gripper opening (degrees)
}

def main():
    parser = argparse.ArgumentParser(description="Test hand-teleop with SO-101 robot")
    parser.add_argument("--model", choices=["wilor", "mediapipe", "apriltag"], 
                       default="wilor", help="Hand tracking model")
    parser.add_argument("--hand", choices=["left", "right"], default="right", 
                       help="Which hand to track")
    parser.add_argument("--cam-idx", type=int, default=0, help="Camera index")
    parser.add_argument("--fps", type=int, default=30, help="Target FPS")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--use-scroll", action="store_true", 
                       help="Use scroll wheel for gripper control")
    parser.add_argument("--pose-only", action="store_true", 
                       help="Test pose tracking only (no kinematics)")
    
    args = parser.parse_args()
    
    # Setup tracker with SO-101 URDF
    urdf_path = None if args.pose_only else "so101"
    
    print(f"🤖 Initializing hand tracker for SO-101...")
    print(f"   Model: {args.model}")
    print(f"   Hand: {args.hand}")
    print(f"   Camera: {args.cam_idx}")
    print(f"   URDF: {'so101' if urdf_path else 'pose-only mode'}")
    
    tracker = HandTracker(
        cam_idx=args.cam_idx,
        hand=args.hand,
        model=args.model,
        urdf_path=urdf_path,
        safe_range=SO101_SAFE_RANGE,
        use_scroll=args.use_scroll,
        debug_mode=args.debug,
        kf_dt=1/args.fps
    )
    
    # Initial pose for SO-101 (home position)
    home_pos = np.array([0.25, 0.0, 0.15])  # 25cm forward, 15cm up
    home_rot = R.from_euler("ZYX", [0, 0, 0], degrees=True).as_matrix()
    home_pose = GripperPose(home_pos, home_rot, open_degree=20)
    
    # If using joint control, convert to joint space
    if not args.pose_only:
        # Home joint configuration for SO-101 (degrees)
        home_joints = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 20.0])  # [j1,j2,j3,j4,j5,gripper]
        
        print(f"🏠 Home joint configuration: {home_joints}")
        print(f"📍 Home pose: {home_pose.to_string()}")
    
    print("\n🎮 Controls:")
    print("   'p' - Pause/resume tracking")
    print("   'space' - Hold to realign/reset")
    print("   'k' - Toggle keypoints-only visualization")
    if args.use_scroll:
        print("   'scroll wheel' - Control gripper opening")
    print("   'Ctrl+C' - Exit")
    print("\n🚀 Starting tracking loop...")
    
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
            if args.pose_only:
                # Test pose tracking only
                current_pose = tracker.read_hand_state(home_pose)
                
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"📊 Pose: {current_pose.to_string()}")
                    
            else:
                # Test joint control
                current_joints = tracker.read_hand_state_joint(home_joints)
                
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"🔧 Joints: [{current_joints[0]:.1f}, {current_joints[1]:.1f}, "
                          f"{current_joints[2]:.1f}, {current_joints[3]:.1f}, "
                          f"{current_joints[4]:.1f}, gripper:{current_joints[5]:.1f}]")
            
            frame_count += 1
            
            # Calculate and display FPS periodically
            if frame_count % 60 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"📈 Average FPS: {fps:.1f}")
            
            time.sleep(1/args.fps)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        
    finally:
        print("🧹 Cleaning up...")
        tracker.close()
        print("✅ Done!")

if __name__ == "__main__":
    main()
