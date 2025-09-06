#!/bin/bash

echo "🔧 Chrome Camera Service Recovery Tool"
echo "====================================="

while true; do
    # Find stuck Chrome video capture services
    STUCK_PIDS=$(ps aux | grep "video_capture.mojom.VideoCaptureService" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$STUCK_PIDS" ]; then
        echo "Found stuck Chrome video capture services: $STUCK_PIDS"
        
        # Check if any are holding camera devices
        for pid in $STUCK_PIDS; do
            if lsof -p $pid 2>/dev/null | grep -q "/dev/video"; then
                echo "PID $pid is holding camera, killing..."
                kill $pid
                sleep 1
                echo "Camera should be free for ~10 seconds"
            fi
        done
    fi
    
    sleep 2
done
