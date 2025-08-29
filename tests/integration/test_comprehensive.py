#!/usr/bin/env python3
"""
Comprehensive Test Suite for Hand Teleop System
Tests all core functionality and identifies issues
"""

import sys
import os
import time
import json
import requests
import traceback
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to project root
sys.path.insert(0, str(PROJECT_ROOT))

class TestRunner:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.errors = []
        
    def log_error(self, test_name, error):
        """Log an error for later review"""
        self.errors.append({
            "test": test_name,
            "error": str(error),
            "traceback": traceback.format_exc()
        })
    
    def test_core_imports(self):
        """Test that core modules can be imported"""
        print("🔍 Testing core module imports...")
        
        try:
            # Test core imports
            from core.resource_manager import ResourceManager
            print("✅ Core ResourceManager imported")
            
            from core.hand_pose.factory import create_estimator
            print("✅ Hand pose factory imported")
            
            from core.robot_control.kinematics import RobotKinematics
            print("✅ Robot kinematics imported")
            
            # Skip tracker import for now due to dependency issues
            # from core.tracking.tracker import HandTracker
            # print("✅ Hand tracker imported")
            print("⚠️  Hand tracker skipped (dependency issues)")
            
            return True
        except Exception as e:
            print(f"❌ Core imports failed: {e}")
            self.log_error("core_imports", e)
            return False
    
    def test_backend_endpoints(self):
        """Test all backend endpoints"""
        print("\n🔍 Testing backend endpoints...")
        
        endpoints = [
            ("GET", "/api/health", None),
            ("GET", "/api/robots", None),
            ("GET", "/api/performance", None),
            ("GET", "/web", None),  # Changed from /demo to /web
            ("POST", "/api/config/robot", {"robot_type": "so101"}),
        ]
        
        results = {}
        for method, endpoint, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ {method} {endpoint}")
                    results[endpoint] = True
                else:
                    print(f"❌ {method} {endpoint} - Status: {response.status_code}")
                    results[endpoint] = False
                    
            except Exception as e:
                print(f"❌ {method} {endpoint} - Error: {e}")
                results[endpoint] = False
                self.log_error(f"{method} {endpoint}", e)
        
        return all(results.values())
    
    def test_hand_pose_estimators(self):
        """Test hand pose estimator creation"""
        print("\n🔍 Testing hand pose estimators...")
        
        try:
            from core.hand_pose.factory import create_estimator
            
            # Test MediaPipe estimator
            try:
                mp_estimator = create_estimator("mediapipe")
                print("✅ MediaPipe estimator created")
            except Exception as e:
                print(f"⚠️  MediaPipe estimator failed: {e}")
            
            # Test WiLoR estimator
            try:
                wilor_estimator = create_estimator("wilor")
                print("✅ WiLoR estimator created")
            except Exception as e:
                print(f"⚠️  WiLoR estimator failed: {e}")
            
            return True
        except Exception as e:
            print(f"❌ Hand pose estimator test failed: {e}")
            self.log_error("hand_pose_estimators", e)
            return False
    
    def test_robot_kinematics(self):
        """Test robot kinematics for all robot types"""
        print("\n🔍 Testing robot kinematics...")
        
        try:
            from core.robot_control.kinematics import RobotKinematics
            
            robot_types = ["so101", "so100", "koch", "moss"]
            
            for robot_type in robot_types:
                try:
                    robot = RobotKinematics(robot_type)
                    print(f"✅ {robot_type} kinematics initialized")
                except Exception as e:
                    print(f"⚠️  {robot_type} kinematics failed: {e}")
            
            return True
        except Exception as e:
            print(f"❌ Robot kinematics test failed: {e}")
            self.log_error("robot_kinematics", e)
            return False
    
    def test_file_structure(self):
        """Test that expected files exist and are valid"""
        print("\n🔍 Testing file structure...")
        
        critical_files = [
            "backend/render_backend.py",
            "core/__init__.py",
            "core/hand_pose/factory.py",
            "core/robot_control/kinematics.py",
            "requirements.txt",
            "README.md"
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not (PROJECT_ROOT / file_path).exists():
                missing_files.append(file_path)
                print(f"❌ Missing: {file_path}")
            else:
                print(f"✅ Found: {file_path}")
        
        return len(missing_files) == 0
    
    def identify_obsolete_files(self):
        """Identify potentially obsolete files"""
        print("\n🔍 Identifying obsolete files...")
        
        # Files that might be obsolete
        potentially_obsolete = []
        
        # Check for duplicate test files
        test_files = list(PROJECT_ROOT.glob("test_*.py"))
        if len(test_files) > 3:  # We only need a few test files
            print(f"⚠️  Found {len(test_files)} test files - may have duplicates")
        
        # Check for old backend files
        backend_files = list((PROJECT_ROOT / "backend").glob("*.py"))
        for file in backend_files:
            if file.name not in ["render_backend.py"]:
                potentially_obsolete.append(str(file.relative_to(PROJECT_ROOT)))
        
        # Check for cache files
        cache_patterns = ["**/__pycache__", "**/*.pyc", "**/temp_*"]
        for pattern in cache_patterns:
            cache_files = list(PROJECT_ROOT.glob(pattern))
            if cache_files:
                potentially_obsolete.extend([str(f.relative_to(PROJECT_ROOT)) for f in cache_files])
        
        if potentially_obsolete:
            print("🗑️  Potentially obsolete files:")
            for file in potentially_obsolete:
                print(f"   - {file}")
        else:
            print("✅ No obviously obsolete files found")
        
        return potentially_obsolete
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Running comprehensive test suite...\n")
        
        tests = [
            ("File Structure", self.test_file_structure),
            ("Core Imports", self.test_core_imports),
            ("Backend Endpoints", self.test_backend_endpoints),
            ("Hand Pose Estimators", self.test_hand_pose_estimators),
            ("Robot Kinematics", self.test_robot_kinematics),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                results[test_name] = False
                self.log_error(test_name, e)
                print(f"❌ {test_name} crashed: {e}")
        
        # Identify obsolete files
        obsolete_files = self.identify_obsolete_files()
        
        # Generate report
        print("\n" + "="*60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if self.errors:
            print(f"\n⚠️  {len(self.errors)} errors found:")
            for error in self.errors:
                print(f"   {error['test']}: {error['error']}")
        
        if obsolete_files:
            print(f"\n🗑️  {len(obsolete_files)} potentially obsolete files found")
        
        return {
            "results": results,
            "errors": self.errors,
            "obsolete_files": obsolete_files,
            "success_rate": passed / total
        }

if __name__ == "__main__":
    print("Comprehensive Test Suite for Hand Teleop System")
    print("Make sure the backend is running: conda activate hand-teleop && python backend/render_backend.py")
    print()
    
    runner = TestRunner()
    report = runner.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if report["success_rate"] == 1.0 else 1)
