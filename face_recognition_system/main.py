import face_recognition
import cv2
import os
from db_manager import get_all_people

def load_known_faces():
    known_face_encodings = []
    known_face_details = []

    people = get_all_people()
    print(f"Loading {len(people)} registered faces...")
    
    for person in people:
        id, name, age, phone, image_path = person
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
                known_face_details.append((name, age, phone))
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

def recognize_faces():
    known_encodings, known_details = load_known_faces()
    
    if not known_encodings:
        print("\n❌ No registered faces found. Please register some faces first.")
        print("💡 You can:")
        print("   1. Use the GUI to register new people")
        print("   2. Run 'python cleanup_database.py' to fix existing entries")
        return
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera!")
        return

    print(f"\n🎥 Starting face recognition with {len(known_encodings)} registered faces...")
    print("Press 'q' to quit.")
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Could not read frame from camera!")
            break
            
        # Resize frame for faster processing
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
            name, age, phone = "Unknown", "", ""
            color = (0, 0, 255)  # Red for unknown

            if True in matches:
                index = matches.index(True)
                name, age, phone = known_details[index]
                color = (0, 255, 0)  # Green for known

            # Scale back to original size
            top, right, bottom, left = [v * 4 for v in face_location]
            
            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Prepare text for display
            info_text = f"{name}"
            if age:
                info_text += f", Age: {age}"
            if phone:
                info_text += f", Phone: {phone}"
            
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
            cv2.rectangle(frame, (text_x - 5, text_y - text_height - 5), 
                         (text_x + text_width + 5, text_y + baseline + 5), (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(frame, info_text, (text_x, text_y), font, font_scale, color, thickness)

        # Display frame
        cv2.imshow("Face Recognition System", frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
