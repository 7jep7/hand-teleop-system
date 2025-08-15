#!/usr/bin/env python3
"""
Minimal WiLoR test - just import and basic setup
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔧 Testing imports...")

try:
    import cv2
    print("✅ OpenCV imported")
except Exception as e:
    print(f"❌ OpenCV failed: {e}")
    sys.exit(1)

try:
    from core.hand_pose.factory import create_estimator
    print("✅ Factory imported")
except Exception as e:
    print(f"❌ Factory failed: {e}")
    sys.exit(1)

print("🧠 Creating WiLoR estimator (this will take time)...")
try:
    estimator = create_estimator("wilor")
    print("✅ WiLoR estimator created successfully!")
    print(f"📊 Estimator type: {type(estimator)}")
    print(f"📊 Pipe type: {type(estimator.pipe)}")
    print(f"📊 Available methods: {[m for m in dir(estimator.pipe) if not m.startswith('_')]}")
except Exception as e:
    print(f"❌ WiLoR creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ All tests passed! WiLoR is working correctly.")
print("💡 You can now run the full test_wilor_simple.py safely.")
