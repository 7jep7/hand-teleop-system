# MVP Task 3: Hand → Robot Mapping Logic

**Time Estimate**: 5 hours  
**Priority**: MVP Critical  
**Day**: 2  
**Labels**: `mvp-critical`, `component/mapping`, `effort/3`

## 🎯 Goal
Create simple direct mapping from hand coordinates to robot joint angles. No complex inverse kinematics - just basic coordinate transformations.

## 📋 MVP Acceptance Criteria
- [ ] Hand X/Y position controls robot base rotation
- [ ] Hand Z position (depth) controls arm extension/retraction  
- [ ] Simple linear scaling between coordinate systems
- [ ] Real-time coordinate transformation (low latency)
- [ ] Works with coordinates from Task 1 (fingertip detection)

## 🔧 Implementation Plan
1. **Create `core/robot_control/mvp_hand_mapper.py`**:
   - Simple class with coordinate transformation methods
   - Linear scaling functions for each axis
   - No complex IK solver needed

2. **Mapping Logic**:
   ```python
   # Example mapping (adjust as needed)
   base_rotation = map_range(hand_x, -1, 1, -180, 180)  # degrees
   shoulder_angle = map_range(hand_y, -1, 1, -90, 90)   # degrees  
   elbow_angle = map_range(hand_z, 0, 1, 0, 120)        # degrees
   ```

3. **Integration Points**:
   - Input: hand coordinates from MediaPipe
   - Output: joint angles for robot visualization
   - Add basic smoothing (simple moving average)

## 💡 MVP Shortcuts
- Direct coordinate mapping (no IK calculations)
- Linear scaling only (no complex curves)
- Map to 3-4 main joints only
- Simple moving average for smoothing
- Hard-coded scaling factors (tune by hand)

## ✅ Definition of Done
- Hand movements produce reasonable robot joint angles
- Mapping feels intuitive (left hand = left robot movement)
- Basic smoothing reduces jittery movements
- Ready to connect Task 1 (hand) to Task 2 (robot)

## 🔄 Next Task
Task 4: Connect Everything (Integration)
