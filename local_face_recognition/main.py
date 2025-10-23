import face_recognition
import cv2
import os
import numpy as np
from .db_manager import get_all_people, init_db

# Initialize the database
init_db()

def load_known_faces():
    known_face_encodings = []
    known_face_details = []

    people = get_all_people()
    print(f"Loading {len(people)} registered faces...")
    
    for person in people:
        user_id, name, age, contact, image_path, created_at = person
        print(f"\nProcessing: {name}")
        print(f"  Image path: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"  ❌ ERROR: Image file not found!")
            continue
            
        try:
            # Load image with OpenCV first to check if it's valid
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                print(f"  ❌ ERROR: OpenCV cannot load the image file!")
                continue
            
            print(f"  ✓ Image file loaded successfully (size: {cv_image.shape})")
            
            # Load with face_recognition library
            image = face_recognition.load_image_file(image_path)
            print(f"  ✓ Face recognition library loaded image")
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            print(f"  ✓ Face detection completed - found {len(face_locations)} faces")
            
            if not face_locations:
                print(f"  ❌ ERROR: No faces detected in the image!")
                print(f"  💡 Tip: Make sure the image contains a clear, well-lit face")
                continue
            
            # Encode faces
            encodings = face_recognition.face_encodings(image, face_locations)
            print(f"  ✓ Face encoding completed - encoded {len(encodings)} faces")
            
            if encodings:
                known_face_encodings.append(encodings[0])
                # Store all user details including user_id and registration date
                known_face_details.append((user_id, name, age, contact, created_at))
                print(f"  ✅ Successfully loaded face for: {name}")
            else:
                print(f"  ❌ ERROR: Could not encode any faces!")
                
        except Exception as e:
            print(f"  ❌ ERROR loading image for {name}: {e}")
            print(f"  💡 This might be due to:")
            print(f"     - Corrupted image file")
            print(f"     - Unsupported image format")
            print(f"     - Insufficient memory")

    print(f"\n📊 Summary:")
    print(f"  Total people in database: {len(people)}")
    print(f"  Successfully loaded faces: {len(known_face_encodings)}")
    print(f"  Failed to load: {len(people) - len(known_face_encodings)}")
    
    if len(known_face_encodings) == 0:
        print(f"\n⚠️  No valid faces loaded!")
        print(f"💡 Solutions:")
        print(f"   1. Run 'python cleanup_database.py' to fix database issues")
        print(f"   2. Re-register people with better quality images")
        print(f"   3. Ensure images contain clear, well-lit faces")
    
    return known_face_encodings, known_face_details

def recognize_face_in_image(image):
    """Recognize faces in a single image and return the results"""
    known_encodings, known_details = load_known_faces()
    
    if not known_encodings:
        return {
            'success': False,
            'message': "No registered faces found. Please register some faces first."
        }
    
    # Convert image to RGB (face_recognition uses RGB)
    if image is None:
        return {
            'success': False,
            'message': "Invalid image provided."
        }
        
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    face_locations = face_recognition.face_locations(rgb_image)
    
    if not face_locations:
        return {
            'success': False,
            'message': "No faces detected in the image."
        }
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    results = []
    
    for face_encoding, face_location in zip(face_encodings, face_locations):
        # Compare with known faces
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        user_id, name, age, contact, registration_date = None, "Unknown", "", "", ""
        
        if True in matches:
            index = matches.index(True)
            user_id, name, age, contact, registration_date = known_details[index]
        
        # Get face location
        top, right, bottom, left = face_location
        
        results.append({
            'user_id': user_id,
            'name': name,
            'age': age,
            'contact': contact,
            'registration_date': registration_date,
            'location': {
                'top': top,
                'right': right,
                'bottom': bottom,
                'left': left
            },
            'recognized': user_id is not None
        })
    
    return {
        'success': True,
        'faces': results
    }

def get_annotated_image(image, recognition_results):
    """Draw face boxes and names on the image"""
    if not recognition_results['success']:
        return image
    
    # Create a copy of the image
    annotated_image = image.copy()
    
    for face in recognition_results['faces']:
        # Get face location
        top = face['location']['top']
        right = face['location']['right']
        bottom = face['location']['bottom']
        left = face['location']['left']
        
        # Set color based on recognition status
        color = (0, 255, 0) if face['recognized'] else (0, 0, 255)  # Green for known, Red for unknown
        
        # Draw rectangle around face
        cv2.rectangle(annotated_image, (left, top), (right, bottom), color, 2)
        
        # Prepare text for display
        info_text = face['name']
        
        # Calculate text position and size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Get text size for proper positioning
        (text_width, text_height), baseline = cv2.getTextSize(info_text, font, font_scale, thickness)
        
        # Position text above the face rectangle
        text_x = left
        text_y = top - 10 if top - 10 > text_height else top + text_height + 10
        
        # Draw background rectangle for text
        cv2.rectangle(annotated_image, (text_x - 5, text_y - text_height - 5), 
                     (text_x + text_width + 5, text_y + baseline + 5), (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(annotated_image, info_text, (text_x, text_y), font, font_scale, color, thickness)
    
    return annotated_image
