import cv2
import os
import face_recognition
import uuid
from datetime import datetime
from .db_manager import insert_person

# Ensure faces directory exists
FACES_DIR = os.path.join(os.path.dirname(__file__), 'faces')
os.makedirs(FACES_DIR, exist_ok=True)

def capture_and_register(user_id):
    """Capture a face image for a user and register it in the database"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return {
            'success': False,
            'message': "Error: Could not open camera!"
        }
    
    face_detected = False

    # Capture frames for 3 seconds to allow camera to adjust
    for i in range(30):  # Assuming 10 FPS
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return {
                'success': False,
                'message': "Error: Could not read frame from camera!"
            }
    
    # Capture the actual frame for processing
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return {
            'success': False,
            'message': "Error: Could not read frame from camera!"
        }
        
    # Convert to RGB for face detection
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if not face_locations:
        cap.release()
        return {
            'success': False,
            'message': "No face detected in the image. Please try again with better lighting."
        }
    
    # Generate a unique filename
    filename = os.path.join(FACES_DIR, f"{uuid.uuid4().hex}.jpg")
    
    # Save the image
    cv2.imwrite(filename, frame)
    
    # Register in database
    insert_person(user_id, filename)
    
    cap.release()
    
    return {
        'success': True,
        'message': "Face registered successfully!",
        'image_path': filename
    }

def capture_face_for_recognition():
    """Capture a face image for recognition purposes"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return None
    
    # Capture frames for 2 seconds to allow camera to adjust
    for i in range(20):  # Assuming 10 FPS
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return None
    
    # Capture the actual frame for processing
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None
        
    return frame
