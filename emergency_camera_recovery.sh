#!/bin/bash

echo "🚨 EMERGENCY CAMERA RECOVERY SCRIPT"
echo "===================================="

# Check if camera processes are running
echo "1. Checking for camera processes..."
CAMERA_PROCS=$(ps aux | grep -E "(chrome.*camera|firefox.*camera|v4l|uvc)" | grep -v grep)
if [ ! -z "$CAMERA_PROCS" ]; then
    echo "Found camera-related processes:"
    echo "$CAMERA_PROCS"
else
    echo "No obvious camera processes found"
fi

echo ""
echo "2. Checking video devices..."
ls -la /dev/video* 2>/dev/null || echo "No video devices found"

echo ""
echo "3. Checking kernel messages for camera errors..."
dmesg | grep -i -E "(uvc|camera|video|v4l)" | tail -10

echo ""
echo "4. Checking if camera is in use..."
lsof /dev/video* 2>/dev/null || echo "lsof: No processes using video devices (or lsof not available)"

echo ""
echo "🔧 RECOVERY STEPS:"
echo "=================="
echo "Run these commands one by one:"
echo ""
echo "# 1. Kill all browser processes (SAVE YOUR WORK FIRST!)"
echo "killall chrome firefox chromium 2>/dev/null"
echo ""
echo "# 2. Reset USB video devices"
echo "sudo rmmod uvcvideo 2>/dev/null"
echo "sudo modprobe uvcvideo"
echo ""
echo "# 3. Reset USB subsystem (if needed)"
echo "sudo rmmod ehci_pci ehci_hcd 2>/dev/null"
echo "sudo modprobe ehci_hcd"
echo "sudo modprobe ehci_pci"
echo ""
echo "# 4. Check if camera is accessible"
echo "v4l2-ctl --list-devices"
echo ""
echo "# 5. Test camera with simple command"
echo "ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 test_frame.jpg 2>&1"
echo ""
echo "⚠️ If none of these work, you need to RESTART THE SYSTEM"
echo ""
echo "🔍 After restart, run this to check what caused the freeze:"
echo "dmesg | grep -i -E '(uvc|camera|video|v4l|usb)' | tail -20"
