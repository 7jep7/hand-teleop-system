# Hand Teleop Leader-Follower System - MVP Project Structure

## 🎯 Project Overview (MVP-First Approach)
Build a **Minimum Viable Product** that demonstrates hand tracking controlling a simulated robot in real-time. Extensions and optimizations come after MVP is working.

## � MVP Milestones (Aggressive 4-Day Sprint)

### ⚡ MVP Phase 1: Foundation (Day 1-2)
**Goal**: Get basic hand tracking and robot visualization working separately
- **Target Date**: Day 2
- **Dependencies**: Current MediaPipe implementation
- **Success Criteria**: Hand landmarks detected + 3D robot model renders

### 🔗 MVP Phase 2: Integration (Day 3)
**Goal**: Connect hand movements to robot control in real-time
- **Target Date**: Day 3
- **Dependencies**: Phase 1 completion
- **Success Criteria**: Moving hand moves robot arm in 3D simulation

### 🎯 MVP Phase 3: Demo-Ready (Day 4)
**Goal**: Polish for a working 5-minute demo
- **Target Date**: Day 4
- **Dependencies**: Phase 2 completion
- **Success Criteria**: Smooth demo showing hand → robot control

## 🏷️ MVP Labels System

### Priority (MVP-Focused)
- `priority/mvp-critical` - Must have for MVP demo
- `priority/post-mvp` - Nice to have after MVP works
- `priority/future` - Extensions for later versions

### Type
- `type/mvp-feature` - Core MVP functionality
- `type/enhancement` - Improve existing feature
- `type/polish` - Demo readiness improvements

### Component
- `component/hand-tracking` - Hand pose detection
- `component/robot-sim` - 3D robot visualization
- `component/mapping` - Hand → robot coordinate mapping
- `component/ui` - Minimal user interface

### Effort (Aggressive MVP Timing)
- `effort/1` - 1-2 hours (quick wins)
- `effort/2` - 3-4 hours (half day)
- `effort/3` - 5-6 hours (full day)

## 📊 MVP Epic Structure

### Epic 1: MVP Foundation (Day 1-2, 12 hours)
- **Task 1.1**: Minimal Fingertip Detection (3h)
- **Task 1.2**: Basic 3D Robot Visualization (4h) 
- **Task 1.3**: Hand → Robot Mapping (5h)

### Epic 2: MVP Integration (Day 3, 6 hours)
- **Task 2.1**: Connect Everything (4h)
- **Task 2.2**: Basic UI Controls (2h)

### Epic 3: MVP Demo Polish (Day 4, 6 hours)
- **Task 3.1**: Make it Smooth (3h)
- **Task 3.2**: Package for Demo (3h)

## 🎯 MVP Scope Decisions

### ✅ MVP Includes (Must Have)
- MediaPipe hand tracking (thumb + index tip only)
- One robot model (SO-101)
- Basic Three.js scene
- Simple coordinate mapping (no complex IK)
- Start/stop button + model toggle
- Real-time hand → robot control

### ❌ Post-MVP (Later Versions)
- Multiple robot models (UR5, KUKA, etc.)
- Complex inverse kinematics
- Performance optimization (<30ms targets)
- Professional UI design
- Physical robot control
- Advanced Kalman filtering
- Comprehensive testing
- Documentation

## 🔄 MVP Workflow

1. **MVP Critical**: Must work for demo
2. **In Progress**: Active development
3. **MVP Complete**: Core functionality works
4. **Demo Ready**: Polished for presentation

## ⏱️ MVP Timeline

| Day | Epic | Tasks | Hours | Deliverable |
|-----|------|-------|-------|-------------|
| **Day 1** | Foundation Part 1 | Fingertip detection + Robot setup | 7h | Components work separately |
| **Day 2** | Foundation Part 2 | Hand → robot mapping | 5h | Basic mapping logic |
| **Day 3** | Integration | Connect + UI | 6h | End-to-end demo |
| **Day 4** | Polish | Smooth + package | 6h | **Shippable MVP** |

**Total: 24 hours = Working demo in 4 days**

## 🚀 Post-MVP Roadmap (Only After MVP Works)

### Version 2.0: Enhanced Models (Week 2)
- Add UR5, KUKA robot support
- Implement proper inverse kinematics
- Performance optimization

### Version 3.0: Professional UI (Week 3)
- Polished interface design
- Advanced configuration options
- Better error handling

### Version 4.0: Physical Integration (Week 4)
- SO-101 real robot driver
- Safety systems
- Production deployment

## 📁 MVP File Organization

```
github-issues/
├── PROJECT_STRUCTURE.md       # This file (MVP-focused)
├── mvp-milestones/
│   ├── mvp-day1-foundation.md
│   ├── mvp-day2-integration.md
│   └── mvp-day3-polish.md
├── mvp-tasks/
│   ├── task1-fingertip-detection.md
│   ├── task2-robot-visualization.md
│   ├── task3-hand-robot-mapping.md
│   ├── task4-integration.md
│   ├── task5-basic-ui.md
│   └── task6-demo-polish.md
└── post-mvp/
    ├── v2-enhanced-models.md
    ├── v3-professional-ui.md
    └── v4-physical-integration.md
```
