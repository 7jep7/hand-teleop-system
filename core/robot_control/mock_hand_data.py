"""
Mock Hand Data Generator for SO-101 Testing
Generates realistic hand pose sequences for testing the robot simulation
"""

import numpy as np
import time
import json
import math
from typing import List, Dict, Tuple


class MockHandDataGenerator:
    """
    Generates mock hand landmark data for testing SO-101 robot simulation.
    """
    
    def __init__(self):
        # Hand landmark indices (MediaPipe format)
        self.LANDMARK_NAMES = [
            "WRIST",
            "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
            "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP", "INDEX_FINGER_TIP",
            "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP",
            "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP",
            "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"
        ]
        
        # Base hand pose (neutral position)
        self.base_landmarks = self._generate_base_hand()
        
        # Animation parameters
        self.time_offset = 0
        self.motion_speed = 1.0
        
    def _generate_base_hand(self) -> List[Dict[str, float]]:
        """Generate base hand landmarks in neutral position."""
        landmarks = []
        
        # Wrist (center reference point)
        landmarks.append({"x": 0.5, "y": 0.5, "z": 0.0})
        
        # Thumb (4 points)
        landmarks.extend([
            {"x": 0.45, "y": 0.45, "z": 0.02},  # CMC
            {"x": 0.42, "y": 0.42, "z": 0.04},  # MCP
            {"x": 0.40, "y": 0.40, "z": 0.06},  # IP
            {"x": 0.38, "y": 0.38, "z": 0.08}   # TIP
        ])
        
        # Index finger (4 points)
        landmarks.extend([
            {"x": 0.48, "y": 0.35, "z": 0.02},  # MCP
            {"x": 0.48, "y": 0.30, "z": 0.04},  # PIP
            {"x": 0.48, "y": 0.25, "z": 0.06},  # DIP
            {"x": 0.48, "y": 0.20, "z": 0.08}   # TIP
        ])
        
        # Middle finger (4 points)
        landmarks.extend([
            {"x": 0.50, "y": 0.35, "z": 0.02},  # MCP
            {"x": 0.50, "y": 0.28, "z": 0.04},  # PIP
            {"x": 0.50, "y": 0.22, "z": 0.06},  # DIP
            {"x": 0.50, "y": 0.16, "z": 0.08}   # TIP
        ])
        
        # Ring finger (4 points)
        landmarks.extend([
            {"x": 0.52, "y": 0.35, "z": 0.02},  # MCP
            {"x": 0.52, "y": 0.29, "z": 0.04},  # PIP
            {"x": 0.52, "y": 0.24, "z": 0.06},  # DIP
            {"x": 0.52, "y": 0.19, "z": 0.08}   # TIP
        ])
        
        # Pinky (4 points)
        landmarks.extend([
            {"x": 0.54, "y": 0.37, "z": 0.02},  # MCP
            {"x": 0.54, "y": 0.32, "z": 0.04},  # PIP
            {"x": 0.54, "y": 0.28, "z": 0.06},  # DIP
            {"x": 0.54, "y": 0.25, "z": 0.08}   # TIP
        ])
        
        return landmarks
    
    def generate_wave_motion(self, t: float) -> List[Dict[str, float]]:
        """Generate hand landmarks for a waving motion."""
        landmarks = []
        
        # Wrist movement (side to side)
        wrist_x = 0.5 + 0.1 * math.sin(t * 2)
        wrist_y = 0.5 + 0.05 * math.cos(t * 1.5)
        
        for i, base_landmark in enumerate(self.base_landmarks):
            landmark = base_landmark.copy()
            
            if i == 0:  # Wrist
                landmark["x"] = wrist_x
                landmark["y"] = wrist_y
                landmark["z"] = 0.02 * math.sin(t * 3)
            else:
                # Apply wrist movement to all points
                landmark["x"] = base_landmark["x"] + (wrist_x - 0.5)
                landmark["y"] = base_landmark["y"] + (wrist_y - 0.5)
                
                # Add finger curl/uncurl motion
                finger_group = (i - 1) // 4
                finger_curl = 0.5 + 0.3 * math.sin(t * 2 + finger_group * 0.5)
                
                # Apply curl based on finger segment
                segment = (i - 1) % 4
                if segment > 0:  # Not MCP joint
                    curl_factor = segment * 0.02 * finger_curl
                    landmark["y"] += curl_factor
                    landmark["z"] += curl_factor * 0.5
            
            landmarks.append(landmark)
        
        return landmarks
    
    def generate_pointing_motion(self, t: float) -> List[Dict[str, float]]:
        """Generate hand landmarks for pointing motion."""
        landmarks = []
        
        # Pointing direction changes over time
        point_angle = math.sin(t) * math.pi / 4  # ±45 degrees
        
        for i, base_landmark in enumerate(self.base_landmarks):
            landmark = base_landmark.copy()
            
            if i == 0:  # Wrist
                landmark["x"] = 0.5 + 0.05 * math.sin(point_angle)
                landmark["y"] = 0.5
                landmark["z"] = 0.0
            elif 5 <= i <= 8:  # Index finger
                # Extend index finger
                segment = i - 5
                extension = 1.0 + segment * 0.1
                
                landmark["x"] = base_landmark["x"] + 0.05 * math.sin(point_angle) * extension
                landmark["y"] = base_landmark["y"] - 0.05 * segment
                landmark["z"] = base_landmark["z"]
            else:
                # Curl other fingers
                curl_factor = 0.8
                if i > 8:  # Middle, ring, pinky
                    finger_group = (i - 9) // 4
                    segment = (i - 9) % 4
                    
                    if segment > 0:
                        curl_amount = segment * 0.03 * curl_factor
                        landmark["y"] += curl_amount
                        landmark["z"] += curl_amount * 0.3
            
            landmarks.append(landmark)
        
        return landmarks
    
    def generate_grabbing_motion(self, t: float) -> List[Dict[str, float]]:
        """Generate hand landmarks for grabbing/grasping motion."""
        landmarks = []
        
        # Grab strength oscillates
        grab_strength = 0.5 + 0.5 * math.sin(t * 3)
        
        for i, base_landmark in enumerate(self.base_landmarks):
            landmark = base_landmark.copy()
            
            if i == 0:  # Wrist
                landmark["y"] = 0.5 + 0.02 * grab_strength
            else:
                # All fingers curl toward palm
                finger_group = (i - 1) // 4
                segment = (i - 1) % 4
                
                if segment > 0:  # Not MCP
                    curl_amount = segment * 0.04 * grab_strength
                    
                    # Curl fingers toward center
                    center_x = 0.5
                    center_y = 0.45
                    
                    dx = landmark["x"] - center_x
                    dy = landmark["y"] - center_y
                    
                    landmark["x"] -= dx * curl_amount
                    landmark["y"] -= dy * curl_amount * 0.5
                    landmark["z"] += curl_amount * 0.2
            
            landmarks.append(landmark)
        
        return landmarks
    
    def get_current_hand_pose(self, motion_type: str = "wave") -> List[Dict[str, float]]:
        """
        Get current hand pose based on motion type.
        
        Args:
            motion_type: Type of motion ("wave", "point", "grab", "static")
            
        Returns:
            List of hand landmarks with x, y, z coordinates
        """
        current_time = time.time() + self.time_offset
        t = current_time * self.motion_speed
        
        if motion_type == "wave":
            return self.generate_wave_motion(t)
        elif motion_type == "point":
            return self.generate_pointing_motion(t)
        elif motion_type == "grab":
            return self.generate_grabbing_motion(t)
        else:  # static
            return self.base_landmarks
    
    def set_motion_speed(self, speed: float):
        """Set the speed of motion animations."""
        self.motion_speed = max(0.1, min(5.0, speed))
    
    def reset_time(self):
        """Reset the animation time."""
        self.time_offset = -time.time()


# Global instance for easy access
mock_hand_generator = MockHandDataGenerator()


def get_mock_hand_data(motion_type: str = "wave") -> Dict:
    """
    Get mock hand data in the format expected by the SO-101 simulation.
    
    Args:
        motion_type: Type of hand motion to generate
        
    Returns:
        Dictionary with hand landmarks and metadata
    """
    landmarks = mock_hand_generator.get_current_hand_pose(motion_type)
    
    return {
        "hand_landmarks": landmarks,
        "hand_detected": True,
        "confidence": 0.95,
        "motion_type": motion_type,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    # Test the mock data generator
    import json
    
    print("🤖 Testing Mock Hand Data Generator")
    print("=" * 50)
    
    generator = MockHandDataGenerator()
    
    motion_types = ["static", "wave", "point", "grab"]
    
    for motion in motion_types:
        print(f"\n{motion.upper()} Motion:")
        hand_data = get_mock_hand_data(motion)
        
        print(f"  Landmarks: {len(hand_data['hand_landmarks'])}")
        print(f"  Confidence: {hand_data['confidence']}")
        print(f"  Wrist position: ({hand_data['hand_landmarks'][0]['x']:.3f}, "
              f"{hand_data['hand_landmarks'][0]['y']:.3f}, "
              f"{hand_data['hand_landmarks'][0]['z']:.3f})")
        
        # Show first few landmarks
        for i in range(min(3, len(hand_data['hand_landmarks']))):
            lm = hand_data['hand_landmarks'][i]
            name = generator.LANDMARK_NAMES[i] if i < len(generator.LANDMARK_NAMES) else f"Point_{i}"
            print(f"    {name}: ({lm['x']:.3f}, {lm['y']:.3f}, {lm['z']:.3f})")
    
    print("\n✅ Mock hand data generator working correctly!")
    print("\nTo test with SO-101 simulation:")
    print("1. Start the backend server")
    print("2. Open the SO-101 simulation frontend")
    print("3. Use this module to send mock hand data via WebSocket")
