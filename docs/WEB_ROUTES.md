# 🌐 Web Application Routes & Testing

## 🚀 **Working Routes (Fixed & Verified)**

### **Backend API Routes (Production)**
When running `python main.py --start` (Backend on port 8000):

| Route | File Served | Description | Status |
|-------|-------------|-------------|---------|
| `/web` | `frontend/web/web_interface.html` | Main web interface | ✅ Fixed |
| `/demo` | `frontend/demos/chrome_safe_demo.html` | Chrome-safe demo | ✅ New |
| `/legacy-demo` | `frontend/demos/legacy_demo.html` | Original demo | ✅ New |
| `/demo.html` | `frontend/demos/legacy_demo.html` | Legacy demo (alt route) | ✅ Fixed |
| `/react-demo` | `frontend/demos/chrome_safe_demo.html` | Chrome-safe demo (alt route) | ✅ Fixed |
| `/so101-simulation` | `frontend/web/web_interface.html` | Web interface (alt route) | ✅ Fixed |

### **Static File Routes**
| Route | Directory | Description |
|-------|-----------|-------------|
| `/frontend/*` | `frontend/` | All frontend files (dev mode) |
| `/static/*` | `static/` | Static assets |

## 🔧 **Development Mode Routes**
When running `python main.py --dev` (Frontend server on port 3000):

| URL | File | Description |
|-----|------|-------------|
| `http://localhost:3000/index.html` | `frontend/index.html` | Main dashboard |
| `http://localhost:3000/demos/chrome_safe_demo.html` | Chrome-safe demo | Recommended for testing |
| `http://localhost:3000/demos/legacy_demo.html` | Original demo | Your old `demo.html` |
| `http://localhost:3000/web/web_interface.html` | Main web interface | Full feature set |

## 🧪 **Testing Web Application**

### **Quick Test Commands**
```bash
# Development mode (recommended for testing)
python main.py --dev
# Access: http://localhost:3000/index.html

# Production mode 
python main.py --start
# Access: http://localhost:8000/demo
```

### **Route Test Script**
```bash
# Test all routes are accessible
curl -I http://localhost:8000/web
curl -I http://localhost:8000/demo  
curl -I http://localhost:8000/legacy-demo
curl -I http://localhost:8000/demo.html
```

## 📁 **File Organization**

```
frontend/
├── index.html                    # Main dashboard
├── demos/
│   ├── chrome_safe_demo.html     # Chrome-optimized demo
│   └── legacy_demo.html          # Original demo.html (renamed)
├── web/
│   └── web_interface.html        # Main web interface
└── diagnostics/
    ├── camera_diagnostic.html    # Camera testing
    ├── camera_safe_mode.html     # Safe mode camera
    └── minimal_camera_test.html  # Minimal camera test
```

## ⚠️ **Important Notes**

1. **Chrome-Safe Demo**: Use `/demo` or `chrome_safe_demo.html` for Chrome testing
2. **Legacy Demo**: Your original `demo.html` is now `legacy_demo.html`
3. **Main Interface**: `/web` serves the full web interface
4. **Development**: Use `--dev` mode for frontend development
5. **Production**: Backend routes work with static file serving

## 🔍 **Integration Tests**

The routes are tested in:
- `tests/integration/test_comprehensive.py` - Tests all working routes
- `tests/api/test_backend.py` - API endpoint testing

All routes now point to existing files and are verified working! ✅
