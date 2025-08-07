# MVP Task 1: Minimal Fingertip Detection

**Time Estimate**: 3 hours  
**Priority**: MVP Critical  
**Day**: 1  
**Labels**: `mvp-critical`, `component/hand-tracking`, `effort/1`

## 🎯 Goal
Extract just thumb tip and index tip coordinates from existing MediaPipe implementation. No optimization, no fancy visualization - just get the coordinates.

## 📋 MVP Acceptance Criteria
- [ ] Extract landmark #4 (thumb tip) and #8 (index tip) only
- [ ] Print coordinates to console (no visualization needed yet)
- [ ] Works with existing MediaPipe setup in `core/hand_pose/estimators/mediapipe.py`
- [ ] No performance optimization required for MVP
- [ ] Basic error handling (don't crash if no hands detected)

## 🔧 Implementation Plan
1. **Update `core/hand_pose/types.py`**:
   - Add simple data structure for thumb/index coordinates
   
2. **Modify `core/hand_pose/estimators/mediapipe.py`**:
   - Extract landmarks #4 and #8 specifically
   - Return simple coordinate pairs
   - Add console logging for debugging

3. **Test**:
   - Run with webcam
   - Verify coordinates print to console
   - Move hand around, see coordinates change

## 💡 MVP Shortcuts
- No confidence thresholds (keep it simple)
- No color-coded visualization
- No performance benchmarking
- Console logging is sufficient
- Use existing MediaPipe setup as-is

## ✅ Definition of Done
- Can see thumb and index coordinates in console
- Coordinates update in real-time as hand moves
- No crashes when hands go out of frame
- Ready to connect to robot mapping

## 🔄 Next Task
Task 2: Basic 3D Robot Visualization
