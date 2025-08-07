"""
Professional Resource Management for Hand Teleop
Prevents system crashes and provides accurate progress tracking
"""
import os
import psutil
import gc
import threading
import time
import signal
from typing import Optional, Callable
from contextlib import contextmanager

class ResourceManager:
    """Professional resource management for GPU-intensive operations"""
    
    def __init__(self, 
                 max_cpu_percent: float = 85.0,     # Increased from 70%
                 max_memory_percent: float = 90.0,   # Increased from 80% 
                 max_gpu_memory_percent: float = 75.0, # Increased from 60%
                 model_loading_mode: bool = False):  # Special mode for model loading
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent
        self.max_gpu_memory_percent = max_gpu_memory_percent
        self.model_loading_mode = model_loading_mode
        self._monitoring = False
        self._kill_switch = False
        self._emergency_triggered = False
        
    @contextmanager
    def controlled_execution(self, progress_callback: Optional[Callable] = None):
        """Context manager for safe, monitored execution"""
        self._kill_switch = False
        self._emergency_triggered = False
        monitor_thread = None
        
        try:
            # Start resource monitoring
            if progress_callback:
                progress_callback("Initializing resource monitor...", 0)
            
            monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
            monitor_thread.start()
            
            # Configure system for limited resource usage
            self._configure_system()
            
            if progress_callback:
                progress_callback("Safe execution environment ready", 5)
            
            yield self
            
        except Exception as e:
            print(f"🚨 Exception in controlled execution: {e}")
            self._emergency_cleanup()
            raise e
        finally:
            self._kill_switch = True
            if monitor_thread:
                monitor_thread.join(timeout=2)
            self._cleanup_resources()
    
    def _configure_system(self):
        """Configure system for resource-conscious execution"""
        try:
            # Set process priority to be nice to the system
            os.nice(5)  # Lower priority
            
            # Limit CPU affinity if possible
            try:
                total_cores = os.cpu_count()
                use_cores = max(1, int(total_cores * 0.7))  # Use 70% of cores
                available_cores = list(range(use_cores))
                psutil.Process().cpu_affinity(available_cores)
                print(f"🔧 Limited to {use_cores}/{total_cores} CPU cores")
            except (AttributeError, OSError):
                print("ℹ️  CPU affinity not supported on this system")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not configure system limits: {e}")
    
    def _monitor_resources(self):
        """Monitor system resources and trigger emergency stop if needed"""
        self._monitoring = True
        consecutive_warnings = 0
        
        while not self._kill_switch and self._monitoring:
            try:
                # Check CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.5)
                
                # Check memory usage
                memory = psutil.virtual_memory()
                
                # Warning thresholds - more lenient during model loading
                if self.model_loading_mode:
                    cpu_warning = cpu_percent > 95  # Very high threshold during loading
                    memory_warning = memory.percent > 95  # Very high threshold during loading
                else:
                    cpu_warning = cpu_percent > self.max_cpu_percent
                    memory_warning = memory.percent > self.max_memory_percent
                
                if cpu_warning or memory_warning:
                    consecutive_warnings += 1
                    if consecutive_warnings == 1:  # First warning
                        print(f"⚠️  Resource warning - CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%")
                else:
                    consecutive_warnings = 0
                
                # Emergency brake if resources are critically high
                if (cpu_percent > 95 or memory.percent > 95 or consecutive_warnings > 10):
                    print("🚨 EMERGENCY: Critical resource usage - triggering cleanup")
                    self._emergency_triggered = True
                    self._emergency_cleanup()
                    break
                    
            except Exception as e:
                print(f"Resource monitoring error: {e}")
            
            time.sleep(1.0)
    
    def _emergency_cleanup(self):
        """Emergency resource cleanup"""
        if self._emergency_triggered:
            return  # Already cleaning up
            
        self._emergency_triggered = True
        print("🧹 Emergency cleanup initiated...")
        
        try:
            # Try to import torch for GPU cleanup
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                print("✅ GPU memory cleared")
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️  GPU cleanup error: {e}")
        
        # Force garbage collection
        gc.collect()
        
        # Set kill switch
        self._kill_switch = True
        print("🛑 Emergency cleanup complete")
        
    def _cleanup_resources(self):
        """Clean up resources after execution"""
        try:
            # Clear GPU memory if available
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        except Exception:
            pass
            
        gc.collect()
        self._monitoring = False
        print("🧹 Resource cleanup complete")

class ProgressTracker:
    """Professional progress tracking with accurate estimates"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
    def update(self, step: int, status: str = ""):
        """Update progress with time estimation"""
        self.current_step = step
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if step > 0:
            avg_time_per_step = elapsed / step
            remaining_steps = self.total_steps - step
            eta = remaining_steps * avg_time_per_step
            
            progress_percent = (step / self.total_steps) * 100
            
            # Rate limiting: only print every 0.5 seconds
            if current_time - self.last_update_time > 0.5:
                print(f"📊 {self.description}: {progress_percent:.1f}% "
                      f"({step}/{self.total_steps}) "
                      f"ETA: {eta:.1f}s {status}")
                self.last_update_time = current_time
        else:
            print(f"📊 {self.description}: Starting... {status}")
    
    def complete(self, status: str = "Complete"):
        """Mark as complete"""
        elapsed = time.time() - self.start_time
        print(f"✅ {self.description}: {status} (Total: {elapsed:.2f}s)")

def configure_torch_for_safety():
    """Configure PyTorch for safe resource usage"""
    try:
        import torch
        
        if torch.cuda.is_available():
            # Limit GPU memory growth
            torch.cuda.empty_cache()
            torch.cuda.set_per_process_memory_fraction(0.6)  # Use max 60% of GPU memory
            
            # Use memory-efficient settings
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            
            print("🔧 PyTorch GPU configured for safe usage (60% memory limit)")
        
        # Limit CPU threads
        max_threads = max(1, int(os.cpu_count() * 0.6))
        torch.set_num_threads(max_threads)
        
        print(f"🔧 PyTorch CPU configured ({max_threads} threads)")
        
    except ImportError:
        print("ℹ️  PyTorch not available - skipping GPU configuration")
    except Exception as e:
        print(f"⚠️  Warning: Could not configure PyTorch: {e}")

class SystemResourceMonitor:
    """Monitor system resources during processing"""
    
    def __init__(self):
        self.monitoring = False
        
    def start_monitoring(self):
        """Start monitoring in background"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                status_line = f"CPU: {cpu:5.1f}% | RAM: {memory.percent:5.1f}%"
                
                # Add GPU info if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        gpu_mem = torch.cuda.memory_allocated() / 1024**3
                        gpu_max = torch.cuda.max_memory_allocated() / 1024**3
                        if gpu_max > 0:
                            gpu_percent = (gpu_mem / gpu_max) * 100
                            status_line += f" | GPU: {gpu_percent:5.1f}%"
                except:
                    pass
                
                print(f"\r🔍 Resources: {status_line}", end="", flush=True)
                time.sleep(2)
                
            except Exception:
                break
