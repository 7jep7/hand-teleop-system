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
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    
    # Check if conda env exists
    conda_check = run_command("conda info --envs | grep hand-teleop", "Check conda environment", 5)
    
    if conda_check:
        print("✅ Using conda environment")
        return run_command(
            "conda activate hand-teleop && python3 backend/render_backend.py &", 
            "Start backend with conda", 
            10
        )
    else:
        print("⚠️  Conda environment not found, using system Python")
        return run_command("python3 backend/render_backend.py &", "Start backend with system Python", 10)

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
    print("🎯 Hand Teleop System - Project Manager")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("\nCommands:")
        print("  clean    - Clean up temporary files and cache")
        print("  test     - Run comprehensive test suite")
        print("  start    - Start the backend server")
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
