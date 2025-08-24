# 🤖 Hand Teleop Remix Component

A production-ready React component for integrating WiLoR hand tracking into Remix applications.

## ✅ **Recent Updates (Fixed)**

- ✅ Fixed React import issues (`useEffect` properly imported)
- ✅ Updated API endpoint to use JSON payload (matches current backend)
- ✅ Added environment-based endpoint switching (dev/prod)
- ✅ Enhanced interface with latest backend response format
- ✅ Added processing time and robot angles display
- ✅ Improved error handling and loading states

## 🚀 **Installation**

### 1. **Copy Component**
```bash
cp integrations/remix/remix-component.tsx app/components/WiLoRHandTracking.tsx
```

### 2. **Install Dependencies**
```bash
npm install react react-dom @types/react @types/react-dom
```

### 3. **Use in Remix Route**
```tsx
// app/routes/hand-tracking.tsx
import WiLoRHandTracking from "~/components/WiLoRHandTracking";

export default function HandTrackingPage() {
  return (
    <div>
      <h1>Hand Tracking Demo</h1>
      <WiLoRHandTracking />
    </div>
  );
}
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# .env
NODE_ENV=development  # Uses localhost:8000
NODE_ENV=production   # Uses hand-teleop-api.onrender.com
```

### **API Endpoints**
- **Local Development**: `http://localhost:8000/api/track`
- **Production**: `https://hand-teleop-api.onrender.com/api/track`

## 📋 **Features**

### **Current Capabilities**
- ✅ Real-time camera access
- ✅ WiLoR hand pose estimation
- ✅ Hand detection with bounding boxes
- ✅ 2D/3D keypoint visualization
- ✅ Robot angle calculation
- ✅ Processing time display
- ✅ Responsive Tailwind UI
- ✅ Error handling and loading states

### **API Integration**
```json
{
  "success": true,
  "hand_detected": true,
  "processing_time_ms": 1250,
  "keypoint_count": 21,
  "overlay_image": "data:image/jpeg;base64,...",
  "hand_data": {
    "bbox": [100, 150, 300, 400],
    "keypoints_2d": [[x1, y1], [x2, y2], ...],
    "keypoints_3d": [[x1, y1, z1], ...]
  },
  "robot_angles": {
    "shoulder_pan": 1.2,
    "shoulder_lift": -0.8,
    "elbow": 2.1,
    "wrist_1": -1.4,
    "wrist_2": 0.5,
    "wrist_3": 0.0
  }
}
```

## 🎯 **Usage Instructions**

### **For Users**
1. Allow camera permissions when prompted
2. Position your **right hand** in the camera view
3. Click "Capture & Process Hand" button
4. Wait for WiLoR processing (20-30 seconds on first run)
5. View hand tracking overlay with keypoints

### **For Developers**
```tsx
// Customization example
<WiLoRHandTracking 
  className="custom-styling"
  onResult={(result) => {
    console.log('Hand tracking result:', result);
    // Handle result in your application
  }}
  onError={(error) => {
    console.error('Tracking error:', error);
    // Handle errors
  }}
/>
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **TypeScript Errors**
   ```bash
   npm install @types/node @types/react @types/react-dom
   ```

2. **Camera Access Denied**
   - Check browser permissions
   - Ensure HTTPS in production
   - Test with different browser

3. **API Connection Failed**
   - Verify backend is running (local: `http://localhost:8000/api/health`)
   - Check network connectivity
   - Confirm CORS settings

4. **Slow Processing**
   - First WiLoR run takes 20-30 seconds (model loading)
   - Subsequent calls are much faster
   - Consider showing loading state

## 🌟 **Integration Status**

✅ **Ready for Production**
- Modern React hooks (useState, useEffect, useCallback)
- TypeScript support with proper interfaces
- Tailwind CSS styling
- Environment-aware API endpoints
- Comprehensive error handling
- Mobile-responsive design

## 📚 **Related Files**

- **Backend API**: `backend/render_backend.py`
- **Local Frontend**: `frontend/web/web_interface.html`
- **Production Demo**: https://jonaspetersen.com (iframe integration)
- **API Documentation**: https://hand-teleop-api.onrender.com/docs

---

**🎉 This component is now fully updated and production-ready!**
