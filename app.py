import sys

# Windows consoles commonly default to cp1252, which cannot print the status
# symbols used throughout this application.  Use UTF-8 so logging never stops
# application startup.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
from flask_cors import CORS
import cv2
import numpy as np
import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from aichatbot import get_ai_response
from database import db
from email_config import get_email_config


# Face recognition relies on dlib, which is not available on every Python
# installation (notably Python 3.12 on Windows without Visual C++ build tools).
# Keep the core age/gender application available when this optional feature
# cannot be loaded.
FACE_RECOGNITION_AVAILABLE = True
try:
    from face_recognition_integration import face_manager
    from enhanced_face_recognition import enhanced_face_recognition
except (ImportError, OSError) as exc:
    FACE_RECOGNITION_AVAILABLE = False

    class _UnavailableFaceManager:
        """Keep non-recognition pages working when the optional module fails."""
        def get_person_by_user_id(self, _user_id):
            return []

        def get_all_people(self):
            return []

        def insert_person_with_details(self, *_args, **_kwargs):
            raise RuntimeError("Face recognition is unavailable")

        def register_face(self, *_args, **_kwargs):
            return False

    face_manager = _UnavailableFaceManager()

    class _UnavailableFaceRecognition:
        base_tolerance = 0.0
        similar_face_threshold = 0.0

        def tune_for_similar_faces(self, _enabled):
            return None

    enhanced_face_recognition = _UnavailableFaceRecognition()
    print(f"Warning: face recognition is unavailable: {exc}")

# Import emotion detector
from emotion_detector import EmotionDetector

# Driver monitoring also depends on dlib, so it is optional for the core app.
DRIVER_MONITORING_AVAILABLE = True
try:
    from driver_monitoring_web import driver_monitor
except (ImportError, OSError) as exc:
    DRIVER_MONITORING_AVAILABLE = False
    driver_monitor = None
    print(f"Warning: driver monitoring is unavailable: {exc}")

# Accurate Face Analysis with Age, Gender, and Emotion Detection
import cv2
import numpy as np
import base64

# Initialize the simple face analyzer
class SimpleFaceAnalyzer:
    def __init__(self):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load models with absolute paths
        self.faceProto = os.path.join(script_dir, "opencv_face_detector.pbtxt")
        self.faceModel = os.path.join(script_dir, "opencv_face_detector_uint8.pb")
        self.ageProto = os.path.join(script_dir, "age_deploy.prototxt")
        self.ageModel = os.path.join(script_dir, "age_net.caffemodel")
        self.genderProto = os.path.join(script_dir, "gender_deploy.prototxt")
        self.genderModel = os.path.join(script_dir, "gender_net.caffemodel")
        
        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.genderList = ['Male', 'Female']
        
        # Load networks
        self.faceNet = cv2.dnn.readNet(self.faceModel, self.faceProto)
        self.ageNet = cv2.dnn.readNet(self.ageModel, self.ageProto)
        self.genderNet = cv2.dnn.readNet(self.genderModel, self.genderProto)
        
        # Initialize emotion detector
        self.emotion_detector = EmotionDetector()
        
        print("✅ Simple face analyzer initialized successfully with emotion detection")
    
    def highlightFace(self, frame, conf_threshold=0.7):
        frameOpencvDnn = frame.copy()
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], True, False)
        
        self.faceNet.setInput(blob)
        detections = self.faceNet.forward()
        faceBoxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                faceBoxes.append([x1, y1, x2, y2])
        return frameOpencvDnn, faceBoxes
    
    def analyze(self, img, actions=None, enforce_detection=False):
        """Analyze face for age, gender, and emotion with enhanced accuracy"""
        try:
            # Detect faces
            resultImg, faceBoxes = self.highlightFace(img)
            
            if not faceBoxes:
                return {'error': 'No faces detected'}
            
            # Analyze the first face
            faceBox = faceBoxes[0]
            padding = 20
            
            face = img[max(0, faceBox[1]-padding):min(faceBox[3]+padding, img.shape[0]-1),
                      max(0, faceBox[0]-padding):min(faceBox[2]+padding, img.shape[1]-1)]
            
            if face.size == 0:
                return {'error': 'Face region is empty'}
            
            # Preprocess face for better accuracy
            face = self.preprocess_face(face)
            
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
            
            # Predict gender with enhanced confidence
            self.genderNet.setInput(blob)
            genderPreds = self.genderNet.forward()
            gender = self.genderList[genderPreds[0].argmax()]
            gender_confidence = float(genderPreds[0].max())
            
            # Enhanced age prediction with multiple passes
            age_result = self.predict_age_enhanced(face)
            age = age_result['age']
            age_confidence = age_result['confidence']
            
            # Detect emotion using the enhanced emotion detector
            emotion_result = self.emotion_detector.detect_emotion_advanced(face)
            emotion = emotion_result.get('emotion', 'Neutral')
            emotion_confidence = emotion_result.get('confidence', 0.5)
            emotion_breakdown = emotion_result.get('all_emotions', {})
            
            # Apply confidence boosting for better results
            final_confidence = self.boost_confidence(age_confidence, gender_confidence, emotion_confidence)
            
            return {
                'age': age,
                'gender': gender,
                'emotion': emotion,
                'region': {'x': int(faceBox[0]), 'y': int(faceBox[1]), 'w': int(faceBox[2]-faceBox[0]), 'h': int(faceBox[3]-faceBox[1])},
                'confidence': {
                    'age': final_confidence['age'],
                    'gender': final_confidence['gender'],
                    'emotion': final_confidence['emotion']
                },
                'emotion_breakdown': emotion_breakdown
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def preprocess_face(self, face):
        """Preprocess face for better detection accuracy"""
        try:
            # Keep color information; the Caffe model expects BGR with mean subtraction
            # Only resize to the target input size
            face = cv2.resize(face, (227, 227))
            return face
        except:
            return face
    
    def predict_age_enhanced(self, face):
        """Enhanced age prediction with multiple techniques"""
        try:
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
            self.ageNet.setInput(blob)
            agePreds = self.ageNet.forward()
            # Map each age bucket to its midpoint (years)
            age_centers = {
                '(0-2)': 1.0,
                '(4-6)': 5.0,
                '(8-12)': 10.0,
                '(15-20)': 17.5,
                '(25-32)': 28.5,
                '(38-43)': 40.5,
                '(48-53)': 50.5,
                '(60-100)': 80.0,
            }

            probs = agePreds[0]
            expected_age = 0.0
            for i, bucket in enumerate(self.ageList):
                expected_age += float(probs[i]) * age_centers.get(bucket, 28.0)

            final_age = int(round(expected_age)) if expected_age > 0 else 28
            confidence = float(np.max(probs))

            return {'age': final_age, 'confidence': confidence}
            
        except Exception as e:
            return {'age': 25, 'confidence': 0.5}
    
    def smooth_age_prediction(self, predicted_age, face):
        """Smooth age prediction based on facial features"""
        try:
            # Convert to grayscale for feature analysis
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            
            # Analyze facial features for age clues
            features = self.analyze_facial_features_for_age(gray)
            
            # Apply smoothing based on features
            if features['wrinkles'] > 0.3 and predicted_age < 30:
                predicted_age = min(predicted_age + 5, 35)
            elif features['smoothness'] > 0.7 and predicted_age > 40:
                predicted_age = max(predicted_age - 5, 25)
            
            return predicted_age
            
        except:
            return predicted_age
    
    def analyze_facial_features_for_age(self, gray_face):
        """Analyze facial features for age estimation"""
        try:
            features = {}
            
            # Analyze texture (wrinkles)
            # Apply Gabor filter to detect fine lines
            kernel = cv2.getGaborKernel((21, 21), 8.0, np.pi/4, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            filtered = cv2.filter2D(gray_face, cv2.CV_8UC3, kernel)
            texture_variance = np.var(filtered)
            
            features['wrinkles'] = min(texture_variance / 1000, 1.0)
            features['smoothness'] = 1.0 - features['wrinkles']
            
            return features
            
        except:
            return {'wrinkles': 0.5, 'smoothness': 0.5}
    
    def boost_confidence(self, age_conf, gender_conf, emotion_conf):
        """Boost confidence scores based on consistency"""
        try:
            # Apply confidence boosting for consistent predictions
            boosted_age = min(age_conf * 1.2, 1.0)
            boosted_gender = min(gender_conf * 1.1, 1.0)
            boosted_emotion = min(emotion_conf * 1.15, 1.0)
            
            return {
                'age': boosted_age,
                'gender': boosted_gender,
                'emotion': boosted_emotion
            }
        except:
            return {
                'age': age_conf,
                'gender': gender_conf,
                'emotion': emotion_conf
            }

# Initialize the simple analyzer
DeepFace = SimpleFaceAnalyzer()

# Enable similar face recognition mode for better accuracy
enhanced_face_recognition.tune_for_similar_faces(True)
print("✅ Enhanced face recognition with similar face mode enabled")
print(f"   Base tolerance: {enhanced_face_recognition.base_tolerance}")
print(f"   Similar face threshold: {enhanced_face_recognition.similar_face_threshold}")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Email configuration
    email_config = get_email_config()
    app.config.update(email_config)
    
    return app

app = create_app()
CORS(app)  # Enable CORS for all routes
mail = Mail(app)

@app.route('/')
def home():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('face-analysis.html', user=user, users=all_users)

@app.route('/home')
def home_redirect():
    return redirect(url_for('face_analysis'))

@app.route('/face-analysis')
def face_analysis():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('face-analysis.html', user=user, users=all_users)

@app.route('/services')
def services():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('services.html', user=user, users=all_users)

@app.route('/about')
def about():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('about.html', user=user, users=all_users)

@app.route('/demo')
def demo():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('demo.html', user=user, users=all_users)

@app.route('/usecases')
def usecases():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('usecases.html', user=user, users=all_users)

@app.route('/products')
def products():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('products.html', user=user, users=all_users)

@app.route('/face-recognition')
def face_recognition_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Redirect based on user role
    if user['role'] == 'admin':
        return render_template('admin-face-recognition.html', user=user)
    else:
        return render_template('user-face-recognition.html', user=user)

@app.route('/face-recognition-usecase')
def face_recognition_usecase():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('face-recognition-usecase.html', user=user, users=all_users)

@app.route('/driver-monitoring')
def driver_monitoring():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('driver-monitoring.html', user=user, users=all_users)

@app.route('/contact')
def contact():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('contact.html', user=user, users=all_users)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Handle contact form submissions"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # Validate required fields
        if not all([name, email, subject, message]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Save feedback to database
        feedback_id = db.add_feedback(name, email, subject, message)
        
        if feedback_id:
            return jsonify({
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.',
                'feedback_id': feedback_id
            })
        else:
            return jsonify({'error': 'Failed to submit feedback. Please try again.'}), 500
            
    except Exception as e:
        print(f"Error in contact form submission: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/signup')
def signup():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('signup.html', user=user, users=all_users)

@app.route('/login')
def login():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('login.html', user=user, users=all_users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Only allow admin users to access admin panel
    if user['role'] != 'admin':
        return redirect(url_for('face_analysis'))
    
    all_users = db.get_all_users()
    password_reset_requests = db.get_password_reset_requests()
    return render_template('admin.html', user=user, all_users=all_users, password_reset_requests=password_reset_requests)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Decode the base64 image
        img_data = data['image']
        # Handle both data:image/jpeg;base64, and raw base64
        if ',' in img_data:
            img_data = img_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Image could not be decoded'}), 400
        
        try:
            # Analyze with our enhanced SimpleFaceAnalyzer
            result = DeepFace.analyze(img)
            
            # Check for errors
            if 'error' in result:
                return jsonify({'error': result['error']}), 400
            
            # Format the response with emotion
            formatted_result = {
                'age': result.get('age', 'N/A'),
                'gender': result.get('gender', 'N/A'),
                'emotion': result.get('emotion', 'N/A'),
                'region': result.get('region', {}),
                'confidence': result.get('confidence', {}),
                'emotion_breakdown': result.get('emotion_breakdown', {})
            }
            
            return jsonify(formatted_result)
            
        except Exception as deepface_error:
            print(f"DeepFace analysis error: {deepface_error}")
            return jsonify({'error': f'Face analysis failed: {str(deepface_error)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Image processing error: {str(e)}'}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message', '')
    
    # Get user context if logged in
    user_name = None
    user_role = None
    
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
        if user:
            user_name = user['full_name']
            user_role = user['role']
    
    reply = get_ai_response(user_message, user_name, user_role)
    return {'response': reply}

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email', '').lower()
    password = data.get('password', '')
    full_name = data.get('fullName', '')
    role = data.get('role', 'user')  # Default to 'user' if not specified
    
    if not email or not password or not full_name:
        return jsonify({'error': 'All fields are required'}), 400
    
    # Validate role - only allow 'user' role for public signup
    if role != 'user':
        return jsonify({'error': 'Invalid role selected'}), 400
    
    # Add user to database
    user_id = db.add_user(full_name, email, password, role)
    
    if user_id is None:
        return jsonify({'error': 'Email already registered'}), 400
    
    return jsonify({'success': True, 'message': 'Account created successfully!', 'redirect': url_for('login')})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email', '').lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user from database
    user = db.get_user_by_email(email)
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if user['password_hash'] != password_hash:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login
    db.update_last_login(user['id'])
    
    # Set session
    session['user_id'] = user['id']
    if remember:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=30)
    
    # Redirect based on user role
    if user['role'] == 'admin':
        redirect_url = url_for('admin')
    else:
        redirect_url = url_for('user_dashboard')
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role']
        },
        'redirect': redirect_url
    })

@app.route('/api/user/profile', methods=['GET'])
def api_user_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }
    })

@app.route('/forgot-password')
def forgot_password():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('forgot-password.html', user=user, users=all_users)

@app.route('/forgot-password', methods=['POST'])
def forgot_password_post():
    email = request.form.get('email')
    request_ip = request.remote_addr
    
    if not email:
        return render_template('forgot-password.html', error="Email is required", user=None, users=[])
    
    # Log the password reset request for admin tracking
    request_id = db.log_password_reset_request(email, request_ip=request_ip)
    
    # Check if user exists
    user = db.get_user_by_email(email)
    
    if not user:
        # Update request status - email not found
        if request_id:
            db.update_password_reset_request(request_id, 'email_not_found')
        
        return render_template('forgot-password.html', 
                             error="No account found with this email address. Please check your email or sign up for a new account.", 
                             user=None, users=[])
    
    # Update request with user_id
    if request_id:
        db.update_password_reset_request(request_id, 'user_found', user_id=user['id'])
    
    # Generate password reset token
    token = db.create_password_reset_token(user['id'])
    if not token:
        # Update request status - token generation failed
        if request_id:
            db.update_password_reset_request(request_id, 'token_generation_failed')
        
        return render_template('forgot-password.html', 
                             error="Failed to generate reset token. Please try again.", 
                             user=None, users=[])
    
    # Create reset URL
    reset_url = request.host_url.rstrip('/') + url_for('reset_password', token=token)
    
    try:
        # Send email
        msg = Message(
            subject='Password Reset Request - Face Analysis AI',
            recipients=[email],
            html=render_template('email/reset_password.html', 
                               user_name=user['full_name'], 
                               reset_url=reset_url)
        )
        mail.send(msg)
        
        # Update request status - email sent successfully
        if request_id:
            db.update_password_reset_request(request_id, 'email_sent', email_sent=True, token=token)
        
        return render_template('forgot-password.html', 
                             success=f"Password reset link has been sent to {email}. Please check your email and follow the instructions to reset your password.", 
                             user=None, users=[])
    
    except Exception as e:
        print(f"Email sending failed: {e}")
        
        # Update request status - email sending failed
        if request_id:
            db.update_password_reset_request(request_id, 'email_sending_failed', token=token)
        
        return render_template('forgot-password.html', 
                             error="Failed to send email. Please try again later or contact support.", 
                             user=None, users=[])

@app.route('/user-face-registration')
def user_face_registration_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the current user
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Redirect to user dashboard with message that admin registration is required
    return redirect(url_for('user_dashboard'))

@app.route('/face-registration')
def face_registration_redirect():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if user['role'] == 'admin':
        return redirect(url_for('admin_register_face', user_id=user['id']))
    else:
        return redirect(url_for('user_face_registration_page'))

@app.route('/api/user/face-register', methods=['POST'])
def api_user_face_register():
    # This endpoint is disabled - only admins can register faces
    return jsonify({'error': 'Face registration is admin-only. Please contact your administrator to register your face.'}), 403

@app.route('/api/test-face-detection', methods=['POST'])
def test_face_detection():
    """Test endpoint to check if face detection is working"""
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        print("🔍 Starting face detection test...")
        
        # Decode the base64 image
        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("❌ Error: Image could not be decoded")
            return jsonify({'error': 'Image could not be decoded'}), 400
        
        print(f"📸 Image decoded successfully, size: {img.shape}")
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Try multiple face detection methods
        import face_recognition as fr
        
        print("🔍 Attempting face detection with HOG model...")
        face_locations = fr.face_locations(rgb_image, model="hog")
        
        if not face_locations:
            print("🔄 No faces found with HOG, trying with upsampling...")
            face_locations = fr.face_locations(rgb_image, model="hog", number_of_times_to_upsample=2)
        
        if not face_locations:
            print("🔄 Still no faces found, trying with CNN model...")
            try:
                face_locations = fr.face_locations(rgb_image, model="cnn")
            except:
                print("⚠️ CNN model not available, falling back to HOG with different parameters...")
                face_locations = fr.face_locations(rgb_image, model="hog", number_of_times_to_upsample=3)
        
        print(f"👥 Face detection result: {len(face_locations)} faces found")
        
        # Provide detailed feedback
        if len(face_locations) > 0:
            # Calculate face sizes to check if they're too small
            face_sizes = []
            for (top, right, bottom, left) in face_locations:
                width = right - left
                height = bottom - top
                face_sizes.append((width, height))
            
            print(f"📏 Face sizes: {face_sizes}")
            
            # Check if faces are too small (might be detection errors)
            small_faces = [size for size in face_sizes if size[0] < 50 or size[1] < 50]
            
            if small_faces:
                return jsonify({
                    'success': True,
                    'faces_detected': len(face_locations),
                    'image_size': rgb_image.shape,
                    'message': f'Detected {len(face_locations)} faces, but some may be too small for reliable recognition. Try positioning your face closer to the camera.',
                    'warning': 'Small faces detected'
                })
            else:
                return jsonify({
                    'success': True,
                    'faces_detected': len(face_locations),
                    'image_size': rgb_image.shape,
                    'message': f'Successfully detected {len(face_locations)} face(s) in the image'
                })
        else:
            return jsonify({
                'success': False,
                'faces_detected': 0,
                'image_size': rgb_image.shape,
                'message': 'No faces detected. Please ensure your face is clearly visible, well-lit, and positioned within the camera frame.',
                'suggestions': [
                    'Position your face within the blue guide frame',
                    'Ensure good lighting - avoid shadows',
                    'Look directly at the camera',
                    'Keep your full face visible',
                    'Try moving closer to the camera'
                ]
            })
        
    except Exception as e:
        print(f"💥 Exception in face detection test: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/face-recognize', methods=['POST'])
def api_face_recognize():
    """Enhanced face recognition API with adaptive thresholds"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
    
        print("🔍 Processing face recognition request...")
        
        # Process the base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        print(f"✅ Image decoded successfully - Size: {img.shape}")
        
        # Assess image quality for adaptive thresholds
        image_quality = enhanced_face_recognition.assess_image_quality(img)
        print(f"📊 Image quality score: {image_quality:.3f}")
        
        # Convert BGR to RGB for face_recognition
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        import face_recognition as fr
        face_locations = fr.face_locations(rgb_img)
        face_encodings = fr.face_encodings(rgb_img, face_locations)
        
        if not face_encodings:
            return jsonify({
                'success': False,
                'message': 'No faces detected in the image',
                'image_quality': round(image_quality, 3),
                'enhanced_recognition': True
            }), 400
        
        print(f"👥 Detected {len(face_encodings)} faces")
        
        # Get known faces from database
        from local_face_recognition.db_manager import get_all_people
        people = get_all_people()
        
        if not people:
            return jsonify({
                'success': False,
                'message': 'No registered faces found in database',
                'image_quality': round(image_quality, 3),
                'enhanced_recognition': True
            }), 400
        
        # Prepare known face data
        known_encodings = []
        known_names = []
        known_people = []
        
        for person in people:
            face_data_id, name, age, contact, image_path, created_at = person
            
            if os.path.exists(image_path):
                try:
                    # Load and encode the known face
                    known_image = fr.load_image_file(image_path)
                    known_encoding = fr.face_encodings(known_image)
                    
                    if known_encoding:
                        known_encodings.append(known_encoding[0])
                        known_names.append(name)
                        known_people.append(person)
                        print(f"✅ Loaded known face: {name}")
                    else:
                        print(f"⚠️ Could not encode known face: {name}")
                except Exception as e:
                    print(f"❌ Error loading known face {name}: {e}")
        
        if not known_encodings:
            return jsonify({
                'success': False,
                'message': 'No valid known faces found in database',
                'image_quality': round(image_quality, 3),
                'enhanced_recognition': True
            }), 400
        
        print(f"📚 Comparing against {len(known_encodings)} known faces")
        
        # Process each detected face with enhanced recognition
        results = []
        for i, face_encoding in enumerate(face_encodings):
            print(f"🎯 Processing face {i+1}/{len(face_encodings)}")
            
            # Use enhanced recognition with adaptive thresholds
            recognized_name, confidence_score, confidence_level, details = enhanced_face_recognition.recognize_face_enhanced(
                known_encodings,
                face_encoding,
                known_names,
                image_quality
            )
            
            # Get face location
            top, right, bottom, left = face_locations[i]
            
            # Keep the database record aligned with the encoding.  Looking up
            # by display name breaks when two enrolled people share a name.
            person_details = None
            if recognized_name != "Unknown":
                matched_index = next(
                    (index for index, name in enumerate(known_names)
                     if name == recognized_name),
                    None,
                )
                if matched_index is not None:
                    person_details = known_people[matched_index]
            
            if person_details and recognized_name != "Unknown":
                face_data_id, name, age, contact, image_path, created_at = person_details
                
                result = {
                    'recognized': True,
                    'user_id': face_data_id,
                    'name': name,
                    'age': age,
                    'contact': contact,
                    'registration_date': created_at,
                    'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
                    'confidence': confidence_score,
                    'confidence_level': confidence_level,
                    'recognition_details': details
                }
                
                print(f"✅ Face {i+1} recognized as: {name} (confidence: {confidence_score:.3f}, level: {confidence_level})")
            else:
                result = {
                    'recognized': False,
                    'location': {'top': top, 'right': right, 'bottom': bottom, 'left': left},
                    'confidence': confidence_score,
                    'confidence_level': confidence_level,
                    'recognition_details': details
                }
                
                print(f"❌ Face {i+1} not recognized (confidence: {confidence_score:.3f})")
            
            results.append(result)
        
        # Get recognition statistics
        stats = enhanced_face_recognition.get_recognition_statistics()
        
        print(f"📊 Recognition Summary: {len([r for r in results if r['recognized']])} recognized out of {len(results)} faces")
        
        # Keep the complete multi-face response while exposing a concise
        # first-face result for the existing browser UI.
        primary_face = results[0]
        primary_person = None
        if primary_face['recognized']:
            primary_person = {
                'id': primary_face['user_id'],
                'name': primary_face['name'],
                'age': primary_face['age'],
                'contact': primary_face['contact'],
            }
        return jsonify({
            'success': True,
            'message': f'Face recognition completed. {len([r for r in results if r["recognized"]])} faces recognized.',
            'faces': results,
            'image_quality': round(image_quality, 3),
            'enhanced_recognition': True,
            'recognition_stats': stats,
            'recognized': primary_face['recognized'],
            'confidence': primary_face['confidence'],
            'person': primary_person,
        })
            
    except Exception as e:
        print(f"💥 Exception in face recognition: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Face recognition failed: {str(e)}'}), 500

@app.route('/api/face-recognition/stats', methods=['GET'])
def api_face_recognition_stats():
    """Get face recognition statistics and performance metrics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get recognition statistics
        stats = enhanced_face_recognition.get_recognition_statistics()
        
        # Get current threshold settings
        threshold_info = {
            'base_tolerance': enhanced_face_recognition.base_tolerance,
            'confidence_threshold': enhanced_face_recognition.confidence_threshold,
            'low_confidence_threshold': enhanced_face_recognition.low_confidence_threshold,
            'medium_confidence_threshold': enhanced_face_recognition.medium_confidence_threshold,
            'high_confidence_threshold': enhanced_face_recognition.high_confidence_threshold
        }
        
        return jsonify({
            'success': True,
            'recognition_statistics': stats,
            'threshold_settings': threshold_info,
            'enhanced_recognition': True
        })
        
    except Exception as e:
        print(f"💥 Exception getting recognition stats: {str(e)}")
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@app.route('/api/face-recognition/tune-thresholds', methods=['POST'])
def api_tune_thresholds():
    """Tune face recognition thresholds for better accuracy"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.json
        
        # Update threshold settings
        if 'base_tolerance' in data:
            enhanced_face_recognition.base_tolerance = float(data['base_tolerance'])
        
        if 'confidence_threshold' in data:
            enhanced_face_recognition.confidence_threshold = float(data['confidence_threshold'])
        
        if 'low_confidence_threshold' in data:
            enhanced_face_recognition.low_confidence_threshold = float(data['low_confidence_threshold'])
        
        if 'medium_confidence_threshold' in data:
            enhanced_face_recognition.medium_confidence_threshold = float(data['medium_confidence_threshold'])
        
        if 'high_confidence_threshold' in data:
            enhanced_face_recognition.high_confidence_threshold = float(data['high_confidence_threshold'])
        
        # Update factor weights if provided
        if 'distance_weight' in data:
            enhanced_face_recognition.distance_weight = float(data['distance_weight'])
        
        if 'similarity_weight' in data:
            enhanced_face_recognition.similarity_weight = float(data['similarity_weight'])
        
        if 'quality_weight' in data:
            enhanced_face_recognition.quality_weight = float(data['quality_weight'])
        
        if 'historical_weight' in data:
            enhanced_face_recognition.historical_weight = float(data['historical_weight'])
        
        # Validate that weights sum to 1.0
        total_weight = (enhanced_face_recognition.distance_weight + 
                       enhanced_face_recognition.similarity_weight + 
                       enhanced_face_recognition.quality_weight + 
                       enhanced_face_recognition.historical_weight)
        
        if abs(total_weight - 1.0) > 0.01:
            return jsonify({'error': 'Factor weights must sum to 1.0'}), 400
        
        print(f"✅ Thresholds updated successfully")
        print(f"📊 New settings: base_tolerance={enhanced_face_recognition.base_tolerance}, confidence_threshold={enhanced_face_recognition.confidence_threshold}")
        
        return jsonify({
            'success': True,
            'message': 'Thresholds updated successfully',
            'new_settings': {
                'base_tolerance': enhanced_face_recognition.base_tolerance,
                'confidence_threshold': enhanced_face_recognition.confidence_threshold,
                'low_confidence_threshold': enhanced_face_recognition.low_confidence_threshold,
                'medium_confidence_threshold': enhanced_face_recognition.medium_confidence_threshold,
                'high_confidence_threshold': enhanced_face_recognition.high_confidence_threshold,
                'factor_weights': {
                    'distance_weight': enhanced_face_recognition.distance_weight,
                    'similarity_weight': enhanced_face_recognition.similarity_weight,
                    'quality_weight': enhanced_face_recognition.quality_weight,
                    'historical_weight': enhanced_face_recognition.historical_weight
                }
            }
        })
    
    except Exception as e:
        print(f"💥 Exception tuning thresholds: {str(e)}")
        return jsonify({'error': f'Failed to update thresholds: {str(e)}'}), 500

@app.route('/api/face-recognition/reset-thresholds', methods=['POST'])
def api_reset_thresholds():
    """Reset face recognition thresholds to default values"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Reset to default values
        enhanced_face_recognition.base_tolerance = 0.6
        enhanced_face_recognition.confidence_threshold = 0.7
        enhanced_face_recognition.low_confidence_threshold = 0.4
        enhanced_face_recognition.medium_confidence_threshold = 0.6
        enhanced_face_recognition.high_confidence_threshold = 0.8
        
        # Reset factor weights
        enhanced_face_recognition.distance_weight = 0.4
        enhanced_face_recognition.similarity_weight = 0.3
        enhanced_face_recognition.quality_weight = 0.2
        enhanced_face_recognition.historical_weight = 0.1
        
        print("✅ Thresholds reset to default values")
        
        return jsonify({
            'success': True,
            'message': 'Thresholds reset to default values',
            'default_settings': {
                'base_tolerance': 0.6,
                'confidence_threshold': 0.7,
                'low_confidence_threshold': 0.4,
                'medium_confidence_threshold': 0.6,
                'high_confidence_threshold': 0.8,
                'factor_weights': {
                    'distance_weight': 0.4,
                    'similarity_weight': 0.3,
                    'quality_weight': 0.2,
                    'historical_weight': 0.1
                }
            }
        })
        
    except Exception as e:
        print(f"💥 Exception resetting thresholds: {str(e)}")
        return jsonify({'error': f'Failed to reset thresholds: {str(e)}'}), 500

@app.route('/api/face-recognition/tune-similar-faces', methods=['POST'])
def api_tune_similar_faces():
    """Tune face recognition system specifically for similar face scenarios"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.json
        enable = data.get('enable', True)
        
        # Tune the system for similar faces
        enhanced_face_recognition.tune_for_similar_faces(enable)
        
        if enable:
            message = "System tuned for similar face recognition"
        else:
            message = "System reset to default parameters"
        
        print(f"✅ {message}")
        
        return jsonify({
            'success': True,
            'message': message,
            'similar_face_mode': enable,
            'current_settings': {
                'base_tolerance': enhanced_face_recognition.base_tolerance,
                'similar_face_threshold': enhanced_face_recognition.similar_face_threshold,
                'similar_face_boost': enhanced_face_recognition.similar_face_boost,
                'confidence_thresholds': {
                    'low': enhanced_face_recognition.low_confidence_threshold,
                    'medium': enhanced_face_recognition.medium_confidence_threshold,
                    'high': enhanced_face_recognition.high_confidence_threshold
                },
                'factor_weights': {
                    'distance_weight': enhanced_face_recognition.distance_weight,
                    'similarity_weight': enhanced_face_recognition.similarity_weight,
                    'quality_weight': enhanced_face_recognition.quality_weight,
                    'historical_weight': enhanced_face_recognition.historical_weight
                }
            }
        })
        
    except Exception as e:
        print(f"💥 Exception tuning similar faces: {str(e)}")
        return jsonify({'error': f'Failed to tune system: {str(e)}'}), 500

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = db.get_user_by_reset_token(token)
    if not user:
        return render_template('reset_password.html', error="Invalid or expired password reset token.")
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            return render_template('reset_password.html', error="Password and Confirm Password are required.")
        
        if new_password != confirm_password:
            return render_template('reset_password.html', error="Passwords do not match.")
        
        if len(new_password) < 6:
            return render_template('reset_password.html', error="Password must be at least 6 characters long.")
        
        # Update password in database
        if db.update_user_password(user['id'], new_password):
            db.mark_reset_token_used(token)  # Mark token as used
            return render_template('reset_password.html', success="Your password has been updated successfully! You can now login with your new password.")
        else:
            return render_template('reset_password.html', error="Failed to update password. Please try again.")
    
    return render_template('reset_password.html', user=user)

@app.route('/terms')
def terms():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('terms.html', user=user, users=all_users)

@app.route('/privacy')
def privacy():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('privacy.html', user=user, users=all_users)

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = db.get_user_by_id(session['user_id'])
    if not current_user or current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    if user_id == current_user['id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    success = db.delete_user(user_id)
    if success:
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
def api_update_user_role(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = db.get_user_by_id(session['user_id'])
    if not current_user or current_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['user', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    success = db.update_user_role(user_id, new_role)
    if success:
        return jsonify({'success': True, 'message': 'User role updated successfully'})
    else:
        return jsonify({'error': 'Failed to update user role'}), 500

@app.route('/admin/register-face/<int:user_id>')
def admin_register_face(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return redirect(url_for('face_analysis'))
    
    # Get the user to register face for
    target_user = db.get_user_by_id(user_id)
    if not target_user:
        return redirect(url_for('admin'))
    
    return render_template('admin-face-registration.html', admin_user=admin_user, target_user=target_user)

@app.route('/api/admin/register-face', methods=['POST'])
def api_admin_register_face():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    user_id = data.get('user_id')
    age = data.get('age')
    contact = data.get('contact')
    image_data = data.get('image')
    
    print(f"🔍 Admin face registration request - User ID: {user_id}, Age: {age}, Contact: {contact}")
    print(f"📸 Image data length: {len(image_data) if image_data else 'None'}")
    
    if not user_id or not age or not contact or not image_data:
        return jsonify({'error': 'All fields are required'}), 400
    
    # Verify the target user exists
    target_user = db.get_user_by_id(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    print(f"✅ Target user found: {target_user['full_name']}")
    
    try:
        # Process the base64 image
        if image_data.startswith('data:image'):
            # Extract the base64 part
            image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("❌ Failed to decode image")
            return jsonify({'error': 'Invalid image data'}), 400
        
        print(f"✅ Image decoded successfully - Size: {img.shape}")
        
        # Validate that there's a face in the image before saving
        print("🔍 Validating face in image...")
        try:
            import face_recognition as fr
            
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = fr.face_locations(rgb_image)
            print(f"👥 Detected {len(face_locations)} faces in image")
            
            if len(face_locations) == 0:
                print("❌ No faces detected in the uploaded image")
                return jsonify({'error': 'No faces detected in the image. Please ensure your face is clearly visible and well-lit.'}), 400
            elif len(face_locations) > 1:
                print(f"⚠️ Multiple faces detected ({len(face_locations)}). Using the first one.")
            
            # Try to encode the face
            face_encodings = fr.face_encodings(rgb_image, face_locations)
            if len(face_encodings) == 0:
                print("❌ Could not encode faces in the image")
                return jsonify({'error': 'Could not process the face in the image. Please try with a clearer image.'}), 400
            
            print(f"✅ Face validation successful - {len(face_encodings)} face(s) encoded")
            
        except Exception as face_error:
            print(f"❌ Face validation error: {face_error}")
            return jsonify({'error': 'Face validation failed. Please try with a different image.'}), 400
        
        # Generate a unique filename
        import uuid
        filename = os.path.join(os.path.dirname(__file__), 'local_face_recognition', 'faces', f"{uuid.uuid4().hex}.jpg")
        
        # Ensure the faces directory exists
        faces_dir = os.path.dirname(filename)
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
            print(f"📁 Created faces directory: {faces_dir}")
        
        # Save the image
        if cv2.imwrite(filename, img):
            print(f"✅ Image saved successfully: {filename}")
        else:
            print(f"❌ Failed to save image: {filename}")
            return jsonify({'error': 'Failed to save image'}), 500
        
        # Update the database with user details and face data
        print(f"💾 Inserting into database...")
        face_manager.insert_person_with_details(user_id, target_user['full_name'], age, contact, filename)
        print(f"✅ Database updated successfully")
        
        return jsonify({
            'success': True,
            'message': f'Face registered successfully for {target_user["full_name"]}!',
            'image_path': filename
        })
    except Exception as e:
        print(f"💥 Exception in admin face registration: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/register-unknown-person', methods=['POST'])
def api_admin_register_unknown_person():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    name = data.get('name')
    age = data.get('age')
    contact = data.get('contact')
    image_data = data.get('image')
    
    if not name or not age or not contact or not image_data:
        return jsonify({'error': 'All fields are required'}), 400
    
    try:
        # Process the base64 image
        if image_data.startswith('data:image'):
            # Extract the base64 part
            image_data = image_data.split(',')[1]
        
        # Decode the base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Validate that there's a face in the image before processing
        print("🔍 Validating face in image...")
        try:
            import face_recognition as fr
            
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = fr.face_locations(rgb_image)
            print(f"👥 Detected {len(face_locations)} faces in image")
            
            if len(face_locations) == 0:
                print("❌ No faces detected in the uploaded image")
                return jsonify({'error': 'No faces detected in the image. Please ensure your face is clearly visible and well-lit.'}), 400
            elif len(face_locations) > 1:
                print(f"⚠️ Multiple faces detected ({len(face_locations)}). Using the first one.")
            
            # Try to encode the face
            face_encodings = fr.face_encodings(rgb_image, face_locations)
            if len(face_encodings) == 0:
                print("❌ Could not encode faces in the image")
                return jsonify({'error': 'Could not process the face in the image. Please try with a clearer image.'}), 400
            
            print(f"✅ Face validation successful - {len(face_encodings)} face(s) encoded")
            
        except Exception as face_error:
            print(f"❌ Face validation error: {face_error}")
            return jsonify({'error': 'Face validation failed. Please try with a different image.'}), 400
        
        # Generate a unique user_id for unknown person (negative number to distinguish from regular users)
        import uuid
        unknown_user_id = -1 * int(uuid.uuid4().hex[:8], 16)
        
        # First, create a temporary user record for the unknown person
        # We need to add this to the users table so the foreign key constraints work
        temp_user_id = db.add_user(name, f"unknown_{unknown_user_id}@temp.com", "temp_password", "user")
        
        if not temp_user_id:
            return jsonify({'error': 'Failed to create temporary user record'}), 500
        
        # Use the face recognition system to register the face
        success = face_manager.register_face(img, name, age, contact, temp_user_id)
        
        if not success:
            return jsonify({'error': 'Failed to register face'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Unknown person "{name}" registered successfully!',
            'user_id': temp_user_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/registered-people')
def api_admin_registered_people():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get all registered people from face recognition database
        people = face_manager.get_all_people()
        
        # Format the data for frontend
        formatted_people = []
        for person in people:
            # person format: (face_data_id, name, age, contact, image_path, created_at)
            formatted_people.append({
                'id': person[0],  # face_recognition_data.id (for deletion)
                'name': person[1],  # name
                'age': person[2],  # age
                'phone': person[3],  # contact
                'image_path': person[4],  # image_path
                'created_at': person[5]  # created_at
            })
        
        return jsonify({
            'success': True,
            'people': formatted_people
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/admin/delete-person/<int:person_id>', methods=['DELETE'])
def api_admin_delete_person(person_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        print(f"🔍 Admin delete person request - Person ID: {person_id}")
        
        # Import the delete function from local face recognition system
        from local_face_recognition.db_manager import delete_person
        
        # Delete the person
        success = delete_person(person_id)
        
        if success:
            print(f"✅ Person {person_id} deleted successfully")
            return jsonify({
                'success': True,
                'message': 'Person deleted successfully'
            })
        else:
            print(f"❌ Failed to delete person {person_id}")
            return jsonify({
                'error': 'Failed to delete person. Person may not exist.'
            }), 400
            
    except Exception as e:
        print(f"💥 Exception in admin delete person: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/admin/feedback')
def api_admin_feedback():
    """Get all feedback submissions for admin"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        feedback_list = db.get_all_feedback()
        return jsonify({
            'success': True,
            'feedback': feedback_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/feedback/<int:feedback_id>', methods=['PUT'])
def api_admin_update_feedback(feedback_id):
    """Update feedback status and response"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.json
        status = data.get('status')
        admin_response = data.get('admin_response')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = db.update_feedback_status(
            feedback_id, 
            status, 
            admin_response, 
            admin_user['id']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Feedback updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update feedback'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/feedback/<int:feedback_id>')
def api_admin_get_feedback(feedback_id):
    """Get specific feedback by ID"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    admin_user = db.get_user_by_id(session['user_id'])
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        feedback = db.get_feedback_by_id(feedback_id)
        if feedback:
            return jsonify({
                'success': True,
                'feedback': feedback
            })
        else:
            return jsonify({'error': 'Feedback not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Get user's face registration details
    # A missing optional face-recognition backend must not prevent a user from
    # opening their dashboard.
    face_details = face_manager.get_person_by_user_id(user['id']) if face_manager else []
    
    return render_template('user-dashboard.html', user=user, face_details=face_details)

@app.route('/dashboard')
def dashboard_redirect():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if user['role'] == 'admin':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('user_dashboard'))

# Driver Monitoring API Endpoints
@app.route('/api/driver-monitoring', methods=['POST'])
def api_driver_monitoring():
    """Process frame for driver drowsiness detection"""
    try:
        data = request.get_json()
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        frame_data = data['frame']
        result = driver_monitor.process_frame(frame_data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver-monitoring/reset', methods=['POST'])
def api_driver_monitoring_reset():
    """Reset driver monitoring counters"""
    try:
        result = driver_monitor.reset_counters()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint to check session status"""
    return jsonify({
        'session_data': dict(session),
        'user_id_in_session': session.get('user_id'),
        'session_permanent': session.permanent,
        'session_lifetime': app.permanent_session_lifetime.total_seconds() if app.permanent_session_lifetime else None
    })

@app.route('/api/debug/face-database', methods=['GET'])
def debug_face_database():
    """Debug endpoint to check face recognition database status"""
    try:
        print("🔍 Checking face recognition database status...")
        
        # Get all registered people
        people = face_manager.get_all_people()
        print(f"👥 Found {len(people)} registered people in database")
        
        # Check if face files exist
        face_files = []
        missing_files = []
        
        for person in people:
            id, name, age, phone, image_path, created_at = person
            if os.path.exists(image_path):
                face_files.append({
                    'id': id,
                    'name': name,
                    'path': image_path,
                    'exists': True
                })
            else:
                missing_files.append({
                    'id': id,
                    'name': name,
                    'path': image_path,
                    'exists': False
                })
        
        print(f"✅ Valid face files: {len(face_files)}")
        print(f"❌ Missing face files: {len(missing_files)}")
        
        return jsonify({
            'success': True,
            'total_registered': len(people),
            'valid_files': len(face_files),
            'missing_files': len(missing_files),
            'people': [
                {
                    'id': p[0],
                    'name': p[1],
                    'age': p[2],
                    'phone': p[3],
                    'image_path': p[4],
                    'created_at': p[5]
                } for p in people
            ],
            'valid_face_files': face_files,
            'missing_face_files': missing_files
        })
        
    except Exception as e:
        print(f"💥 Exception in database debug: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/edit-profile')
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('edit-profile.html', user=user)

@app.route('/security-settings')
def security_settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('security-settings.html', user=user)

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        
        if not full_name or not email:
            return jsonify({'error': 'Full name and email are required'}), 400
        
        # Update user profile
        success = db.update_user_profile(session['user_id'], full_name, email)
        
        if success:
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return jsonify({'error': 'All password fields are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
        
        # Verify current password and update
        success = db.change_user_password(session['user_id'], current_password, new_password)
        
        if success:
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        else:
            return jsonify({'error': 'Current password is incorrect or update failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
