#!/usr/bin/env python3
"""
Professional System Resource Monitor for Hand Teleop
Monitors CPU, memory, and GPU usage during WiLoR processing
"""

import psutil
import time
import signal
import sys
from datetime import datetime

class ResourceMonitor:
    def __init__(self):
        self.monitoring = True
        
    def monitor(self, interval=2):
        """Monitor system resources with professional output"""
        print("🔍 Hand Teleop Resource Monitor Started")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.monitoring:
                # Get timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=interval)
                cpu_status = self._get_status_icon(cpu_percent, 70, 90)
                
                # Memory usage
                memory = psutil.virtual_memory()
                mem_status = self._get_status_icon(memory.percent, 70, 85)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_status = self._get_status_icon(disk.percent, 80, 90)
                
                # GPU info (if available)
                gpu_info = self._get_gpu_info()
                
                # Display status
                print(f"\r[{timestamp}] "
                      f"CPU: {cpu_status} {cpu_percent:5.1f}% | "
                      f"RAM: {mem_status} {memory.percent:5.1f}% | "
                      f"Disk: {disk_status} {disk.percent:4.1f}% | "
                      f"GPU: {gpu_info}", end="", flush=True)
                
                # Check for critical usage
                if cpu_percent > 95 or memory.percent > 95:
                    print(f"\n🚨 CRITICAL: Resource usage at dangerous levels!")
                    print(f"   CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%")
                
        except KeyboardInterrupt:
            print("\n\n✅ Resource monitoring stopped")
    
    def _get_status_icon(self, value, warning_threshold, critical_threshold):
        """Get status icon based on thresholds"""
        if value < warning_threshold:
            return "🟢"
        elif value < critical_threshold:
            return "🟡"
        else:
            return "🔴"
    
    def _get_gpu_info(self):
        """Get GPU information if available"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / 1024**3  # GB
                gpu_max = torch.cuda.max_memory_allocated() / 1024**3  # GB
                gpu_percent = (gpu_memory / gpu_max * 100) if gpu_max > 0 else 0
                gpu_status = self._get_status_icon(gpu_percent, 60, 80)
                return f"{gpu_status} {gpu_percent:4.1f}%"
        except:
            pass
        return "N/A"

def signal_handler(sig, frame):
    print("\n\n🛑 Monitoring interrupted by user")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    monitor = ResourceMonitor()
    monitor.monitor()
