import face_recognition
import cv2
import os
import sqlite3
import numpy as np
from datetime import datetime
from face_recognition_system.db_manager import init_db, insert_person, get_all_people, get_person_by_user_id
from face_recognition_system.face_recognition_core import load_known_faces, recognize_faces_in_image, get_annotated_image

class FaceRecognitionManager:
    def __init__(self):
        # Initialize the database
        init_db()
    
    def insert_person_with_details(self, user_id, name, age, phone, image_path):
        """Insert a person with all details including user_id"""
        insert_person(name, age, phone, image_path, user_id)
    
    def get_all_people(self):
        """Get all registered people"""
        return get_all_people()
    
    def get_person_by_user_id(self, user_id):
        """Get person details by user_id"""
        return get_person_by_user_id(user_id)
    
    def load_known_faces(self):
        """Load all known faces from the database"""
        return load_known_faces()
    
    def recognize_faces_in_image(self, image):
        """Recognize faces in a given image"""
        return recognize_faces_in_image(image)
    
    def get_annotated_image(self, image, recognition_results):
        """Add annotations to the image showing recognition results"""
        return get_annotated_image(image, recognition_results)

# Global instance
face_manager = FaceRecognitionManager()

# Initialize the database when module is imported
try:
    init_db()
    print("✅ Face recognition database initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize face recognition database: {e}") 