#!/bin/bash
# Project Management Script for Hand Teleop System

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}Hand Teleop System - Project Manager${NC}"

case "${1:-help}" in
    "clean")
        echo "🧹 Cleaning project..."
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "temp_*" -delete 2>/dev/null || true
        echo "✅ Cleaned"
        ;;
    "test")
        echo "🧪 Running tests..."
        conda activate hand-teleop && python tests/integration/test_comprehensive.py
        ;;
    "backend")
        echo "� Starting backend..."
        conda activate hand-teleop && python backend/render_backend.py
        ;;
    *)
        echo "Usage: $0 [clean|test|backend]"
        ;;
esac
