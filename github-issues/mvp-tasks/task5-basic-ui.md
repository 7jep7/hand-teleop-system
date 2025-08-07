# MVP Task 5: Basic UI Controls

**Time Estimate**: 2 hours  
**Priority**: MVP Critical  
**Day**: 3  
**Labels**: `mvp-critical`, `component/ui`, `effort/1`

## 🎯 Goal
Add minimal UI controls for start/stop tracking and model selection. Basic HTML buttons are perfectly fine for MVP.

## 📋 MVP Acceptance Criteria
- [ ] Start/Stop tracking button
- [ ] Toggle between MediaPipe and WiLoR models
- [ ] Basic status display (tracking/stopped)
- [ ] Controls are functional (no styling required)
- [ ] Clear visual feedback for current state

## 🔧 Implementation Plan
1. **Simple HTML Controls**:
   ```html
   <button id="start-stop">Start Tracking</button>
   <select id="model-select">
     <option value="mediapipe">MediaPipe</option>
     <option value="wilor">WiLoR</option>
   </select>
   <div id="status">Status: Stopped</div>
   ```

2. **State Management**:
   - Track current state (tracking/stopped)
   - Handle model switching
   - Update UI to reflect current state

3. **Integration**:
   - Wire controls to existing tracking system
   - Add event listeners for button clicks
   - Update status display in real-time

## 💡 MVP Shortcuts
- Plain HTML buttons (no CSS styling)
- Simple text for status display
- Basic event handling only
- No loading states or animations

## ✅ Definition of Done
- Can start/stop tracking with button
- Can switch between MediaPipe/WiLoR
- Status display updates correctly
- Controls feel responsive and work reliably

## 🔄 Next Task
Task 6: Smooth Movement (Day 4 polish)
