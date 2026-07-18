import cv2
import os
import face_recognition
import uuid
from db_manager import insert_person

def capture_and_register(name, age, phone, user_id=None):
    """Capture and register a face with details"""
    # Ensure faces directory exists
    faces_dir = os.path.join(os.path.dirname(__file__), 'faces')
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera!")
        return None
    
    print("Position face in front of camera. Press 's' to capture when face is detected.")
    face_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from camera!")
            break
            
        # Convert to RGB for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # Draw rectangle around detected face
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            face_detected = True
        
        # Display status
        if face_detected:
            status_text = "Face Detected - Press 's' to capture"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            status_text = "No face detected - Please position face in camera"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("Register Face", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and face_detected:
            filename = os.path.join(faces_dir, f"{uuid.uuid4().hex}.jpg")
            cv2.imwrite(filename, frame)
            insert_person(name, age, phone, filename, user_id)
            print(f"Face and details registered successfully!")
            print(f"Image saved as: {filename}")
            cap.release()
            cv2.destroyAllWindows()
            return filename
        elif key == ord('q'):
            print("Registration cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

def capture_face_for_recognition():
    """Capture face for recognition testing"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera!")
        return None
    
    print("Position face in front of camera. Press 's' to capture.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from camera!")
            break
        
        cv2.imshow("Capture Face", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cap.release()
            cv2.destroyAllWindows()
            return frame
        elif key == ord('q'):
            print("Capture cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return None
