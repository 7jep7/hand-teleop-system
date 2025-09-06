#!/usr/bin/env python3
"""
Comprehensive test runner for hand-teleop-system

Organizes and runs different categories of tests with appropriate setup.
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Run hand-teleop-system tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--functional", action="store_true", help="Run functional tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Hand Teleop System Test Runner")
    print("=" * 50)
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    if args.coverage:
        pytest_cmd.extend(["--cov=core", "--cov-report=html", "--cov-report=term"])
    
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    success = True
    
    if args.unit or args.all:
        cmd = pytest_cmd + ["tests/unit/"]
        success &= run_command(cmd, "Unit Tests")
    
    if args.api or args.all:
        cmd = pytest_cmd + ["tests/api/"]
        success &= run_command(cmd, "API Tests")
    
    if args.functional or args.all:
        cmd = pytest_cmd + ["tests/functional/"]
        success &= run_command(cmd, "Functional Tests")
    
    if args.integration or args.all:
        cmd = pytest_cmd + ["tests/integration/"]
        success &= run_command(cmd, "Integration Tests")
    
    # If no specific category chosen, run all
    if not any([args.unit, args.api, args.functional, args.integration, args.all]):
        cmd = pytest_cmd + ["tests/"]
        success &= run_command(cmd, "All Tests")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
