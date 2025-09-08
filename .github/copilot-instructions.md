# GitHub Copilot Instructions for Hand Teleop System

## Environment Setup
```bash
conda activate hand-teleop  # Always activate this environment first
```

## Core Commands
```bash
python3 main.py --dev       # Development mode (start here)
python3 main.py --test      # Run tests
python3 run_tests.py --unit # Specific test categories
```

## Key Architecture Patterns

### Hand Tracking Factory (`core/hand_pose/factory.py`)
Uses lazy imports with automatic fallbacks:
```python
create_estimator("wilor")     # Primary model
create_estimator("mediapipe") # Fallback
create_estimator("apriltag")  # Cube tracking
```

### Resource Management (`core/resource_manager.py`)
Always wrap GPU operations:
```python
with ResourceManager().controlled_execution():
    # GPU-intensive code here
```

### WebSocket Streaming (`backend/render_backend.py`)
Real-time data via `ConnectionManager` class with `active_connections` list.

## Browser Compatibility
- **Firefox**: Recommended (stable camera access)
- **Chrome**: May freeze camera - use recovery scripts in `scripts/recovery/`

## Project Structure
- `main.py` - Unified entry point with ProcessManager
- `backend/render_backend.py` - FastAPI app with WebSocket endpoints
- `core/` - Modular components (hand tracking, robot control, resources)
- `frontend/` - Browser interfaces with Chrome bug mitigation
- `tests/` - Organized by scope: unit, api, functional, integration
