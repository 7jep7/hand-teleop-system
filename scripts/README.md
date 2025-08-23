# 🔧 Scripts

> **⚠️ DEPRECATION NOTICE**: These scripts are being phased out in favor of the unified `main.py` entry point.

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
| Custom resource setup | Built into `main.py` (automatic) |
| Manual environment checks | `python main.py --info` |

## Recommended Usage

Use the unified entry point for all operations:
```bash
python main.py --help    # See all options
python main.py           # Quick start
python main.py --dev     # Development mode
```

**Features:**
- Memory limits (8GB virtual, 6GB physical)
- CPU core allocation (70% of available cores)
- Process priority control
- PyTorch memory management
- GPU allocation control
- Partition mounting for conda environments

**Requirements:**
- `/mnt/nvme0n1p8/conda-envs/j11n` environment
- `/mnt/nvme0n1p8/conda-envs/hand-teleop` environment
- Sufficient system permissions for `ulimit` and `nice`

**Usage:**
```bash
./scripts/run_web_api.sh
```

### Alternative: `manage.py`
**Use when:** You want simple, cross-platform startup without resource management.

**Features:**
- Simple conda environment detection
- Basic health checks
- Cross-platform compatibility
- Integrated testing and validation

**Usage:**
```bash
python3 manage.py start    # Simple startup
python3 manage.py dev      # Development mode with frontend
```

## Recommendations

- **Development:** Use `python3 manage.py dev`
- **Production (your system):** Use `./scripts/run_web_api.sh`
- **Production (other systems):** Use `python3 manage.py start`
- **CI/CD & Testing:** Use `python3 manage.py test`

## Migration Path

If you want to consolidate, you could:
1. Keep `run_web_api.sh` for your specific production setup
2. Use `manage.py` for general development and testing
3. Eventually migrate resource management features from `run_web_api.sh` into `manage.py`
