#!/bin/bash
# 🚀 Manual Render Deployment Trigger
# This script helps troubleshoot and trigger Render deployments

echo "🔧 Render Deployment Troubleshooter"
echo "=================================="

echo "📊 Current Git Status:"
echo "Branch: $(git branch --show-current)"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Message: $(git log -1 --pretty=format:'%s')"

echo -e "\n🔍 Current API Status:"
API_RESPONSE=$(curl -s https://hand-teleop-api.onrender.com/api/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$API_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'  Version: {data.get(\"version\", \"unknown\")}')
    print(f'  Git Commit: {data.get(\"git_commit\", \"missing\")}')
    print(f'  Status: {data.get(\"status\", \"unknown\")}')
except:
    print('  Could not parse API response')
    print('  Raw response:')
    print(sys.stdin.read())
    "
else
    echo "  ❌ API not responding"
fi

echo -e "\n🛠️ Troubleshooting Steps:"
echo "1. Check Render Dashboard: https://dashboard.render.com"
echo "2. Navigate to hand-teleop-api service"
echo "3. Go to 'Events' tab to see deployment activity"
echo "4. Check 'Settings' → 'Build & Deploy' for auto-deploy status"
echo "5. If needed, click 'Manual Deploy' → 'Clear build cache & deploy'"

echo -e "\n📋 Expected vs Actual:"
echo "Expected Version: 1.0.1"
echo "Expected Git Commit: $(git rev-parse --short HEAD)"
echo "Actual Version: $(echo "$API_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('version', 'unknown'))
except:
    print('unknown')
" 2>/dev/null)"

echo -e "\n💡 If auto-deploy isn't working:"
echo "- Render might need manual activation of the webhook"
echo "- GitHub integration might need reconnection"  
echo "- Service might need a manual deploy to 'wake up' auto-deploy"

# Check if we should wait and monitor
read -p "🕐 Monitor API for changes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Monitoring API for 5 minutes..."
    for i in {1..10}; do
        sleep 30
        echo "📍 Check $i/10..."
        NEW_RESPONSE=$(curl -s https://hand-teleop-api.onrender.com/api/health 2>/dev/null)
        NEW_VERSION=$(echo "$NEW_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('version', 'unknown'))
except:
    print('unknown')
        " 2>/dev/null)
        
        if [ "$NEW_VERSION" = "1.0.1" ]; then
            echo "🎉 Deployment detected! New version: $NEW_VERSION"
            echo "$NEW_RESPONSE" | python3 -m json.tool
            break
        else
            echo "   Still version: $NEW_VERSION"
        fi
    done
fi
