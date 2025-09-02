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
import signal
import psutil
from pathlib import Path
from typing import Optional, List, Tuple, Any

# Get project root and set working directory
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

class ProcessManager:
    """Enhanced process management for robust development environment"""
    
    def __init__(self):
        self.backend_proc: Optional[subprocess.Popen] = None
        self.frontend_proc: Optional[subprocess.Popen] = None
        self.cleanup_registered = False
        
    def register_cleanup(self):
        """Register cleanup handlers for graceful shutdown"""
        if not self.cleanup_registered:
            signal.signal(signal.SIGINT, self._cleanup_handler)
            signal.signal(signal.SIGTERM, self._cleanup_handler)
            self.cleanup_registered = True
    
    def _cleanup_handler(self, signum, frame):
        """Handle cleanup on signal"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.cleanup_all()
        sys.exit(0)
    
    def kill_port_processes(self, port: int, timeout: int = 10) -> bool:
        """Kill processes using a specific port with enhanced robustness"""
        try:
            # Find processes using the port
            pids = []
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            pids.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not pids:
                print(f"✅ Port {port} is free")
                return True
                
            print(f"🔄 Found {len(pids)} process(es) on port {port}, terminating...")
            
            # Try graceful termination first
            for pid in pids:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Wait for graceful termination
            time.sleep(2)
            
            # Force kill remaining processes
            remaining_pids = []
            for pid in pids:
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        proc.kill()
                        remaining_pids.append(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Final verification
            time.sleep(1)
            for pid in remaining_pids:
                try:
                    if psutil.Process(pid).is_running():
                        print(f"⚠️  Process {pid} still running on port {port}")
                        return False
                except psutil.NoSuchProcess:
                    continue
                    
            print(f"✅ Cleared port {port}")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing port {port}: {e}")
            # Fallback to shell commands
            return self._fallback_port_cleanup(port)
    
    def _fallback_port_cleanup(self, port: int) -> bool:
        """Fallback port cleanup using shell commands"""
        try:
            # Try lsof approach
            result = subprocess.run(
                f"lsof -ti:{port} | xargs kill -9",
                shell=True, capture_output=True, timeout=5
            )
            time.sleep(1)
            
            # Verify
            verify = subprocess.run(
                f"lsof -ti:{port}",
                shell=True, capture_output=True, timeout=3
            )
            
            success = verify.returncode != 0 or not verify.stdout.strip()
            if success:
                print(f"✅ Cleared port {port} (fallback)")
            else:
                print(f"⚠️  Port {port} cleanup failed")
            return success
            
        except Exception as e:
            print(f"❌ Fallback cleanup failed for port {port}: {e}")
            return False
    
    def cleanup_all(self):
        """Clean up all managed processes"""
        processes = []
        if self.backend_proc:
            processes.append(("Backend", self.backend_proc))
        if self.frontend_proc:
            processes.append(("Frontend", self.frontend_proc))
            
        if not processes:
            return
            
        print("🛑 Stopping servers...")
        
        # Graceful termination
        for name, proc in processes:
            try:
                if proc.poll() is None:
                    print(f"   Terminating {name}...")
                    proc.terminate()
            except Exception as e:
                print(f"   Warning: Could not terminate {name}: {e}")
        
        # Wait for graceful shutdown
        time.sleep(3)
        
        # Force kill if needed
        for name, proc in processes:
            try:
                if proc.poll() is None:
                    print(f"   Force killing {name}...")
                    proc.kill()
                    proc.wait(timeout=2)
            except Exception as e:
                print(f"   Warning: Could not kill {name}: {e}")
        
        print("✅ Cleanup complete")

def run_command(cmd: str, description: str = "", timeout: int = 30) -> bool:
    """Run a command and return success status"""
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            if description:
                print(f"✅ {description} - Success")
            return True
        else:
            if description:
                print(f"❌ {description} - Failed")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        if description:
            print(f"⏱️  {description} - Timeout")
        return False
    except Exception as e:
        if description:
            print(f"❌ {description} - Exception: {e}")
        return False

def setup_resource_management():
    """Configure optimized resource management"""
    print("🛡️  Configuring resource management...")
    
    # Get system resources
    total_cores = multiprocessing.cpu_count()
    use_cores = max(1, min(4, int(total_cores * 0.6)))  # Limit to max 4 cores
    
    # Set environment variables for resource control
    env_vars = {
        'OMP_NUM_THREADS': str(use_cores),
        'MKL_NUM_THREADS': str(use_cores),
        'NUMBA_NUM_THREADS': str(use_cores),
        'CUDA_VISIBLE_DEVICES': '0',
        'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:128'  # Conservative memory
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    print(f"   CPU cores: {use_cores}/{total_cores}")

def check_backend_health(timeout: int = 5) -> bool:
    """Check if backend is responding"""
    try:
        result = subprocess.run(
            "curl -s -f http://localhost:8000/api/health",
            shell=True, capture_output=True, timeout=timeout
        )
        return result.returncode == 0
    except:
        return False

def wait_for_backend(max_wait: int = 30) -> bool:
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to be ready...")
    
    for i in range(max_wait):
        if check_backend_health():
            print("✅ Backend health check passed")
            return True
        time.sleep(1)
        if i % 5 == 4:  # Progress indicator every 5 seconds
            print(f"   Still waiting... ({i+1}s)")
    
    print("❌ Backend health check timeout")
    return False

def development_mode():
    """Start enhanced development environment"""
    print("🚀 Starting development environment...")
    print("=" * 60)
    
    # Initialize process manager
    pm = ProcessManager()
    pm.register_cleanup()
    
    # Setup resource management
    setup_resource_management()
    
    # Clear ports
    print("\n🔧 Clearing ports...")
    ports_cleared = True
    for port in [8000, 3000]:
        if not pm.kill_port_processes(port):
            ports_cleared = False
    
    if not ports_cleared:
        print("❌ Could not clear all ports. Please resolve manually.")
        return False
    
    print("⏳ Port cleanup complete, starting servers...")
    time.sleep(2)
    
    # Start backend
    try:
        print("🔄 Starting backend server...")
        backend_cmd = [sys.executable, "backend/render_backend.py"]
        pm.backend_proc = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=os.environ.copy()  # Include our resource management env vars
        )
        print(f"🚀 Backend server started (PID {pm.backend_proc.pid})")
        
        # Wait for backend to be ready
        if not wait_for_backend():
            print("❌ Backend failed to start properly")
            pm.cleanup_all()
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        pm.cleanup_all()
        return False
    
    # Start frontend
    try:
        print("🔄 Starting frontend server...")
        frontend_cmd = [sys.executable, "-m", "http.server", "3000"]
        pm.frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        print(f"🌐 Frontend server started (PID {pm.frontend_proc.pid})")
        time.sleep(2)
        
        # Quick check that frontend started
        if pm.frontend_proc.poll() is not None:
            stdout, stderr = pm.frontend_proc.communicate()
            print(f"❌ Frontend failed to start: {stderr}")
            pm.cleanup_all()
            return False
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        pm.cleanup_all()
        return False
    
    # Success message
    print("\n" + "✅" * 20)
    print("🎉 Development environment ready!")
    print("=" * 60)
    print("🔗 Backend API: http://localhost:8000")
    print("📋 Health check: http://localhost:8000/api/health")
    print("🌐 Frontend: http://localhost:3000")
    print("🎯 Main Demo: http://localhost:8000/ (or http://localhost:3000/demo.html)")
    print("� Debug Tool: http://localhost:8000/debug.html (or http://localhost:3000/debug.html)")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop all servers")
    print()
    
    try:
        # Monitor both processes
        while True:
            # Check backend
            if pm.backend_proc.poll() is not None:
                print("❌ Backend process died unexpectedly")
                stdout, stderr = pm.backend_proc.communicate()
                if stderr:
                    print(f"   Backend error: {stderr}")
                break
                
            # Check frontend  
            if pm.frontend_proc.poll() is not None:
                print("❌ Frontend process died unexpectedly")
                stdout, stderr = pm.frontend_proc.communicate()
                if stderr:
                    print(f"   Frontend error: {stderr}")
                break
                
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
    finally:
        pm.cleanup_all()
    
    return True

def run_tests():
    """Run test suite"""
    print("🧪 Running tests...")
    
    test_commands = [
        ("python -m pytest tests/ -v", "Unit tests"),
        ("python test_so101.py", "SO-101 integration test"),
    ]
    
    all_passed = True
    for cmd, desc in test_commands:
        print(f"\n🔄 Running {desc}...")
        success = run_command(cmd, "", 60)
        if success:
            print(f"✅ {desc} passed")
        else:
            print(f"❌ {desc} failed")
            all_passed = False
    
    return all_passed

def show_project_info():
    """Display project information"""
    print("📋 Hand Teleop System Information")
    print("=" * 50)
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"💻 CPU Cores: {multiprocessing.cpu_count()}")
    
    # Check key dependencies
    dependencies = [
        ("fastapi", "fastapi"),
        ("opencv-python", "cv2"), 
        ("mediapipe", "mediapipe"),
        ("numpy", "numpy")
    ]
    print("\n📦 Key Dependencies:")
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"   ✅ {dep_name}")
        except ImportError:
            print(f"   ❌ {dep_name} (missing)")
    
    print()
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Hand Teleop System")
    parser.add_argument("--dev", action="store_true", help="Start development environment")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--info", action="store_true", help="Show project info")
    
    args = parser.parse_args()
    
    if args.dev:
        return development_mode()
    elif args.test:
        return run_tests()
    elif args.info:
        return show_project_info()
    else:
        print("Hand Teleop System")
        print("Use --dev to start development environment")
        print("Use --test to run tests")
        print("Use --info to show project information")
        parser.print_help()
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)