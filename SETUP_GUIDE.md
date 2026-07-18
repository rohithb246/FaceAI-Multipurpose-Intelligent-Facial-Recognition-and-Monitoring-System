# FaceAI Setup Guide

## Problem Resolution

You encountered a permission error when trying to install Python packages:
```
ERROR: Could not install packages due to an EnvironmentError: [WinError 5] Access is denied
```

## Solutions

### ✅ Solution 1: Use `--user` flag (Recommended)
Install packages to your user directory instead of system directory:
```bash
python -m pip install --user package_name
```

### ✅ Solution 2: Create Virtual Environment (Best Practice)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### ✅ Solution 3: Run as Administrator
Run PowerShell as Administrator and then install packages.

## Current Status

✅ **Flask** - Successfully installed  
✅ **Flask-Mail** - Successfully installed  
✅ **NumPy** - Already installed  
❌ **OpenCV** - Installation interrupted  
❌ **DeepFace** - Installation interrupted  

## Quick Start

### Option 1: Use Minimal Version (Currently Working)
```bash
python app_minimal.py
```
This runs the basic Flask application without heavy dependencies.

### Option 2: Install Full Dependencies
```bash
# Install packages one by one with user flag
python -m pip install --user opencv-python
python -m pip install --user deepface
python -m pip install --user scikit-learn

# Then run the full application
python app.py
```

## Application Features

### Currently Working:
- ✅ Flask web server
- ✅ Basic routing and templates
- ✅ User session management
- ✅ Email configuration (basic)

### Requires Additional Dependencies:
- ❌ Face detection and analysis
- ❌ Age/gender detection
- ❌ Emotion recognition
- ❌ Face recognition

## Troubleshooting

### If packages fail to install:
1. Try using `--user` flag
2. Create a virtual environment
3. Run PowerShell as Administrator
4. Check your internet connection
5. Try installing packages one by one

### If the application doesn't start:
1. Check if Flask is installed: `python -c "import flask"`
2. Check if all required files exist
3. Ensure you're in the correct directory

## Next Steps

1. **For Development**: Use `app_minimal.py` to test basic functionality
2. **For Full Features**: Install missing dependencies using the methods above
3. **For Production**: Set up proper email configuration and database

## Access the Application

Once running, access the application at:
- http://127.0.0.1:5000
- http://localhost:5000

The application is currently running on port 5000 with debug mode enabled. 