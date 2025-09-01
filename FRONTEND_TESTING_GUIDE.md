# Frontend Testing Guide - Dual Backend Support

## Overview
The frontend test files now support testing against both local and deployed backends:

- **Local Backend**: `ws://localhost:8000/api/tracking/live` (for development)
- **Deployed Backend**: `wss://hand-teleop-api.onrender.com/api/tracking/live` (for production testing)

## Updated Test Files

### 1. test_websocket.html
- **URL**: http://localhost:3000/test_websocket.html
- **Features**: 
  - Radio buttons to select local vs deployed backend
  - WebSocket connection testing
  - Camera stream testing
  - Real-time fingertip data display
  - Connection status monitoring

### 2. mvp-demo.html  
- **URL**: http://localhost:3000/mvp-demo.html
- **Features**:
  - Full MVP demonstration
  - Dual backend selection
  - Performance metrics
  - Hand pose visualization
  - Camera controls

## Testing Workflow

### Phase 1: Local Backend Testing
1. Start local backend: `uvicorn backend.render_backend:app --reload --host 0.0.0.0 --port 8000`
2. Open test page: http://localhost:3000/test_websocket.html
3. Select "Local Backend (localhost:8000)"
4. Click "Connect WebSocket"
5. Test camera stream and finger tracking

### Phase 2: Deployed Backend Testing
1. Ensure deployed backend is running: https://hand-teleop-api.onrender.com/api/health
2. Open test page: http://localhost:3000/test_websocket.html
3. Select "Deployed Backend (hand-teleop-api.onrender.com)" 
4. Click "Connect WebSocket"
5. Test camera stream and finger tracking

### Phase 3: Production Readiness Validation
If deployed backend testing works successfully, the integration should work identically on jonaspetersen.com.

## WebSocket Connection Patterns

### Local Development
```javascript
const ws = new WebSocket('ws://localhost:8000/api/tracking/live');
```

### Production Deployment
```javascript 
const ws = new WebSocket('wss://hand-teleop-api.onrender.com/api/tracking/live');
```

## Troubleshooting

### Common Issues
1. **CORS errors**: Ensure backend allows your frontend origin
2. **Certificate issues**: Use `wss://` for deployed backend
3. **Connection timeouts**: Check Render.com service status
4. **Mixed content**: HTTPS sites require WSS connections

### Debug Steps
1. Check browser developer console for errors
2. Verify backend health: GET https://hand-teleop-api.onrender.com/api/health
3. Test WebSocket connectivity independently
4. Monitor network requests in browser dev tools

## Integration for jonaspetersen.com

When integrating on jonaspetersen.com, use the same WebSocket pattern:

```javascript
// For production use
const ws = new WebSocket('wss://hand-teleop-api.onrender.com/api/tracking/live');

ws.onopen = function() {
    console.log('Connected to hand tracking backend');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.fingertips) {
        // Handle fingertip tracking data
        updateFingerVisualization(data.fingertips);
    }
};
```

This testing approach ensures the deployed backend works exactly as expected before integrating with jonaspetersen.com.
