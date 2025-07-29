#!/usr/bin/env python3
"""
Hand Teleop - Main Entry Point
Hand-controlled robot manipulation system
"""
import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Hand Teleop - Hand-controlled robot manipulation")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Web API command
    web_parser = subparsers.add_parser('web', help='Start web API server')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host address')
    web_parser.add_argument('--port', type=int, default=8000, help='Port number')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Start desktop GUI')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run hand tracking test')
    test_parser.add_argument('--image', help='Test with specific image file')
    
    args = parser.parse_args()
    
    if args.command == 'web':
        print("🌐 Starting Hand Teleop Web API...")
        print(f"📍 Server starting on http://{args.host}:{args.port}")
        
        # Note: For production use, run via scripts/run_web_api.sh
        # This ensures proper conda environment activation
        print("💡 For best results, use: ./scripts/run_web_api.sh")
        
    elif args.command == 'gui':
        print("🖥️  Starting Hand Teleop GUI...")
        print("💡 For best results, use: ./scripts/run_gui.sh")
        
    elif args.command == 'test':
        print("🧪 Running hand tracking test...")
        if args.image:
            print(f"📸 Testing with image: {args.image}")
        else:
            print("📷 Testing with webcam...")
        print("💡 See tests/ directory for available test scripts")
        
    else:
        parser.print_help()
        print("\n🚀 Hand Teleop - Hand-controlled robot manipulation")
        print("📋 Quick Start:")
        print("  ./scripts/run_web_api.sh  - Start web server")
        print("  ./scripts/run_gui.sh      - Start desktop GUI")
        print("\n📁 Project Structure:")
        print("  backend/       - Web API server")
        print("  frontend/      - Web interface & Remix components")
        print("  core/          - Hand tracking & robot control")
        print("  examples/      - Example applications")
        print("  scripts/       - Setup and run scripts")

if __name__ == "__main__":
    main()