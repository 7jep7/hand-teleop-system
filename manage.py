#!/usr/bin/env python3
"""
Hand Teleop System - Project Manager
Simple project management and testing utility
"""

import sys
import os
import subprocess
import time
from pathlib import Path

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

def check_backend_status():
    """Check if backend is running"""
    print("\n🔍 Checking backend status...")
    return run_command("curl -s http://localhost:8000/api/health > /dev/null", "Backend health check", 5)

def start_backend():
    """Start the backend server with production-grade resource management"""
    print("\n🚀 Starting backend server with resource management...")
    
    # Production-grade resource management
    setup_resource_management()
    
    # Check and mount partition if needed
    ensure_partition_mounted()
    
    # Use hand-teleop environment (not j11n)
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

def setup_resource_management():
    """Configure production-grade resource management"""
    print("🛡️  Configuring resource management...")
    
    import multiprocessing
    
    # Get system resources
    total_cores = multiprocessing.cpu_count()
    use_cores = max(1, int(total_cores * 0.7))  # Use 70% of cores
    
    # Set environment variables for resource control
    env_vars = {
        'OMP_NUM_THREADS': str(use_cores),
        'MKL_NUM_THREADS': str(use_cores),
        'CUDA_VISIBLE_DEVICES': '0',
        'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:512'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    # Set memory limits (requires privileged access)
    try:
        run_command("ulimit -v 8388608", "Set virtual memory limit (8GB)", 2)
        run_command("ulimit -m 6291456", "Set physical memory limit (6GB)", 2) 
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

def serve_frontend():
    """Serve the frontend for testing"""
    print("\n🌐 Serving frontend...")
    
    # First ensure backend is running
    if not check_backend_status():
        print("Backend not running, starting it first...")
        start_backend()
        time.sleep(3)
    
    # Serve the frontend directory
    frontend_cmd = "cd frontend && python3 -m http.server 3000"
    print("🔄 Starting frontend server on http://localhost:3000")
    print("🔗 Backend API available at http://localhost:8000")
    print("📋 Access the web interface at: http://localhost:3000/web/web_interface.html")
    
    return run_command(frontend_cmd, "Start frontend server", timeout=5)

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    
    # First ensure backend is running
    if not check_backend_status():
        print("Backend not running, attempting to start...")
        start_backend()
        time.sleep(3)  # Give it time to start
        
        if not check_backend_status():
            print("❌ Could not start backend, some tests will fail")
    
    # Run comprehensive tests
    test_cmd = "python3 tests/integration/test_comprehensive.py"
    return run_command(test_cmd, "Run comprehensive tests", 60)

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

def main():
    """Main project manager interface"""
    print("⚠️  DEPRECATION NOTICE: manage.py is being replaced by main.py")
    print("🔄 Please use: python main.py [options]")
    print("   python main.py --help for all options")
    print("=" * 60)
    print("")
    
    print("🎯 Hand Teleop System - Project Manager")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("\nCommands:")
        print("  clean    - Clean up temporary files and cache")
        print("  test     - Run comprehensive test suite")
        print("  start    - Start the backend server")
        print("  frontend - Serve frontend for testing")
        print("  dev      - Start both backend and frontend")
        print("  check    - Validate project structure")
        print("  info     - Show project information")
        print("  all      - Run clean, check, start, and test")
        return
    
    command = sys.argv[1].lower()
    
    if command == "clean":
        cleanup_project()
    elif command == "test":
        run_tests()
    elif command == "start":
        start_backend()
    elif command == "frontend":
        serve_frontend()
    elif command == "dev":
        print("🚀 Starting development environment...")
        print("\n" + "="*50)
        start_backend()
        time.sleep(2)
        serve_frontend()
    elif command == "check":
        validate_structure()
    elif command == "info":
        show_project_info()
    elif command == "all":
        print("🎯 Running complete project validation...")
        
        tasks = [
            ("Project Info", show_project_info),
            ("Cleanup", cleanup_project),
            ("Structure Check", validate_structure),
            ("Start Backend", start_backend),
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
    
    else:
        print(f"❌ Unknown command: {command}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
