# 🧪 Testing Guide

## Test Organization

The test suite is organized into logical categories for easy execution and maintenance:

```
tests/
├── unit/                  # 🔬 Unit tests (isolated component testing)
├── api/                   # 🌐 API and backend tests
│   ├── test_backend.py           # Backend API functionality
│   ├── test_websocket_endpoints.py # WebSocket endpoint testing
│   └── test_websocket_simple.py    # Basic WebSocket functionality
├── functional/            # 🎯 Functional and end-to-end tests
│   ├── test_so101.py             # SO-101 robot testing
│   ├── test_mvp_fingertips.py    # Fingertip tracking tests
│   ├── test_wilor_minimal.py     # WiLoR hand tracking tests
│   ├── test_wilor_simple.py      # Simple WiLoR functionality
│   ├── test_error_debug.py       # Error handling tests
│   ├── test_minimal.py           # Minimal functionality tests
│   └── test_simple_overlay.py    # UI overlay tests
└── integration/           # 🔗 Integration tests
    ├── test_comprehensive.py     # Full system integration
    └── test_simple.py            # Basic integration tests
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
python run_tests.py --all

# Run specific categories
python run_tests.py --unit        # Unit tests only
python run_tests.py --api         # API/backend tests
python run_tests.py --functional  # Functional tests
python run_tests.py --integration # Integration tests

# Fast testing (skip slow tests)
python run_tests.py --fast

# With coverage report
python run_tests.py --coverage

# Verbose output
python run_tests.py --verbose
```

### Direct pytest Commands

```bash
# All tests
pytest

# Specific directories
pytest tests/unit/
pytest tests/api/
pytest tests/functional/
pytest tests/integration/

# Specific test files
pytest tests/api/test_backend.py
pytest tests/functional/test_so101.py

# With markers
pytest -m "not slow"          # Skip slow tests
pytest -m "api"               # Run API tests only
pytest -m "functional"        # Run functional tests only
```

## Test Categories

### 🔬 Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: Minimal, mostly mocked
- **Coverage**: Core modules, utilities, algorithms

### 🌐 API Tests (`tests/api/`)
- **Purpose**: Test backend APIs and WebSocket endpoints
- **Speed**: Medium (1-5 seconds per test)
- **Dependencies**: FastAPI server, WebSocket connections
- **Coverage**: REST endpoints, WebSocket communication, error handling

**Key Tests:**
- `test_backend.py`: Health checks, API responses, error handling
- `test_websocket_endpoints.py`: WebSocket connection, message handling
- `test_websocket_simple.py`: Basic WebSocket functionality

### 🎯 Functional Tests (`tests/functional/`)
- **Purpose**: Test end-to-end functionality and user scenarios
- **Speed**: Medium to Slow (5-30 seconds per test)
- **Dependencies**: Full system, camera access, models
- **Coverage**: Hand tracking, robot control, UI functionality

**Key Tests:**
- `test_so101.py`: SO-101 robot kinematics and control
- `test_mvp_fingertips.py`: Fingertip detection and tracking
- `test_wilor_minimal.py`: WiLoR hand pose estimation
- `test_error_debug.py`: Error handling and debugging features

### 🔗 Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and system integration
- **Speed**: Slow (10-60 seconds per test)
- **Dependencies**: Full system, external services, hardware
- **Coverage**: Complete workflows, browser integration, performance

**Key Tests:**
- `test_comprehensive.py`: Full system end-to-end testing
- `test_simple.py`: Basic integration workflows

## Test Configuration

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes

markers =
    unit: Unit tests
    integration: Integration tests
    api: API and backend tests
    functional: Functional and end-to-end tests
    slow: Slow tests (require backend)
    gpu: Tests requiring GPU
    browser: Tests requiring browser functionality
```

### Test Markers

Use markers to categorize and filter tests:

```python
import pytest

@pytest.mark.unit
def test_kinematics_calculation():
    """Unit test for kinematics"""
    pass

@pytest.mark.api
@pytest.mark.slow
def test_websocket_connection():
    """API test requiring backend"""
    pass

@pytest.mark.functional
@pytest.mark.gpu
def test_hand_tracking():
    """Functional test requiring GPU"""
    pass

@pytest.mark.browser
def test_frontend_interface():
    """Test requiring browser functionality"""
    pass
```

## Browser Compatibility Testing

### Manual Browser Tests

1. **Firefox Testing** (Recommended):
   ```bash
   # Start system
   python main.py --dev
   
   # Open in Firefox
   firefox http://localhost:8000/
   ```

2. **Chrome Testing** (With Recovery Ready):
   ```bash
   # Have recovery script ready
   ./scripts/recovery/chrome_camera_recovery.sh
   
   # Open in Chrome
   google-chrome http://localhost:8000/
   ```

3. **Diagnostic Testing**:
   ```bash
   # Camera diagnostics
   open http://localhost:8000/diagnostics/camera_diagnostic.html
   
   # Safe mode testing
   open http://localhost:8000/diagnostics/camera_safe_mode.html
   ```

### Automated Browser Tests

```python
# Example browser test structure
@pytest.mark.browser
@pytest.mark.slow
def test_camera_functionality():
    """Test camera access across browsers"""
    # Test Firefox
    assert test_browser_camera("firefox") == True
    
    # Test Chrome with caution
    with chrome_recovery_context():
        assert test_browser_camera("chrome") == True
```

## Performance Testing

### Benchmarking
```bash
# Performance benchmarks
pytest tests/functional/test_so101.py::test_kinematics_performance

# Memory usage testing
pytest --memprof tests/functional/

# Profiling
pytest --profile tests/functional/test_wilor_minimal.py
```

### Load Testing
```bash
# WebSocket load testing
pytest tests/api/test_websocket_endpoints.py::test_concurrent_connections

# Hand tracking performance
pytest tests/functional/test_mvp_fingertips.py::test_frame_rate_performance
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run fast tests
      run: python run_tests.py --fast --coverage
    - name: Run browser tests
      run: python run_tests.py --functional
      env:
        DISPLAY: :99.0
```

## Troubleshooting Tests

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=/home/jonas-petersen/dev/hand-teleop-system:$PYTHONPATH
   ```

2. **Backend Connection Failures**:
   ```bash
   # Start backend before API tests
   python main.py --start &
   pytest tests/api/
   ```

3. **Camera Access Issues**:
   ```bash
   # Use diagnostic tools
   python -c "import cv2; print('Camera:', cv2.VideoCapture(0).isOpened())"
   
   # Recovery if needed
   ./scripts/recovery/chrome_camera_recovery.sh
   ```

4. **GPU/CUDA Issues**:
   ```bash
   # Skip GPU tests
   pytest -m "not gpu"
   
   # Check CUDA availability
   python -c "import torch; print('CUDA:', torch.cuda.is_available())"
   ```

### Debug Mode
```bash
# Run tests with debug output
pytest -s -v tests/functional/test_error_debug.py

# Drop into debugger on failure
pytest --pdb tests/

# Capture output
pytest -s tests/ | tee test_output.log
```

## Coverage Reports

```bash
# Generate coverage report
python run_tests.py --coverage

# View HTML report
open htmlcov/index.html

# Coverage for specific modules
pytest --cov=core.hand_pose --cov-report=html tests/functional/
```

---

## Best Practices

1. **Write tests for new features** - Every new feature should have corresponding tests
2. **Use appropriate test categories** - Place tests in the correct directory
3. **Mark tests appropriately** - Use pytest markers for filtering
4. **Test browser compatibility** - Always test in Firefox and Chrome
5. **Include performance tests** - Monitor system performance
6. **Document test purpose** - Clear docstrings for test functions
7. **Use fixtures for setup** - Reusable test setup and teardown
8. **Mock external dependencies** - Unit tests should be isolated
9. **Test error conditions** - Include negative test cases
10. **Keep tests maintainable** - Regular cleanup and refactoring
