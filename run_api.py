#!/usr/bin/env python3
"""
Face Analysis API Startup Script
Handles proper initialization and startup of the API server
"""

import os
import sys
import logging
from dotenv import load_dotenv
from api import app, load_models
from config import get_config

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('api.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        os.path.join(script_dir, 'opencv_face_detector.pbtxt'),
        os.path.join(script_dir, 'opencv_face_detector_uint8.pb'),
        os.path.join(script_dir, 'age_deploy.prototxt'),
        os.path.join(script_dir, 'age_net.caffemodel'),
        os.path.join(script_dir, 'gender_deploy.prototxt'),
        os.path.join(script_dir, 'gender_net.caffemodel')
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(os.path.basename(file))
    
    if missing_files:
        print("❌ Missing required model files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all model files are in the project directory.")
        return False
    
    print("✅ All required model files found")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'logs', 'cache']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main startup function"""
    print("🚀 Starting Face Analysis API...")
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Load models in background
    print("📦 Loading AI models...")
    load_models()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Starting server on {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 API Documentation: http://{host}:{port}/api/health")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 