import cv2
import numpy as np
import time
import base64
import json
from collections import deque
import dlib
import os

class WebDriverMonitoring:
    def __init__(self):
        # Initialize face detector and facial landmark predictor
        self.face_detector = dlib.get_frontal_face_detector()
        
        # Get the current directory for model loading
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try to load the facial landmark predictor
        model_path = os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat")
        try:
            self.landmark_predictor = dlib.shape_predictor(model_path)
            print("✅ Facial landmark predictor loaded successfully")
        except:
            print("⚠️  Facial landmark predictor not found. Downloading...")
            import urllib.request
            url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            urllib.request.urlretrieve(url, os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat.bz2"))
            import bz2
            with bz2.open(os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat.bz2")) as fr, open(model_path, "wb") as fw:
                fw.write(fr.read())
            self.landmark_predictor = dlib.shape_predictor(model_path)
            print("✅ Facial landmark predictor downloaded and loaded successfully")
        
        # Eye aspect ratio threshold for drowsiness detection
        self.EAR_THRESHOLD = 0.25
        self.EAR_CONSEC_FRAMES = 2
        
        # Blink counter and drowsiness detection
        self.counter = 0
        self.total_blinks = 0
        self.ear_history = deque(maxlen=30)  # Store last 30 frames of EAR values
        self.eyes_closed = False
        self.closed_frames = 0
        
        # Drowsiness detection parameters
        self.drowsy_counter = 0
        # The browser sends roughly 10 frames per second.  Six consecutive
        # closed-eye frames gives a prompt alert without treating a normal
        # blink as drowsiness.
        self.DROWSY_THRESHOLD = 6
        self.no_face_frames = 0
        self.ALERT_DURATION = 3  # Seconds to show red screen
        
        # Alert state
        self.is_drowsy = False
        self.alert_start_time = None
        
        # Performance metrics
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def eye_aspect_ratio(self, eye):
        """Calculate the Eye Aspect Ratio (EAR)"""
        # Compute the euclidean distances between the vertical eye landmarks
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        
        # Compute the euclidean distance between the horizontal eye landmarks
        C = np.linalg.norm(eye[0] - eye[3])
        
        # Compute the eye aspect ratio
        if C == 0:
            return 0.0
        return (A + B) / (2.0 * C)
    
    def get_eye_landmarks(self, shape):
        """Extract eye landmarks from facial landmarks"""
        # Left eye landmarks (indices 36-41)
        left_eye = np.array([(shape.part(36).x, shape.part(36).y),
                           (shape.part(37).x, shape.part(37).y),
                           (shape.part(38).x, shape.part(38).y),
                           (shape.part(39).x, shape.part(39).y),
                           (shape.part(40).x, shape.part(40).y),
                           (shape.part(41).x, shape.part(41).y)])
        
        # Right eye landmarks (indices 42-47)
        right_eye = np.array([(shape.part(42).x, shape.part(42).y),
                            (shape.part(43).x, shape.part(43).y),
                            (shape.part(44).x, shape.part(44).y),
                            (shape.part(45).x, shape.part(45).y),
                            (shape.part(46).x, shape.part(46).y),
                            (shape.part(47).x, shape.part(47).y)])
        
        return left_eye, right_eye
    
    def detect_drowsiness(self, frame):
        """Main drowsiness detection function"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_detector(gray)
        
        drowsiness_detected = False
        ear_left = 0
        ear_right = 0
        ear_avg = 0
        
        # The UI is designed for one driver.  Analysing only the largest face
        # prevents two passengers from corrupting the driver's counters.
        if faces:
            self.no_face_frames = 0
            face = max(faces, key=lambda item: item.width() * item.height())
            # Get facial landmarks
            shape = self.landmark_predictor(gray, face)
            
            # Extract eye landmarks
            left_eye, right_eye = self.get_eye_landmarks(shape)
            
            # Calculate EAR for both eyes
            ear_left = self.eye_aspect_ratio(left_eye)
            ear_right = self.eye_aspect_ratio(right_eye)
            
            # Average EAR
            ear_avg = (ear_left + ear_right) / 2.0
            
            # Add to history
            self.ear_history.append(ear_avg)
            
            # Draw eye contours
            cv2.drawContours(frame, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)
            
            # Count a blink when eyes re-open after a short closure.  The
            # previous implementation counted one blink every few closed-eye
            # frames, which made the counter inaccurate and delayed alerts.
            eyes_closed_now = ear_avg < self.EAR_THRESHOLD
            if eyes_closed_now:
                self.eyes_closed = True
                self.closed_frames += 1
                self.counter = self.closed_frames
            else:
                if self.eyes_closed and self.EAR_CONSEC_FRAMES <= self.closed_frames < self.DROWSY_THRESHOLD:
                    self.total_blinks += 1
                self.eyes_closed = False
                self.closed_frames = 0
                self.counter = 0

            # Drowsiness is a sustained eye closure, not a single blink.
            self.drowsy_counter = self.closed_frames
            
            # Check for drowsiness
            if self.drowsy_counter >= self.DROWSY_THRESHOLD:
                drowsiness_detected = True
                if not self.is_drowsy:
                    self.is_drowsy = True
                    self.alert_start_time = time.time()
            elif not eyes_closed_now:
                self.is_drowsy = False
                self.alert_start_time = None
            
            # Draw face rectangle
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            color = (0, 0, 255) if drowsiness_detected else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Display metrics
            cv2.putText(frame, f"EAR: {ear_avg:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Blinks: {self.total_blinks}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Drowsy Counter: {self.drowsy_counter}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if drowsiness_detected:
                cv2.putText(frame, "DROWSINESS DETECTED!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # Do not keep a stale closed-eye state when the face detector
            # loses the driver (for example, after the camera is covered).
            self.no_face_frames += 1
            self.counter = 0
            self.drowsy_counter = 0
            self.closed_frames = 0
            self.eyes_closed = False
            if self.no_face_frames >= 3:
                self.is_drowsy = False
                self.alert_start_time = None
        
        # Calculate FPS
        self.fps_counter += 1
        if time.time() - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = time.time()
        
        cv2.putText(frame, f"FPS: {self.current_fps}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame, drowsiness_detected, ear_left, ear_right, ear_avg
    
    def create_alert_overlay(self, frame):
        """Create red screen overlay for drowsiness alert"""
        if self.is_drowsy and self.alert_start_time:
            elapsed_time = time.time() - self.alert_start_time
            if self.is_drowsy:
                # Create red overlay
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
                
                # Add transparency
                alpha = 0.3
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
                
                # Add warning text
                text = "DROWSINESS ALERT!"
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2
                
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                
                # The alert remains visible while the eyes stay closed.
                countdown_text = f"Eyes closed: {int(elapsed_time)}s"
                cv2.putText(frame, countdown_text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def process_frame(self, frame_data):
        """Process a frame from web interface and return results"""
        try:
            # Decode base64 image
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]
            
            # Decode base64 to numpy array
            img_data = base64.b64decode(frame_data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {
                    'success': False,
                    'error': 'Failed to decode image'
                }
            
            # Detect drowsiness
            frame, drowsiness_detected, ear_left, ear_right, ear_avg = self.detect_drowsiness(frame)
            
            # Add alert overlay if drowsy
            frame = self.create_alert_overlay(frame)
            
            # Convert frame back to base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare response
            response = {
                'success': True,
                'drowsiness_detected': drowsiness_detected,
                'ear_left': float(ear_left),
                'ear_right': float(ear_right),
                'ear_average': float(ear_avg),
                'total_blinks': self.total_blinks,
                'drowsy_counter': self.drowsy_counter,
                'fps': self.current_fps,
                'is_alert_active': self.is_drowsy,
                'processed_image': f'data:image/jpeg;base64,{img_base64}'
            }
            
            # Add alert info if drowsy
            if self.is_drowsy and self.alert_start_time:
                response['alert_countdown'] = int(time.time() - self.alert_start_time)
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def reset_counters(self):
        """Reset all counters and alert state"""
        self.total_blinks = 0
        self.drowsy_counter = 0
        self.is_drowsy = False
        self.alert_start_time = None
        self.counter = 0
        self.closed_frames = 0
        self.eyes_closed = False
        self.no_face_frames = 0
        return {'success': True, 'message': 'Counters reset successfully'}

# Global instance for web interface
driver_monitor = WebDriverMonitoring() 
