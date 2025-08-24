# 🧪 Manual Testing Guide: Frontend + Backend Integration

## 🚀 **Current Status**
- ✅ **Backend**: Running on `http://localhost:8000` (Healthy)
- ✅ **Frontend**: Running on `http://localhost:3000` (Active)
- ✅ **Web Interface**: Available at `http://localhost:3000/web/web_interface.html`

---

## 📋 **Quick Tests You Can Do Right Now**

### **1. 🔍 Backend API Tests**
```bash
# Health check
curl http://localhost:8000/api/health

# API documentation
curl http://localhost:8000/docs
```

### **2. 🌐 Frontend Access Tests**
- **Main Interface**: http://localhost:3000/web/web_interface.html
- **Camera Diagnostics**: http://localhost:3000/web/camera_diagnostics.html

### **3. 🤖 Hand Tracking Integration Tests**

#### **Step 1: Open Web Interface**
1. Go to `http://localhost:3000/web/web_interface.html`
2. Click "Show Analytics" to open the tracking panel
3. Allow camera access when prompted

#### **Step 2: Test Live Tracking**
1. Click "Start Tracking" button
2. Move your hand in front of the camera
3. **Expected Results**:
   - ✅ Green dots on fingertips (thumb, index PIP, index tip)
   - ✅ Coordinate displays updating in real-time
   - ✅ Robot visualization moving with your hand
   - ✅ FPS counter showing ~10-20 FPS (optimized)

#### **Step 3: Test WiLoR API Integration**
1. With tracking running, click "Capture & Process WiLoR"
2. **Expected Results**:
   - ✅ Status shows "Processing with WiLoR..."
   - ✅ Backend processes the image (check terminal logs)
   - ✅ Status updates to show results

#### **Step 4: Test Performance**
1. Monitor Chrome Task Manager (Shift+Esc)
2. **Expected Results**:
   - ✅ Chrome tab stays responsive (not frozen)
   - ✅ CPU usage reasonable (<70%)
   - ✅ Memory usage stable (no leaks)

---

## 🐛 **Troubleshooting Guide**

### **Problem: Chrome Becomes Unresponsive**
- ✅ **FIXED**: Throttled MediaPipe to 10 FPS
- ✅ **FIXED**: Throttled API calls to 2/second
- ✅ **FIXED**: Reduced resource allocation

### **Problem: High CPU/Memory Usage**
- ✅ **FIXED**: Backend now uses 50% CPU (was 70%)
- ✅ **FIXED**: Memory limited to 4GB (was 8GB)
- ✅ **FIXED**: GPU memory reduced to 256MB chunks

### **Problem: Slow API Response**
- ✅ **FIXED**: Added 1.5s timeout for faster feedback
- ✅ **FIXED**: Reduced image quality to 60% for faster processing

---

## 🎯 **What to Test For**

### **✅ Functional Tests**
- [ ] Camera initializes without errors
- [ ] Hand tracking displays fingertip coordinates
- [ ] Robot visualization responds to hand movements
- [ ] WiLoR API calls work (even if slow)
- [ ] Status messages update correctly

### **⚡ Performance Tests**
- [ ] Chrome remains responsive during tracking
- [ ] FPS stays stable (10-20 range)
- [ ] Memory usage doesn't grow continuously
- [ ] No JavaScript errors in console

### **🔗 Integration Tests**
- [ ] Frontend connects to backend API
- [ ] WebSocket communication works (if available)
- [ ] Error handling works (disconnect backend, test frontend)

---

## 🎉 **Success Criteria**

**The system is working correctly if**:
1. ✅ You can start hand tracking without Chrome freezing
2. ✅ Fingertip detection works in real-time
3. ✅ Robot visualization moves smoothly
4. ✅ API calls complete within reasonable time
5. ✅ Browser stays responsive throughout testing

---

## 🔧 **Advanced Testing**

### **Browser DevTools Testing**
1. Open DevTools (F12)
2. Go to **Performance** tab
3. Start recording, enable tracking, record for 10 seconds
4. Check for:
   - No long tasks (>50ms)
   - Smooth frame rate
   - No memory spikes

### **Network Tab Testing**
1. Open **Network** tab in DevTools
2. Start tracking
3. Check API calls to `/api/track`
4. Verify response times and success rates

---

**🎯 Ready to test! Everything should work smoothly now with the performance optimizations.**
