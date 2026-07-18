import cv2
import numpy as np
import time
from collections import deque
import dlib
import math

class DriverMonitoringSystem:
    def __init__(self):
        # Initialize face detector and facial landmark predictor
        self.face_detector = dlib.get_frontal_face_detector()
        
        # Try to load the facial landmark predictor
        try:
            self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            print("✅ Facial landmark predictor loaded successfully")
        except:
            print("⚠️  Facial landmark predictor not found. Downloading...")
            import urllib.request
            url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            urllib.request.urlretrieve(url, "shape_predictor_68_face_landmarks.dat.bz2")
            import bz2
            with bz2.open("shape_predictor_68_face_landmarks.dat.bz2") as fr, open("shape_predictor_68_face_landmarks.dat", "wb") as fw:
                fw.write(fr.read())
            self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            print("✅ Facial landmark predictor downloaded and loaded successfully")
        
        # Eye aspect ratio threshold for drowsiness detection
        self.EAR_THRESHOLD = 0.25
        self.EAR_CONSEC_FRAMES = 3
        
        # Blink counter and drowsiness detection
        self.counter = 0
        self.total_blinks = 0
        self.ear_history = deque(maxlen=30)  # Store last 30 frames of EAR values
        
        # Drowsiness detection parameters
        self.drowsy_counter = 0
        self.DROWSY_THRESHOLD = 10  # Frames with closed eyes to trigger drowsiness
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
        ear = (A + B) / (2.0 * C)
        return ear
    
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
        
        for face in faces:
            # Get facial landmarks
            shape = self.landmark_predictor(gray, face)
            
            # Extract eye landmarks
            left_eye, right_eye = self.get_eye_landmarks(shape)
            
            # Calculate EAR for both eyes
            ear_left = self.eye_aspect_ratio(left_eye)
            ear_right = self.eye_aspect_ratio(right_eye)
            
            # Average EAR
            ear = (ear_left + ear_right) / 2.0
            
            # Add to history
            self.ear_history.append(ear)
            
            # Draw eye contours
            cv2.drawContours(frame, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)
            
            # Check if eyes are closed
            if ear < self.EAR_THRESHOLD:
                self.counter += 1
                if self.counter >= self.EAR_CONSEC_FRAMES:
                    self.total_blinks += 1
                    self.counter = 0
            else:
                self.counter = 0
            
            # Drowsiness detection based on sustained eye closure
            if ear < self.EAR_THRESHOLD:
                self.drowsy_counter += 1
            else:
                self.drowsy_counter = max(0, self.drowsy_counter - 1)
            
            # Check for drowsiness
            if self.drowsy_counter >= self.DROWSY_THRESHOLD:
                drowsiness_detected = True
                if not self.is_drowsy:
                    self.is_drowsy = True
                    self.alert_start_time = time.time()
            
            # Draw face rectangle
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            color = (0, 0, 255) if drowsiness_detected else (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Display metrics
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Blinks: {self.total_blinks}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Drowsy Counter: {self.drowsy_counter}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if drowsiness_detected:
                cv2.putText(frame, "DROWSINESS DETECTED!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Calculate FPS
        self.fps_counter += 1
        if time.time() - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = time.time()
        
        cv2.putText(frame, f"FPS: {self.current_fps}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame, drowsiness_detected, ear_left, ear_right
    
    def create_alert_overlay(self, frame):
        """Create red screen overlay for drowsiness alert"""
        if self.is_drowsy and self.alert_start_time:
            elapsed_time = time.time() - self.alert_start_time
            if elapsed_time < self.ALERT_DURATION:
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
                
                # Add countdown
                countdown = int(self.ALERT_DURATION - elapsed_time)
                countdown_text = f"Alert: {countdown}s"
                cv2.putText(frame, countdown_text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                # Reset alert state
                self.is_drowsy = False
                self.alert_start_time = None
        
        return frame
    
    def run_monitoring(self):
        """Run the driver monitoring system"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("🚗 Driver Monitoring System Started")
        print("📋 Controls:")
        print("   - Press 'q' to quit")
        print("   - Press 'r' to reset counters")
        print("   - Press 's' to save screenshot")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Could not read frame")
                break
            
            # Detect drowsiness
            frame, drowsiness_detected, ear_left, ear_right = self.detect_drowsiness(frame)
            
            # Add alert overlay if drowsy
            frame = self.create_alert_overlay(frame)
            
            # Display the frame
            cv2.imshow('Driver Monitoring System', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.total_blinks = 0
                self.drowsy_counter = 0
                self.is_drowsy = False
                self.alert_start_time = None
                print("🔄 Counters reset")
            elif key == ord('s'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"driver_monitoring_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Screenshot saved: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print("🛑 Driver Monitoring System Stopped")

def main():
    """Main function to run the driver monitoring system"""
    try:
        monitoring_system = DriverMonitoringSystem()
        monitoring_system.run_monitoring()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have a webcam connected and dlib is properly installed")

if __name__ == "__main__":
    main() 