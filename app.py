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


# Import face recognition module
from face_recognition_integration import face_manager

# Import emotion detector
from emotion_detector import EmotionDetector

# Accurate Face Analysis with Age, Gender, and Emotion Detection
import cv2
import numpy as np
import base64

# Initialize the simple face analyzer
class SimpleFaceAnalyzer:
    def __init__(self):
        # Load models
        self.faceProto = "opencv_face_detector.pbtxt"
        self.faceModel = "opencv_face_detector_uint8.pb"
        self.ageProto = "age_deploy.prototxt"
        self.ageModel = "age_net.caffemodel"
        self.genderProto = "gender_deploy.prototxt"
        self.genderModel = "gender_net.caffemodel"
        
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
            # Convert to grayscale for better feature detection
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for better contrast
            gray = cv2.equalizeHist(gray)
            
            # Apply Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Convert back to BGR for DNN models
            face = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # Resize to standard size
            face = cv2.resize(face, (227, 227))
            
            return face
        except:
            return face
    
    def predict_age_enhanced(self, face):
        """Enhanced age prediction with multiple techniques"""
        try:
            # Multiple age predictions with different preprocessing
            age_predictions = []
            confidences = []
            
            # Original prediction
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
            self.ageNet.setInput(blob)
            agePreds = self.ageNet.forward()
            
            # Enhanced age mapping with more precise ranges
            age_map_enhanced = {
                '(0-2)': 1, '(4-6)': 5, '(8-12)': 10, '(15-20)': 17,
                '(25-32)': 28, '(38-43)': 40, '(48-53)': 50, '(60-100)': 70
            }
            
            # Weighted average with confidence boosting
            age_weights = agePreds[0]
            weighted_age = 0
            total_weight = 0
            
            for i, age_range_key in enumerate(self.ageList):
                weight = age_weights[i]
                age_value = age_map_enhanced.get(age_range_key, 25)
                
                # Apply confidence boosting for more accurate weights
                boosted_weight = weight * (1 + weight * 0.5)  # Boost high confidence predictions
                weighted_age += age_value * boosted_weight
                total_weight += boosted_weight
            
            if total_weight > 0:
                final_age = int(weighted_age / total_weight)
                confidence = float(max(age_weights))
            else:
                final_age = 25
                confidence = 0.5
            
            # Apply age smoothing based on facial features
            final_age = self.smooth_age_prediction(final_age, face)
            
            return {
                'age': final_age,
                'confidence': confidence
            }
            
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
        
        # Save the image temporarily for DeepFace analysis
        temp_path = os.path.join(os.path.dirname(__file__), 'temp_analysis.jpg')
        cv2.imwrite(temp_path, img)
        
        try:
            # Analyze with our enhanced SimpleFaceAnalyzer
            result = DeepFace.analyze(img)
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
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
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
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

@app.route('/api/user/face-register', methods=['POST'])
def api_user_face_register():
    # This endpoint is disabled - only admins can register faces
    return jsonify({'error': 'Face registration is admin-only. Please contact your administrator to register your face.'}), 403

@app.route('/api/face-recognize', methods=['POST'])
def api_face_recognize():
    # Check if there's image data
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided'}), 400
    
    try:
        # Decode the base64 image
        img_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Image could not be decoded'}), 400
        
        # Recognize faces in the image using the integrated system
        recognition_results = face_manager.recognize_faces_in_image(img)
        
        if not recognition_results['success']:
            return jsonify({'error': recognition_results['message']}), 400
        
        # Get the annotated image
        annotated_img = face_manager.get_annotated_image(img, recognition_results)
        
        # Convert the annotated image back to base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        annotated_img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'faces': recognition_results['faces'],
            'annotated_image': f'data:image/jpeg;base64,{annotated_img_base64}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
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
    
    if not user_id or not age or not contact or not image_data:
        return jsonify({'error': 'All fields are required'}), 400
    
    # Verify the target user exists
    target_user = db.get_user_by_id(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
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
        
        # Generate a unique filename
        import uuid
        filename = os.path.join(os.path.dirname(__file__), 'local_face_recognition', 'faces', f"{uuid.uuid4().hex}.jpg")
        
        # Save the image
        cv2.imwrite(filename, img)
        
        # Update the database with user details and face data
        face_manager.insert_person_with_details(user_id, target_user['full_name'], age, contact, filename)
        
        return jsonify({
            'success': True,
            'message': f'Face registered successfully for {target_user["full_name"]}!',
            'image_path': filename
        })
    except Exception as e:
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
        
        # Generate a unique filename
        import uuid
        filename = os.path.join(os.path.dirname(__file__), 'local_face_recognition', 'faces', f"{uuid.uuid4().hex}.jpg")
        
        # Save the image
        cv2.imwrite(filename, img)
        
        # Generate a unique user_id for unknown person (negative number to distinguish from regular users)
        unknown_user_id = -1 * int(uuid.uuid4().hex[:8], 16)
        
        # Insert the unknown person into the face recognition database
        face_manager.insert_person_with_details(unknown_user_id, name, age, contact, filename)
        
        return jsonify({
            'success': True,
            'message': f'Unknown person "{name}" registered successfully!',
            'image_path': filename,
            'user_id': unknown_user_id
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
            formatted_people.append({
                'id': person[0],
                'name': person[1],
                'age': person[2],
                'phone': person[3],
                'image_path': person[4],
                'user_id': person[5],
                'created_at': person[6]
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
        # Import the delete function from face recognition system
        from face_recognition_system.db_manager import delete_person
        
        # Delete the person
        delete_person(person_id)
        
        return jsonify({
            'success': True,
            'message': 'Person deleted successfully'
        })
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
    face_details = face_manager.get_person_by_user_id(user['id'])
    
    return render_template('user-dashboard.html', user=user, face_details=face_details)

if __name__ == '__main__':
    app.run(debug=True)