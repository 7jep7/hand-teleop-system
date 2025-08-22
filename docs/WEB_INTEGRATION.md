# WiLoR Hand Tracking - Web Integration Guide

This project provides a complete web-based hand tracking solution using WiLoR that's ready for integration with your Remix website at jonaspetersen.com.

## 🚀 Quick Start

### 1. Start the Web API Server

```bash
python3 manage.py start
# OR for full resource management:
./scripts/run_web_api.sh
```

This starts a FastAPI server at `http://localhost:8000` with:
- **Demo Interface**: `http://localhost:8000/demo` (built-in demo)
- **Full Web Interface**: `http://localhost:8000/web` (advanced interface)
- **API Endpoint**: `http://localhost:8000/api/track`
- **Health Check**: `http://localhost:8000/health`

### 2. For Remix Integration

Drop the `remix-component.tsx` into your Remix app and use it:

```tsx
// app/routes/hand-tracking.tsx
import WiLoRHandTracking from '~/components/WiLoRHandTracking';

export default function HandTrackingPage() {
  return (
    <div>
      <h1>Hand Tracking Demo</h1>
      <WiLoRHandTracking />
    </div>
  );
}
```

## 🔧 Technical Architecture

### Dual Environment Setup
- **j11n environment**: Runs the FastAPI web server (lightweight)
- **hand-teleop environment**: Processes WiLoR hand tracking (heavy ML models)

This separation ensures:
- ✅ Fast web server startup
- ✅ Isolated ML processing 
- ✅ No VS Code crashes
- ✅ Easy integration with existing websites

### API Endpoints

#### POST `/api/track`
Upload an image and get hand tracking results.

**Request:**
```bash
curl -X POST http://localhost:8000/api/track \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image", "robot_type": "so101", "tracking_mode": "wilor"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Hand detected and processed successfully",
  "hand_detected": true,
  "overlay_image": "data:image/jpeg;base64,/9j/4AAQ...",
  "hand_data": {
    "bbox": [100, 50, 200, 150],
    "keypoints_2d": [[120, 80], [130, 90], ...]
  },
  "keypoint_count": 21
}
```

## 🎨 Styling & Integration

The components use **Tailwind CSS** classes that match your existing website:
- Responsive grid layout (`lg:grid-cols-2`)
- Shadow cards (`shadow-lg`)
- Color scheme matches jonaspetersen.com
- Smooth animations and transitions

## 📱 Features

### Web Interface
- ✅ Live camera feed
- ✅ One-click capture and processing
- ✅ Real-time overlay visualization
- ✅ Progress indicators
- ✅ Error handling
- ✅ Mobile responsive

### Hand Tracking Visualization
- 🟢 **Green box**: Hand bounding box
- 🟡 **Yellow dots**: Fingertips (5 points)
- 🔵 **Blue dots**: Joint positions (16 points)

## 🔒 Production Considerations

### For jonaspetersen.com deployment:

1. **Update CORS settings** in `render_backend.py`:
   ```python
   allow_origins=["https://jonaspetersen.com", "https://www.jonaspetersen.com"]
   ```

2. **Environment variables**:
   ```bash
   export API_URL="https://api.jonaspetersen.com"
   export ENVIRONMENT="production"
   ```

3. **SSL/HTTPS**: Camera access requires HTTPS in production

4. **Server deployment**: 
   ```bash
   uvicorn render_backend:app --host 0.0.0.0 --port 8000 --workers 1
   ```

## 🛠️ Development

### Files Structure
```
├── backend/
│   └── render_backend.py      # FastAPI backend server
├── frontend/
│   └── web/
│       ├── web_interface.html # Full web interface  
│       └── camera_diagnostics.html # Camera diagnostics
├── scripts/
│   └── run_web_api.sh        # Launcher script
├── manage.py                 # Project manager
└── examples/
    └── wilor_gui_app.py      # Original tkinter app (fallback)
```

### Environment Dependencies
- **j11n**: FastAPI, OpenCV, NumPy, Pillow
- **hand-teleop**: WiLoR, PyTorch, MediaPipe, all ML dependencies

## 🚨 Troubleshooting

### Common Issues

1. **"Could not access camera"**
   - Check browser permissions
   - Ensure HTTPS in production
   - Try different browsers

2. **"No hand detected"**
   - Position RIGHT hand clearly in view
   - Ensure good lighting
   - Hand should be 20-50cm from camera

3. **Processing timeouts**
   - First run takes 20-30 seconds (model loading)
   - Subsequent runs are much faster
   - Check hand-teleop environment is working

4. **API connection failed**
   - Ensure web API server is running
   - Check firewall/port 8000
   - Verify CORS settings

### Debug Commands
```bash
# Check environments
conda env list

# Test hand-teleop directly
conda activate /mnt/nvme0n1p8/conda-envs/hand-teleop
python -c "from hand_teleop.hand_pose.factory import create_estimator; print('WiLoR OK')"

# Test web API
curl http://localhost:8000/health
```

## 🎯 Next Steps

1. **Deploy to jonaspetersen.com**
2. **Add authentication** (if needed)
3. **Database integration** (save results)
4. **Advanced visualizations** (3D hand model)
5. **Multi-hand support** (left + right hands)

---

**Ready for integration!** 🚀 The web API provides a clean separation between your website and the heavy ML processing, making it perfect for production deployment.
