#!/usr/bin/env python3
"""
Production Health Check - Verify deployment readiness
Quick startup test for Render.com
"""

import sys
import os

def check_deployment():
    """Check if all essential components are available"""
    
    print("🔍 Checking deployment readiness...")
    
    # Check Python version
    print(f"✅ Python {sys.version}")
    
    # Check essential imports
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI not available: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except ImportError as e:
        print(f"❌ Uvicorn not available: {e}")
        return False
        
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV not available: {e}")
        return False
        
    try:
        import mediapipe
        print(f"✅ MediaPipe {mediapipe.__version__}")
    except ImportError as e:
        print(f"❌ MediaPipe not available: {e}")
        return False
    
    # Check backend import
    try:
        sys.path.append('.')
        from backend.render_backend import app
        print("✅ Backend API imports successfully")
    except ImportError as e:
        print(f"❌ Backend import failed: {e}")
        return False
    
    # Check environment variables
    port = os.environ.get("PORT", "8000")
    disable_wilor = os.environ.get("DISABLE_WILOR", "false")
    print(f"✅ PORT: {port}")
    print(f"✅ DISABLE_WILOR: {disable_wilor}")
    
    print("🚀 Deployment check passed!")
    return True

if __name__ == "__main__":
    success = check_deployment()
    sys.exit(0 if success else 1)
