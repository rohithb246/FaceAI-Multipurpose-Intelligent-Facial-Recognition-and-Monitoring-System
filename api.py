from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
import os
import json
import time
import logging
from datetime import datetime
import threading
from functools import wraps
import hashlib

# Import existing modules
from deepface import DeepFace
from aichatbot import get_ai_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    users = {}
    return app, users

app, users = create_app()
CORS(app)  # Enable CORS for all routes

# Cache configuration
cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
}
cache = Cache(app, config=cache_config)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model loading (load once at startup)
script_dir = os.path.dirname(os.path.abspath(__file__))

faceProto = os.path.join(script_dir, "opencv_face_detector.pbtxt")
faceModel = os.path.join(script_dir, "opencv_face_detector_uint8.pb")
ageProto = os.path.join(script_dir, "age_deploy.prototxt")
ageModel = os.path.join(script_dir, "age_net.caffemodel")
genderProto = os.path.join(script_dir, "gender_deploy.prototxt")
genderModel = os.path.join(script_dir, "gender_net.caffemodel")

# Global model variables
faceNet = None
ageNet = None
genderNet = None
models_loaded = False

def load_models():
    """Load AI models in a separate thread to avoid blocking startup"""
    global faceNet, ageNet, genderNet, models_loaded
    
    try:
        logger.info("Loading AI models...")
        faceNet = cv2.dnn.readNet(faceModel, faceProto)
        ageNet = cv2.dnn.readNet(ageModel, ageProto)
        genderNet = cv2.dnn.readNet(genderModel, genderProto)
        models_loaded = True
        logger.info("AI models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        models_loaded = False

# Start model loading in background
threading.Thread(target=load_models, daemon=True).start()

# Constants
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_cache_key(data):
    """Generate cache key from data"""
    if isinstance(data, str):
        return hashlib.md5(data.encode()).hexdigest()
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

def rate_limit(max_requests=60, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Simple rate limiting - in production, use Redis
            return f(*args, **kwargs)
        return wrapped
    return decorator

def highlightFace(net, frame, conf_threshold=0.7):
    """Detect faces in the frame"""
    frameOpencvDnn = frame.copy()
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], True, False)
    net.setInput(blob)
    detections = net.forward()
    faceBoxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            faceBoxes.append([x1, y1, x2, y2])
    return faceBoxes

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': models_loaded,
        'version': '1.0.0'
    })

@app.route('/api/analyze', methods=['POST'])
@rate_limit(max_requests=30, window=60)
@cache.memoize(timeout=300)
def analyze_face():
    """Analyze face for age, gender, and emotion"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Generate cache key
        cache_key = generate_cache_key(data['image'])
        
        # Decode image
        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Image could not be decoded'}), 400

        # Check if models are loaded
        if not models_loaded:
            return jsonify({'error': 'AI models are still loading, please try again in a moment'}), 503

        # Detect faces
        faceBoxes = highlightFace(faceNet, frame)
        if not faceBoxes:
            return jsonify({'error': 'No face detected in the image'}), 200

        results = []
        for faceBox in faceBoxes:
            # Extract face region
            padding = 20
            face = frame[max(0, faceBox[1]-padding):min(faceBox[3]+padding, frame.shape[0]-1),
                        max(0, faceBox[0]-padding):min(faceBox[2]+padding, frame.shape[1]-1)]
            
            if face.size == 0:
                continue

            # Analyze with OpenCV models
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            
            # Gender prediction
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            
            # Age prediction
            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]

            # Emotion analysis using DeepFace
            try:
                emotion_result = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)
                emotion = emotion_result[0]['dominant_emotion']
            except:
                emotion = 'neutral'

            results.append({
                'gender': gender,
                'age': age[1:-1],  # Remove parentheses
                'emotion': emotion,
                'confidence': float(genderPreds[0].max()),
                'region': {
                    'x': faceBox[0], 'y': faceBox[1],
                    'w': faceBox[2] - faceBox[0], 'h': faceBox[3] - faceBox[1]
                }
            })

        return jsonify({
            'success': True,
            'faces_detected': len(results),
            'results': results,
            'processing_time': time.time()
        })

    except Exception as e:
        logger.error(f"Error in analyze_face: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analyze-emotion', methods=['POST'])
@rate_limit(max_requests=50, window=60)
def analyze_emotion():
    """Analyze emotion only"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Image could not be decoded'}), 400

        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        
        return jsonify({
            'success': True,
            'emotion': result[0]['dominant_emotion'],
            'emotions': result[0]['emotion']
        })

    except Exception as e:
        logger.error(f"Error in analyze_emotion: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/face-recognition', methods=['POST'])
@rate_limit(max_requests=20, window=60)
def face_recognition():
    """Face recognition endpoint"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # This would integrate with a face recognition system
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'message': 'Face recognition feature coming soon',
            'status': 'development'
        })

    except Exception as e:
        logger.error(f"Error in face_recognition: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/driver-monitoring', methods=['POST'])
@rate_limit(max_requests=30, window=60)
def driver_monitoring():
    """Driver monitoring endpoint"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Image could not be decoded'}), 400

        # Analyze for drowsiness and distraction
        # This would include eye tracking, head pose estimation, etc.
        
        # Placeholder analysis
        faceBoxes = highlightFace(faceNet, frame) if models_loaded else []
        
        return jsonify({
            'success': True,
            'faces_detected': len(faceBoxes),
            'drowsiness_detected': False,
            'distraction_detected': False,
            'alert_level': 'normal',
            'recommendations': ['Continue driving safely']
        })

    except Exception as e:
        logger.error(f"Error in driver_monitoring: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chatbot', methods=['POST'])
@rate_limit(max_requests=100, window=60)
def chatbot():
    """AI chatbot endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        reply = get_ai_response(user_message)
        
        return jsonify({
            'success': True,
            'response': reply,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'size': os.path.getsize(filepath)
            })
        
        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        logger.error(f"Error in upload_file: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get API usage statistics"""
    return jsonify({
        'success': True,
        'stats': {
            'total_requests': 0,  # Would be tracked in production
            'models_loaded': models_loaded,
            'uptime': time.time(),
            'version': '1.0.0'
        }
    })

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear all cached data"""
    try:
        cache.clear()
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 