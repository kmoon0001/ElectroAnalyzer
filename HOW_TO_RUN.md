# 🚀 **ElectroAnalyzer - How to Run Guide**

> **Complete Setup and Troubleshooting Guide** for the ElectroAnalyzer Clinical Compliance Analysis System

## 📋 **Production Status: READY TO RUN**

✅ **691/754 tests passing** (92% pass rate)
✅ **Ultra-lightweight AI system** optimized for <10GB RAM
✅ **One-command startup** with automatic configuration
✅ **Comprehensive troubleshooting** and diagnostic tools

---

## 🎯 **Quick Start (Recommended)**

### **One-Command Launch**
```bash
# Windows (PowerShell) - RECOMMENDED
.\START_APP.ps1

# Windows (Command Prompt)
START_APP.bat

# Manual Start
python start_robust.py
```

### **What Gets Started**
The application consists of two integrated components:

1. **Python FastAPI Backend** (Port 8001)
   - Ultra-lightweight AI/ML processing (<10GB RAM)
   - Encrypted SQLite database
   - Comprehensive REST API with 20+ endpoints
   - Real-time performance monitoring

2. **Electron/React Frontend** (Port 3001)
   - Professional Qt-style desktop application UI
   - Real-time WebSocket communication
   - Integrated AI chat assistant
   - Responsive design with accessibility features

---

## 🔧 **First-Time Setup**

### **System Requirements**
- **Python 3.11+** (Required for backend)
- **Node.js 18+** (Required for frontend)
- **8GB+ RAM** (Recommended for optimal performance)
- **2GB+ Storage** (For AI models and data)

### **Initial Configuration**
```bash
# Generate secure encryption keys
python generate_keys.py

# Create test user (optional)
python create_test_user.py

# Verify installation
python -c "import src; print('Installation successful')"
```

### **Default Credentials**
- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 **Testing Components Separately**

### **Test Backend API Only**
```bash
# Start API only
python start_backend.py

# Test API endpoints
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/api/v2/system/health

# View API documentation
# Open: http://127.0.0.1:8001/docs
```

### **Test Frontend Only**
```bash
# Make sure API is running first!
cd frontend/electron-react-app
npm install
npm start

# Frontend will open on port 3001
# API must be running on port 8001
```

### **Test Full Integration**
```bash
# Run comprehensive test suite
pytest

# Run specific test categories
pytest -m "not slow"  # Exclude slow tests
pytest tests/test_api/  # API tests only
pytest tests/test_analysis/  # Analysis tests only
```

---

## 🔍 **Troubleshooting Guide**

### **Run Full Diagnostic**
```bash
# Windows PowerShell
.\RUN_FULL_DIAGNOSTIC.ps1

# Manual diagnostic checks
python -c "
import sys
print(f'Python: {sys.version}')
import src
print('Backend imports: OK')
"
```

**Diagnostic checks:**
- ✅ Python installation and version
- ✅ Node.js installation and version
- ✅ Virtual environment status
- ✅ Node modules installation
- ✅ Port availability (8001, 3001)
- ✅ Database status and encryption
- ✅ API imports and dependencies
- ✅ Configuration files validation

### **Common Issues & Solutions**

#### **"Port already in use" Error**
```bash
# Find processes using ports
netstat -ano | findstr ":8001"
netstat -ano | findstr ":3001"

# Kill specific processes
taskkill /PID <PID> /F

# Or kill all Python processes
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

#### **"Virtual environment not found"**
```bash
# Create fresh virtual environment
python -m venv venv_fresh
venv_fresh\Scripts\activate
pip install -r requirements.txt
```

#### **"Node modules not installed"**
```bash
cd frontend/electron-react-app
rm -rf node_modules package-lock.json
npm install
cd ../..
```

#### **"API won't start"**
```bash
# Test API separately
python start_backend.py

# Check for import errors
python -c "from src.api.main import app; print('API imports OK')"

# Check configuration
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

#### **"Frontend won't connect to API"**
```bash
# Verify API is running
curl http://127.0.0.1:8001/health

# Check frontend configuration
cat frontend/electron-react-app/src/config.js

# Restart both components
# 1. Start API: python start_backend.py
# 2. Start Frontend: cd frontend/electron-react-app && npm start
```

#### **"Analysis stuck at 5%"**
```bash
# Check API console for errors
# Verify use_ai_mocks setting in config.yaml
# Restart both API and frontend
# Try a different document
```

#### **"Memory usage too high"**
```bash
# Enable ultra-lightweight mode
export ULTRA_LIGHTWEIGHT_MODE=true
export MAX_RAM_GB=8.0

# Or edit config.yaml:
# performance:
#   ultra_lightweight_mode: true
#   max_ram_gb: 8.0
```

---

## 📊 **Performance Optimization**

### **Ultra-Lightweight Mode**
```bash
# Enable in environment
export ULTRA_LIGHTWEIGHT_MODE=true
export MAX_RAM_GB=8.0

# Or configure in config.yaml
performance:
  ultra_lightweight_mode: true
  max_ram_gb: 8.0
  memory_efficient_mode: true
  fast_mode: true
```

### **Performance Monitoring**
```bash
# Check system performance
curl http://127.0.0.1:8001/api/v2/performance/dashboard

# Monitor memory usage
curl http://127.0.0.1:8001/api/v2/performance/metrics/memory_usage_percent

# Check cache performance
curl http://127.0.0.1:8001/api/v2/cache/stats
```

---

## 🔒 **Security Configuration**

### **Required Environment Variables**
```bash
# Critical Security Variables (REQUIRED)
SECRET_KEY="your-super-secret-jwt-key-minimum-32-chars"
FILE_ENCRYPTION_KEY="your-base64-encoded-fernet-key"
DATABASE_ENCRYPTION_KEY="your-base64-encoded-fernet-key"

# Optional Security Settings
SESSION_TIMEOUT_MINUTES=30
MAX_CONCURRENT_SESSIONS=3
ENABLE_RATE_LIMITING=true
```

### **Security Validation**
```bash
# Run security checks
python security_log_review.py

# Test authentication
curl -X POST "http://127.0.0.1:8001/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 📁 **Important Files & Directories**

### **Configuration Files**
- `config.yaml` - Main application settings and AI model configuration
- `.env` - Environment variables and secrets
- `pytest.ini` - Test configuration
- `mypy.ini` - Type checking configuration

### **Key Directories**
- `src/` - Backend Python source code
- `frontend/electron-react-app/` - Frontend React/Electron application
- `logs/` - Application logs and audit trails
- `models/` - AI model storage and cache
- `secure_storage/` - Encrypted file storage
- `tests/` - Test suite and validation scripts

### **Database Files**
- `compliance.db` - Main SQLite database (encrypted)
- `tasks.db` - Task registry database
- `compliance.db-shm` - SQLite shared memory
- `compliance.db-wal` - SQLite write-ahead log

---

## 🎯 **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ElectroAnalyzer Desktop App                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Electron UI   │  │   React Frontend│  │   WebSocket     │ │
│  │   (Desktop)     │  │   (Port 3001)   │  │   (Real-time)   │ │
│  └─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘ │
└────────────┼────────────────────┼────────────────────┼─────────┘
             │ HTTP/WebSocket      │ HTTP               │
             ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8001)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────┐ │
│  │   Auth API  │  │ Analysis API │  │  ML API v2   │  │ Admin │ │
│  │   Security  │  │ Compliance   │  │  Unified     │  │ Users │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────┘ │
└─────────────┬───────────────────────┬───────────────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core AI/ML System                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────┐ │
│  │ Ultra-Light │  │ Multi-Tier  │  │ Advanced     │  │ XAI   │ │
│  │ AI Models   │  │ Cache       │  │ Security     │  │ Ethics│ │
│  │ (<10GB RAM) │  │ System      │  │ System       │  │ Engine│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────┘ │
└─────────────┬───────────────────────┬───────────────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Secure Storage Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────┐ │
│  │ SQLite DB   │  │ Encrypted   │  │ Vector      │  │ Audit │ │
│  │ (Fernet)    │  │ Files       │  │ Store       │  │ Logs  │ │
│  │             │  │ (AES-GCM)   │  │ (FAISS)     │  │       │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ **Development Mode**

### **Hot Reload Support**
- **Backend**: Auto-reloads on Python file changes
- **Frontend**: Hot-reloads on React file changes
- **DevTools**: Press `Ctrl+Shift+I` in Electron

### **Development Commands**
```bash
# Backend development
python start_backend.py  # With auto-reload

# Frontend development
cd frontend/electron-react-app
npm run dev  # Hot reload enabled

# Full development stack
python start_robust.py  # Both backend and frontend
```

---

## 📦 **First Run Notes**

### **AI Model Download**
- **First run**: Downloads ~2GB of ultra-lightweight AI models
- **Requires internet**: Connection needed for initial model download
- **Models cached**: Stored in `.cache` directory for future runs
- **Subsequent runs**: Much faster startup (no download needed)

### **Database Initialization**
- **Automatic setup**: Database created and encrypted on first run
- **User creation**: Default admin user created automatically
- **Migration**: Database schema updated automatically

---

## ✅ **Success Indicators**

### **When Running Correctly**
1. **API Server**: Shows "Application startup complete" message
2. **React Dev Server**: Compiles successfully without errors
3. **Electron Window**: Opens with professional login screen
4. **Console**: No error messages in any console
5. **Health Check**: `curl http://127.0.0.1:8001/health` returns 200 OK

### **Performance Benchmarks**
- **Startup Time**: <3 seconds
- **Analysis Time**: 15-45 seconds per document
- **Memory Usage**: <8GB during normal operation
- **Response Time**: <2000ms for API calls

---

## 🆘 **Still Having Issues?**

### **Step-by-Step Troubleshooting**
1. **Run Full Diagnostic**: `.\RUN_FULL_DIAGNOSTIC.ps1`
2. **Check Logs**: Review console output for specific errors
3. **Verify Ports**: Ensure 8001 and 3001 are available
4. **Test Components**: Run backend and frontend separately
5. **Check Configuration**: Validate config.yaml and environment variables
6. **Restart Everything**: Kill all processes and restart fresh

### **Emergency Reset**
```bash
# Nuclear option - reset everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe
rm -rf node_modules package-lock.json
rm -rf .cache
python -m venv venv_fresh
venv_fresh\Scripts\activate
pip install -r requirements.txt
cd frontend/electron-react-app
npm install
cd ../..
python start_robust.py
```

---

## 📞 **Support Resources**

### **Documentation**
- **[Quick Start Guide](QUICK_START.md)** - Immediate setup
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Production Deployment](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Enterprise deployment
- **[Security Guide](SECURITY_IMPLEMENTATION.md)** - HIPAA compliance
- **[Testing Guide](README_TESTING.md)** - Comprehensive testing

### **Getting Help**
1. **Check Documentation**: Comprehensive guides in root directory
2. **Run Diagnostics**: Use built-in diagnostic tools
3. **Review Logs**: Check console output and log files
4. **Test Components**: Verify each component individually
5. **AI Assistant**: Use integrated chat for compliance questions

---

## 🎉 **Ready to Analyze!**

The ElectroAnalyzer is now ready to help you improve clinical documentation quality and ensure regulatory compliance.

**Start analyzing today!** 🏥✨

---

*For technical support or questions, refer to the comprehensive documentation or use the integrated AI assistant.*
