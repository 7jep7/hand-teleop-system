# 🔧 Scripts

> **⚠️ DEPRECATION NOTICE**: Most scripts are being phased out in favor of the unified `main.py` entry point.

## Current Scripts

### `run_web_api.sh` (Legacy)
- **Status**: Deprecated
- **Replacement**: `python main.py --start`
- **Purpose**: Production server with resource management

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
