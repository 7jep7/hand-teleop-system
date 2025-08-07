# MVP Task 2: Basic 3D Robot Visualization

**Time Estimate**: 4 hours  
**Priority**: MVP Critical  
**Day**: 1  
**Labels**: `mvp-critical`, `component/robot-sim`, `effort/2`

## 🎯 Goal
Get a simple 3D robot arm rendering in Three.js with joints that can be rotated programmatically. No fancy materials or lighting needed.

## 📋 MVP Acceptance Criteria
- [ ] Three.js scene, camera, renderer working in browser
- [ ] Simple SO-101 robot model visible (basic geometric shapes are fine)
- [ ] Can manually set joint angles via code/UI sliders
- [ ] Basic camera controls (orbit controls for debugging)
- [ ] Runs at reasonable frame rate (20+ FPS)

## 🔧 Implementation Plan
1. **Create `frontend/components/RobotVisualization.tsx`**:
   - Set up Three.js scene basics
   - Add camera, renderer, basic lighting
   
2. **Robot Model**:
   - Use existing URDF in `core/robot_control/urdf/so101.urdf` OR
   - Create simple geometric shapes (boxes/cylinders) for joints
   - Focus on getting joints to move, not visual polish

3. **Joint Control**:
   - Create methods to set joint angles
   - Add temporary UI sliders for testing
   - Implement basic forward kinematics

## 💡 MVP Shortcuts
- Use simple geometric shapes instead of detailed meshes
- Basic ambient lighting only
- No shadows or fancy materials
- Hard-code robot dimensions if needed
- UI sliders for manual testing (temporary)

## ✅ Definition of Done
- 3D robot arm visible in browser
- Can move joints with sliders/code
- Smooth animation when joints change
- No crashes or performance issues
- Ready to receive joint commands from mapping logic

## 🔄 Next Task
Task 3: Hand → Robot Mapping Logic
