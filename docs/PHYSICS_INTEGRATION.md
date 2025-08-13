# Physics Integration Architecture

## Overview
This document outlines the architecture for integrating physics simulation with the hand teleop system for dataset recording.

## Option 1: Three.js + Web Physics (Lightweight)

### Tech Stack
- **Frontend**: Three.js + Cannon.js/Ammo.js
- **Physics**: Browser-based rigid body simulation
- **Recording**: Direct JSON export of trajectories

### Use Cases
- Basic teleoperation practice
- Simple object manipulation
- Rapid prototyping
- Lightweight dataset collection

### Implementation
```javascript
// Three.js + Cannon.js example
import * as CANNON from 'cannon-es';
import * as THREE from 'three';

class PhysicsScene {
    constructor() {
        this.world = new CANNON.World();
        this.world.gravity.set(0, -9.82, 0);
        
        // Record trajectory data
        this.trajectoryData = [];
    }
    
    recordFrame(handPose, robotJoints, objects) {
        this.trajectoryData.push({
            timestamp: Date.now(),
            handPose: handPose,
            robotState: robotJoints,
            objectStates: objects.map(obj => ({
                position: obj.position,
                rotation: obj.quaternion,
                velocity: obj.velocity
            }))
        });
    }
}
```

## Option 2: Hybrid Web + Physics Server (Recommended)

### Architecture
```
┌─────────────────┐    WebSocket     ┌──────────────────┐
│   Web Frontend  │ ←─────────────→  │  Physics Server  │
│   (Three.js)    │                  │ (Isaac/MuJoCo)   │
│                 │                  │                  │
│ - Live Viz      │                  │ - Accurate Sim   │
│ - Hand Control  │                  │ - Dataset Export │
│ - Robot View    │                  │ - ML Training    │
└─────────────────┘                  └──────────────────┘
```

### Benefits
- **Real-time visualization** in browser
- **High-fidelity physics** on server
- **Scalable** - can run multiple simulations
- **ML-ready** dataset output

### Physics Server Options

#### Isaac Sim (NVIDIA)
```python
# Example Isaac Sim integration
import omni.isaac.core as core
from omni.isaac.manipulators import SingleManipulator
import websockets
import json

class TeleopDatasetRecorder:
    def __init__(self):
        self.simulation = core.World()
        self.robot = SingleManipulator(prim_path="/robot")
        self.dataset = []
        
    async def handle_teleop_command(self, websocket, path):
        async for message in websocket:
            command = json.loads(message)
            # Apply hand pose to robot
            joint_targets = self.ik_solver.solve(command['hand_pose'])
            self.robot.set_joint_positions(joint_targets)
            
            # Record frame
            self.record_frame(command, self.get_scene_state())
            
            # Send back visualization data
            await websocket.send(json.dumps({
                'robot_state': joint_targets,
                'objects': self.get_object_states()
            }))
```

#### MuJoCo (Lightweight Alternative)
```python
import mujoco
import mujoco_viewer
import websockets

class MuJoCoTeleopServer:
    def __init__(self, model_path):
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        self.viewer = mujoco_viewer.MujocoViewer(self.model, self.data)
        
    def step_simulation(self, hand_commands):
        # Apply IK to get joint targets
        joint_targets = self.compute_ik(hand_commands)
        self.data.ctrl[:] = joint_targets
        
        # Step physics
        mujoco.mj_step(self.model, self.data)
        
        # Record dataset
        return self.get_state_for_dataset()
```

## Option 3: Progressive Enhancement

Start lightweight and upgrade as needed:

### Phase 1: Three.js Only
- Basic visualization
- Simple collision detection
- JSON trajectory export

### Phase 2: Add Web Physics
- Cannon.js for basic physics
- Object interaction
- Force feedback simulation

### Phase 3: Physics Server Integration
- Add Isaac Sim/MuJoCo backend
- High-fidelity dataset recording
- ML training pipeline

## Dataset Recording Strategy

### Data Structure
```json
{
  "metadata": {
    "session_id": "uuid",
    "robot_model": "so-101",
    "timestamp": "2025-08-13T10:30:00Z",
    "physics_engine": "isaac_sim"
  },
  "trajectory": [
    {
      "frame": 0,
      "time": 0.033,
      "hand_pose": {
        "thumb_tip": [x, y, z],
        "index_pip": [x, y, z],
        "index_tip": [x, y, z]
      },
      "robot_state": {
        "joint_positions": [j1, j2, j3, j4, j5, j6],
        "joint_velocities": [v1, v2, v3, v4, v5, v6],
        "end_effector_pose": [x, y, z, qx, qy, qz, qw]
      },
      "objects": [
        {
          "id": "cube_001",
          "position": [x, y, z],
          "rotation": [qx, qy, qz, qw],
          "velocity": [vx, vy, vz]
        }
      ]
    }
  ]
}
```

## Recommendations

### For Immediate Development
- Start with **Three.js + Cannon.js**
- Focus on getting teleoperation working
- Record basic trajectory data

### For Production/Research
- Implement **hybrid architecture**
- Use **Isaac Sim** for high-fidelity physics
- **MuJoCo** as lightweight alternative

### Performance Considerations
- Web physics: ~60 FPS, simple scenes
- Isaac Sim: Variable FPS, complex scenes
- MuJoCo: ~1000+ FPS, efficient for ML

## Next Steps
1. Implement Three.js robot visualization
2. Add basic Cannon.js physics
3. Design WebSocket protocol for physics server
4. Create dataset export format
5. Integrate with ML training pipeline
