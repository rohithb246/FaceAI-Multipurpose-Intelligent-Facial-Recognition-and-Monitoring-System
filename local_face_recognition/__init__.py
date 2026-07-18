# Face Recognition Module

from .main import load_known_faces, recognize_face_in_image, get_annotated_image
from .capture_face import capture_and_register, capture_face_for_recognition
from .db_manager import init_db, insert_person, get_all_people, get_user_face_data, delete_face_data

__all__ = [
    'load_known_faces',
    'recognize_face_in_image',
    'get_annotated_image',
    'capture_and_register',
    'capture_face_for_recognition',
    'init_db',
    'insert_person',
    'get_all_people',
    'get_user_face_data',
    'delete_face_data'
]