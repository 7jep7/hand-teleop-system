"""
SO-101 Robot Simulation Service
Provides real-time joint state management and kinematics for the SO-101 robot arm.
"""

import numpy as np
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .kinematics import RobotKinematics


class SO101Simulation:
    """
    SO-101 Robot Simulation with real-time joint control and kinematics.
    Manages 6-DOF robot state and provides IK/FK capabilities.
    """
    
    def __init__(self):
        # Joint names in order
        self.joint_names = [
            "shoulder_pan",
            "shoulder_lift", 
            "elbow_flex",
            "wrist_flex",
            "wrist_roll",
            "gripper"
        ]
        
        # Joint limits (from URDF)
        self.joint_limits = {
            "shoulder_pan": (-1.91986, 1.91986),
            "shoulder_lift": (-1.74533, 1.74533),
            "elbow_flex": (-1.69, 1.69),
            "wrist_flex": (-1.65806, 1.65806),
            "wrist_roll": (-2.74385, 2.84121),
            "gripper": (-0.174533, 1.74533)
        }
        
        # Current joint positions (radians)
        self.joint_positions = np.zeros(6)
        
        # Target joint positions for smooth interpolation
        self.target_positions = np.zeros(6)
        
        # Joint velocities for smooth motion
        self.joint_velocities = np.zeros(6)
        
        # Initialize kinematics
        urdf_path = Path(__file__).parent.parent.parent / "assets" / "meshes" / "so101" / "so101_complete.urdf"
        try:
            self.kinematics = RobotKinematics(str(urdf_path), frame_name="gripper_frame_link")
            self.kinematics_available = True
            print(f"✅ SO-101 kinematics initialized with URDF: {urdf_path}")
        except Exception as e:
            print(f"⚠️  Kinematics not available: {e}")
            self.kinematics_available = False
    
    def get_joint_state(self) -> Dict:
        """Get current joint state as dictionary."""
        return {
            "joint_names": self.joint_names,
            "positions": self.joint_positions.tolist(),
            "targets": self.target_positions.tolist(),
            "velocities": self.joint_velocities.tolist(),
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def set_joint_positions(self, positions: List[float], smooth: bool = True) -> bool:
        """
        Set target joint positions.
        
        Args:
            positions: List of 6 joint positions in radians
            smooth: Whether to use smooth interpolation
            
        Returns:
            True if positions are valid, False otherwise
        """
        if len(positions) != 6:
            return False
            
        # Clamp to joint limits
        clamped_positions = []
        for i, pos in enumerate(positions):
            joint_name = self.joint_names[i]
            lower, upper = self.joint_limits[joint_name]
            clamped_pos = max(lower, min(upper, pos))
            clamped_positions.append(clamped_pos)
        
        if smooth:
            self.target_positions = np.array(clamped_positions)
        else:
            self.joint_positions = np.array(clamped_positions)
            self.target_positions = np.array(clamped_positions)
            
        return True
    
    def update_motion(self, dt: float = 0.016) -> None:
        """
        Update joint positions with smooth interpolation.
        Call this at ~60Hz for smooth motion.
        
        Args:
            dt: Time delta in seconds (default 60fps)
        """
        # Simple smooth interpolation
        alpha = min(1.0, dt * 10.0)  # Adjust speed as needed
        
        # Calculate velocity
        position_diff = self.target_positions - self.joint_positions
        self.joint_velocities = position_diff / dt if dt > 0 else np.zeros(6)
        
        # Update positions
        self.joint_positions += position_diff * alpha
    
    def compute_forward_kinematics(self) -> Optional[np.ndarray]:
        """
        Compute forward kinematics for current joint state.
        
        Returns:
            4x4 transformation matrix of end-effector, or None if kinematics unavailable
        """
        if not self.kinematics_available:
            return None
            
        try:
            return self.kinematics.fk(self.joint_positions)
        except Exception as e:
            print(f"FK computation failed: {e}")
            return None
    
    def compute_inverse_kinematics(self, target_pose: np.ndarray) -> Optional[np.ndarray]:
        """
        Compute inverse kinematics for target end-effector pose.
        
        Args:
            target_pose: 4x4 transformation matrix
            
        Returns:
            Joint positions array, or None if IK failed
        """
        if not self.kinematics_available:
            return None
            
        try:
            # Use current positions as initial guess
            result = self.kinematics.ik(self.joint_positions, target_pose)
            return result
        except Exception as e:
            print(f"IK computation failed: {e}")
            return None
    
    def hand_pose_to_joint_angles(self, hand_landmarks: List[Dict]) -> Optional[List[float]]:
        """
        Convert hand pose landmarks to robot joint angles.
        This is a simplified mapping - can be enhanced with more sophisticated algorithms.
        
        Args:
            hand_landmarks: List of hand landmark dictionaries with x, y, z coordinates
            
        Returns:
            List of 6 joint angles, or None if conversion failed
        """
        if not hand_landmarks or len(hand_landmarks) < 21:
            return None
            
        try:
            # Extract key landmarks
            wrist = hand_landmarks[0]
            thumb_tip = hand_landmarks[4]
            index_tip = hand_landmarks[8]
            middle_tip = hand_landmarks[12]
            
            # Simple mapping based on hand orientation and finger positions
            # This is a placeholder - replace with your actual hand-to-robot mapping
            
            # Shoulder pan: based on wrist x position
            shoulder_pan = (wrist['x'] - 0.5) * 2.0  # Scale to joint range
            
            # Shoulder lift: based on wrist y position
            shoulder_lift = (0.5 - wrist['y']) * 1.5
            
            # Elbow flex: based on hand "openness"
            hand_span = np.sqrt((thumb_tip['x'] - index_tip['x'])**2 + 
                               (thumb_tip['y'] - index_tip['y'])**2)
            elbow_flex = (hand_span - 0.1) * 3.0
            
            # Wrist flex: based on middle finger position
            wrist_flex = (middle_tip['y'] - wrist['y']) * 2.0
            
            # Wrist roll: based on wrist z rotation (if available)
            wrist_roll = wrist.get('z', 0.5) * 1.0
            
            # Gripper: based on thumb-index distance
            gripper_dist = np.sqrt((thumb_tip['x'] - index_tip['x'])**2 + 
                                  (thumb_tip['y'] - index_tip['y'])**2)
            gripper = max(0, min(1.5, gripper_dist * 5.0))
            
            joint_angles = [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper]
            
            # Clamp to limits
            for i, angle in enumerate(joint_angles):
                joint_name = self.joint_names[i]
                lower, upper = self.joint_limits[joint_name]
                joint_angles[i] = max(lower, min(upper, angle))
            
            return joint_angles
            
        except Exception as e:
            print(f"Hand pose conversion failed: {e}")
            return None
    
    def get_robot_info(self) -> Dict:
        """Get robot configuration information."""
        return {
            "name": "SO-101",
            "dof": 6,
            "joint_names": self.joint_names,
            "joint_limits": self.joint_limits,
            "kinematics_available": self.kinematics_available,
            "urdf_path": "assets/meshes/so101/so101_complete.urdf"
        }


# Global simulation instance
so101_sim = SO101Simulation()


def get_simulation() -> SO101Simulation:
    """Get the global SO-101 simulation instance."""
    return so101_sim
