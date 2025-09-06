# 🔧 Scripts Directory

Organized scripts for development, deployment, and maintenance.

## 🚀 **Development Scripts**

### **Start Scripts**
- **`start_dev.sh`** - Full development environment (backend + frontend)
- **`start_backend.sh`** - Backend server only
- **`start_local.sh`** - Local development setup

Usage:
```bash
# Full development environment
./scripts/start_dev.sh

# Backend only
./scripts/start_backend.sh
```

## 🛠️ **Utility Scripts**

### **Setup & Environment**
- **`setup.sh`** - Initial project setup
- **`monitor_resources.py`** - Resource monitoring tool

### **Development Tools**
- **`run_gui.sh`** - Run GUI application
- **`run_web_api.sh`** - Legacy web API runner (use `python main.py --start`)

### **Deployment**
- **`trigger_deploy.sh`** - Trigger deployment process

### **Data Processing**
- **`convert_step_to_gltf.py`** - Convert STEP files to GLTF format
- **`mount_conda_drive.sh`** - Mount conda environment drive

## 🚨 **Recovery Scripts**

### **Emergency Recovery**
- **`recovery/chrome_camera_recovery.sh`** - Chrome camera bug recovery
- **`recovery/emergency_camera_recovery.sh`** - System-wide camera recovery

Usage:
```bash
# Chrome camera issues
./scripts/recovery/chrome_camera_recovery.sh

# System-wide camera problems
./scripts/recovery/emergency_camera_recovery.sh
```

## ⚠️ **Migration Notice**

Most functionality has been unified under `main.py`:

- **Instead of**: `./scripts/run_web_api.sh`
- **Use**: `python main.py --start`

- **Instead of**: `./scripts/start_dev.sh` 
- **Use**: `python main.py --dev`

See `python main.py --help` for all options.

### `setup.sh`
- **Status**: Active
- **Purpose**: Initial environment setup
- **Usage**: `./scripts/setup.sh`

### `run_gui.sh`
- **Status**: Active
- **Purpose**: Desktop GUI launcher
- **Usage**: `./scripts/run_gui.sh`

## Migration Guide

| Old Command | New Command |
|-------------|-------------|
| `./scripts/run_web_api.sh` | `python main.py --start` |
| Any manual resource setup | Built into `main.py` (automatic) |

## Recommended Usage

Use the unified entry point for all operations:
```bash
python main.py --help    # See all options
python main.py           # Quick start
python main.py --dev     # Development mode
python main.py --start   # API server only
python main.py --test    # Run tests
```

## Features in main.py

- **Production resource management**: Memory limits, CPU allocation, process priority
- **Automatic environment detection**: Finds and uses optimal conda environment
- **Comprehensive validation**: Built-in health checks and testing
- **Cross-platform compatibility**: Works on any system with Python
