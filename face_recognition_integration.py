import face_recognition
import cv2
import os
import sqlite3
import numpy as np
from datetime import datetime
from local_face_recognition.db_manager import insert_person_with_details as db_insert_person, get_all_people, get_user_face_data
from local_face_recognition.main import load_known_faces, recognize_face_in_image, get_annotated_image

class FaceRecognitionManager:
    def __init__(self):
        # The local_face_recognition system uses the main users.db, no need for separate init
        pass
    
    def insert_person_with_details(self, user_id, name, age, phone, image_path):
        """Insert a person with all details including user_id"""
        # Note: the underlying function only takes user_id, age, phone, image_path
        # The name parameter is not stored in the face recognition details table
        db_insert_person(user_id, age, phone, image_path)
    
    def get_all_people(self):
        """Get all registered people"""
        return get_all_people()
    
    def get_person_by_user_id(self, user_id):
        """Get person details by user_id"""
        return get_user_face_data(user_id)
    
    def load_known_faces(self):
        """Load all known faces from the database"""
        return load_known_faces()
    
    def recognize_faces_in_image(self, image):
        """Recognize faces in a given image"""
        return recognize_face_in_image(image)
    
    def get_annotated_image(self, image, recognition_results):
        """Add annotations to the image showing recognition results"""
        return get_annotated_image(image, recognition_results)
    
    def register_face(self, image, name, age, contact, user_id):
        """Register a new face with details"""
        try:
            import cv2
            import uuid
            import os
            
            # Generate a unique filename for the face image
            filename = os.path.join(
                os.path.dirname(__file__), 
                'local_face_recognition', 
                'faces', 
                f"{uuid.uuid4().hex}.jpg"
            )
            
            # Ensure the faces directory exists
            faces_dir = os.path.dirname(filename)
            if not os.path.exists(faces_dir):
                os.makedirs(faces_dir)
            
            # Save the image
            if cv2.imwrite(filename, image):
                # Store in database
                self.insert_person_with_details(user_id, name, age, contact, filename)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error registering face: {e}")
            return False

# Global instance
face_manager = FaceRecognitionManager()

# Initialize the database when module is imported
try:
    from local_face_recognition.db_manager import init_db
    init_db()
    print("✅ Face recognition database initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize face recognition database: {e}") 