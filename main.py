#!/usr/bin/env python3
"""
Hand Teleop System - Unified Entry Point
Production-ready hand tracking and robot control system with resource management
"""

import argparse
import sys
import os
import subprocess
import time
import multiprocessing
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

# Get project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

def run_command(cmd, description="", timeout=30):
    """Run a command and return success status"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def kill_existing_servers():
    """Kill any existing processes on ports 8000 and 3000"""
    print("🔧 Checking for existing servers...")
    
    ports_to_kill = [8000, 3000]
    for port in ports_to_kill:
        # Check if port is in use
        check_cmd = f"lsof -ti:{port}"
        try:
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print(f"   Found process on port {port}, killing...")
                kill_cmd = f"fuser -k {port}/tcp"
                subprocess.run(kill_cmd, shell=True, capture_output=True)
                time.sleep(1)  # Give processes time to die
                print(f"✅ Cleared port {port}")
            else:
                print(f"✅ Port {port} is free")
        except Exception as e:
            print(f"   ⚠️  Could not check/kill port {port}: {e}")

def setup_resource_management():
    """Configure production-grade resource management"""
    print("🛡️  Configuring resource management...")
    
    # Get system resources
    total_cores = multiprocessing.cpu_count()
    use_cores = max(1, int(total_cores * 0.5))  # Reduced from 70% to 50% to prevent Chrome freeze
    
    # Set environment variables for resource control
    env_vars = {
        'OMP_NUM_THREADS': str(use_cores),
        'MKL_NUM_THREADS': str(use_cores),
        'CUDA_VISIBLE_DEVICES': '0',
        'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:256'  # Reduced from 512MB to 256MB
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    # Set memory limits (requires privileged access)
    try:
        run_command("ulimit -v 4194304", "Set virtual memory limit (4GB)", 2)  # Reduced from 8GB
        run_command("ulimit -m 3145728", "Set physical memory limit (3GB)", 2)  # Reduced from 6GB
    except:
        print("   ⚠️  Memory limits require privileged access")
    
    print(f"   CPU cores: {use_cores}/{total_cores}")
    print("   Process priority: Nice +10")

def ensure_partition_mounted():
    """Ensure the conda environments partition is mounted"""
    conda_dir = "/mnt/nvme0n1p8/conda-envs"
    
    if not os.path.exists(conda_dir):
        print("🔧 Mounting conda environments partition...")
        mount_success = run_command(
            "sudo mount /dev/nvme0n1p8 /mnt/nvme0n1p8", 
            "Mount partition for conda environments", 
            10
        )
        if not mount_success:
            print("   ⚠️  Partition mounting failed - using fallback environment")
    else:
        print("✅ Conda environments partition already mounted")

def check_backend_status():
    """Check if backend is running"""
    print("\n🔍 Checking backend status...")
    return run_command("curl -s http://localhost:8000/api/health > /dev/null", "Backend health check", 5)

def cleanup_project():
    """Clean up temporary files and cache"""
    print("\n🧹 Cleaning up project...")
    
    cleanup_commands = [
        ("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true", "Remove Python cache"),
        ("find . -name '*.pyc' -delete", "Remove compiled Python files"),  
        ("find . -name 'temp_*' -delete", "Remove temporary files"),
        ("find . -name '*.tmp' -delete", "Remove .tmp files"),
    ]
    
    for cmd, desc in cleanup_commands:
        run_command(cmd, desc)

def validate_structure():
    """Validate project structure"""
    print("\n📁 Validating project structure...")
    
    required_files = [
        "backend/render_backend.py",
        "core/__init__.py", 
        "core/hand_pose/factory.py",
        "core/robot_control/kinematics.py",
        "requirements.txt",
        "README.md",
        "tests/integration/test_comprehensive.py"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    return len(missing) == 0

def show_project_info():
    """Show project information"""
    print("\n📊 Project Information:")
    print(f"   Root: {PROJECT_ROOT}")
    print(f"   Python: {sys.executable}")
    
    # Count files by type
    py_files = len(list(Path(".").rglob("*.py")))
    md_files = len(list(Path(".").rglob("*.md")))
    
    print(f"   Python files: {py_files}")
    print(f"   Documentation files: {md_files}")

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    
    # First ensure backend is running
    if not check_backend_status():
        print("Backend not running, attempting to start...")
        start_backend_with_resource_management()
        time.sleep(3)  # Give it time to start
        
        if not check_backend_status():
            print("❌ Could not start backend, some tests will fail")
    
    # Run comprehensive tests
    test_cmd = "python3 tests/integration/test_comprehensive.py"
    return run_command(test_cmd, "Run comprehensive tests", 60)

def start_backend_with_resource_management():
    """Start the backend server with production-grade resource management"""
    print("\n🚀 Starting backend server with resource management...")
    
    # Production-grade resource management
    setup_resource_management()
    
    # Check and mount partition if needed
    ensure_partition_mounted()
    
    # Use hand-teleop environment (unified approach)
    conda_path = "/mnt/nvme0n1p8/conda-envs/hand-teleop/bin/python"
    fallback_check = run_command("conda info --envs | grep hand-teleop", "Check conda environment", 5)
    
    if os.path.exists(conda_path):
        print("✅ Using optimized conda environment with resource management")
        cmd = f"nice -n 10 {conda_path} backend/render_backend.py"
        return run_command(cmd, "Start backend with production settings", 10)
    elif fallback_check:
        print("✅ Using conda environment with basic resource management")  
        cmd = "nice -n 10 conda run -n hand-teleop python3 backend/render_backend.py"
        return run_command(cmd, "Start backend with conda run", 10)
    else:
        print("⚠️  Using system Python with basic resource management")
        return run_command("nice -n 10 python3 backend/render_backend.py", "Start backend with system Python", 10)

def serve_frontend():
    """Serve the frontend for testing"""
    print("\n🌐 Serving frontend...")
    
    # First ensure backend is running
    if not check_backend_status():
        print("Backend not running, starting it first...")
        start_backend_with_resource_management()
        time.sleep(3)
    
    # Serve the frontend directory
    frontend_cmd = "cd frontend && python3 -m http.server 3000"
    print("🔄 Starting frontend server on http://localhost:3000")
    print("🔗 Backend API available at http://localhost:8000")
    print("📋 Access the web interface at: http://localhost:3000/web/web_interface.html")
    
    return run_command(frontend_cmd, "Start frontend server", timeout=5)

def start_api_server():
    """Start API server (main backend functionality)"""
    print("\n🚀 Starting Hand Teleop System with production-grade resource management...")
    start_backend_with_resource_management()

def quick_start():
    """Quick start command for immediate use"""
    print("� Hand Teleop System - Quick Start")
    print("=" * 50)
    
    # Production defaults
    setup_resource_management()
    ensure_partition_mounted()
    
    print("\n� Starting backend with production settings...")
    start_backend_with_resource_management()
    
    print("\n✅ System ready!")
    print("🔗 API: http://localhost:8000")
    print("📋 Health check: http://localhost:8000/api/health")
    print("🌐 Frontend: Use 'python main.py --dev' to start web interface")

def development_mode():
    """Start development environment with both backend and frontend in parallel"""
    import subprocess
    print("� Starting development environment...")
    print("\n" + "="*50)

    # Kill any existing servers on the ports first
    kill_existing_servers()

    # Start backend server
    backend_cmd = [sys.executable, "main.py", "--start"]
    backend_proc = subprocess.Popen(backend_cmd)
    print("🚀 Backend server starting (PID {}), API at http://localhost:8000".format(backend_proc.pid))

    # Wait a moment for backend to start
    time.sleep(2)

    # Start frontend server
    frontend_cmd = [sys.executable, "-m", "http.server", "3000"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd="frontend")
    print("🌐 Frontend server starting (PID {}), web at http://localhost:3000/web/web_interface.html".format(frontend_proc.pid))

    print("\nPress Ctrl+C to stop both servers.")

    try:
        # Wait for both processes
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("✅ Servers stopped.")

def run_comprehensive_validation():
    """Run complete project validation"""
    print("🎯 Running complete project validation...")
    
    tasks = [
        ("Project Info", show_project_info),
        ("Cleanup", cleanup_project),
        ("Structure Check", validate_structure),
        ("Start Backend", start_backend_with_resource_management),
        ("Run Tests", run_tests),
    ]
    
    results = {}
    for task_name, task_func in tasks:
        print(f"\n{'='*20} {task_name} {'='*20}")
        try:
            result = task_func()
            results[task_name] = result if isinstance(result, bool) else True
        except Exception as e:
            print(f"❌ {task_name} failed: {e}")
            results[task_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print("=" * 60)
    
    for task, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{task:<20} {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tasks completed successfully")
    
    if passed == total:
        print("🎉 Project is ready for production!")
    else:
        print("⚠️  Some issues found. Check output above.")
    
    return passed == total

def main():
    """Main entry point with comprehensive management"""
    parser = argparse.ArgumentParser(
        description="Hand Teleop System - Production-ready hand tracking and robot control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Quick start (recommended)
  python main.py --start            # Start API server
  python main.py --dev              # Development mode (backend + frontend)
  python main.py --test             # Run test suite
  python main.py --validate         # Complete validation
  python main.py --clean            # Clean up project
  python main.py --info             # Show project info
        """
    )
    
    # Main commands
    parser.add_argument('--start', action='store_true', help='Start API server')
    parser.add_argument('--dev', action='store_true', help='Development mode (backend + frontend)')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--validate', action='store_true', help='Run complete validation')
    parser.add_argument('--clean', action='store_true', help='Clean up temporary files')
    parser.add_argument('--info', action='store_true', help='Show project information')
    parser.add_argument('--frontend', action='store_true', help='Serve frontend only')
    parser.add_argument('--check', action='store_true', help='Check project structure')
    
    args = parser.parse_args()
    
    # If no arguments, do quick start
    if len(sys.argv) == 1:
        quick_start()
        return 0
    
    # Execute based on arguments
    if args.clean:
        cleanup_project()
    elif args.test:
        return 0 if run_tests() else 1
    elif args.start:
        start_api_server()
    elif args.frontend:
        serve_frontend()
    elif args.dev:
        development_mode()
    elif args.check:
        return 0 if validate_structure() else 1
    elif args.info:
        show_project_info()
    elif args.validate:
        return 0 if run_comprehensive_validation() else 1
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())