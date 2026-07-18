import face_recognition as fr
import cv2
import os
import numpy as np
from .db_manager import get_all_people

# Import the enhanced face recognition system
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enhanced_face_recognition import enhanced_face_recognition

def load_known_faces():
    """Load all known faces from the database"""
    known_face_encodings = []
    known_face_details = []

    people = get_all_people()
    print(f"Loading {len(people)} registered faces...")
    
    for person in people:
        id, name, age, phone, image_path, user_id, created_at = person
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
            image = fr.load_image_file(image_path)
            print(f"  ✓ Face recognition library loaded image")
            
            # Detect faces
            face_locations = fr.face_locations(image)
            print(f"  ✓ Face detection completed - found {len(face_locations)} faces")
            
            if not face_locations:
                print(f"  ❌ ERROR: No faces detected in the image!")
                continue
            
            # Encode faces
            encodings = fr.face_encodings(image, face_locations)
            print(f"  ✓ Face encoding completed - encoded {len(encodings)} faces")
            
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_details.append((user_id, name, age, phone, created_at))
                print(f"  ✅ Successfully loaded face for: {name}")
            else:
                print(f"  ❌ ERROR: Could not encode any faces!")
                
        except Exception as e:
            print(f"  ❌ ERROR loading image for {name}: {e}")

    print(f"\n📊 Summary:")
    print(f"  Total people in database: {len(people)}")
    print(f"  Successfully loaded faces: {len(known_face_encodings)}")
    
    return known_face_encodings, known_face_details

def recognize_faces_in_image(image_path, known_faces_dir="local_face_recognition/faces"):
    """
    Enhanced face recognition with adaptive thresholds and confidence scoring
    """
    try:
        # Load known faces with enhanced system
        known_face_encodings, known_face_details = load_known_faces()
        
        if not known_face_encodings:
            return {"error": "No known faces found in database"}
        
        # Extract names from known_face_details
        known_face_names = [details[1] for details in known_face_details]  # name is at index 1
        
        # Load and process the image
        image = fr.load_image_file(image_path)
        face_locations = fr.face_locations(image)
        face_encodings = fr.face_encodings(image, face_locations)
        
        if not face_encodings:
            return {"error": "No faces detected in the image"}
        
        # Assess image quality for adaptive thresholds
        image_quality = enhanced_face_recognition.assess_image_quality(image)
        
        results = []
        for i, face_encoding in enumerate(face_encodings):
            # Use enhanced recognition with adaptive thresholds
            recognized_name, confidence_score, confidence_level, details = enhanced_face_recognition.recognize_face_enhanced(
                known_face_encodings,
                face_encoding,
                known_face_names,
                image_quality
            )
            
            # Get face location
            top, right, bottom, left = face_locations[i]
            
            result = {
                "name": recognized_name,
                "confidence": round(confidence_score, 3),
                "confidence_level": confidence_level,
                "location": {"top": top, "right": right, "bottom": bottom, "left": left},
                "details": details
            }
            
            results.append(result)
        
        return {
            "faces_found": len(face_encodings),
            "results": results,
            "image_quality": round(image_quality, 3),
            "enhanced_recognition": True
        }
        
    except Exception as e:
        return {"error": f"Face recognition failed: {str(e)}"}

def get_annotated_image(image, recognition_results):
    """Add annotations to the image showing recognition results"""
    annotated_image = image.copy()
    
    for face in recognition_results['faces']:
        top, right, bottom, left = face['location']
        
        if face['recognized']:
            # Green rectangle for recognized faces
            cv2.rectangle(annotated_image, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Add name label
            name = face.get('name', 'Unknown')
            cv2.putText(annotated_image, name, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            # Red rectangle for unrecognized faces
            cv2.rectangle(annotated_image, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(annotated_image, 'Unknown', (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    return annotated_image

def recognize_faces_realtime(video_capture, known_faces_dir="local_face_recognition/faces"):
    """
    Enhanced real-time face recognition with adaptive thresholds
    """
    try:
        # Load known faces
        known_face_encodings, known_face_details = load_known_faces()
        
        if not known_face_encodings:
            return {"error": "No known faces found in database"}
        
        # Extract names from known_face_details
        known_face_names = [details[1] for details in known_face_details]  # name is at index 1
        
        # Get video properties
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))
        frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Initialize video writer for output
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, fps, (frame_width, frame_height))
        
        frame_count = 0
        recognition_results = []
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every 3rd frame for performance
            if frame_count % 3 != 0:
                continue
            
            # Convert BGR to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = fr.face_locations(rgb_frame)
            face_encodings = fr.face_encodings(rgb_frame, face_locations)
            
            # Assess frame quality
            frame_quality = enhanced_face_recognition.assess_image_quality(frame)
            
            # Process each detected face
            for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
                # Enhanced recognition with adaptive thresholds
                recognized_name, confidence_score, confidence_level, details = enhanced_face_recognition.recognize_face_enhanced(
                    known_face_encodings,
                    face_encoding,
                    known_face_names,
                    frame_quality
                )
                
                # Draw results on frame
                top, right, bottom, left = face_location
                
                # Color based on confidence level
                if confidence_level == "high":
                    color = (0, 255, 0)  # Green
                elif confidence_level == "medium":
                    color = (0, 255, 255)  # Yellow
                elif confidence_level == "low":
                    color = (0, 165, 255)  # Orange
                else:
                    color = (0, 0, 255)  # Red
                
                # Draw rectangle around face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label with name and confidence
                label = f"{recognized_name} ({confidence_score:.2f})"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                
                # Draw background for label
                cv2.rectangle(frame, 
                            (left, bottom - label_size[1] - 10),
                            (left + label_size[0], bottom),
                            color, cv2.FILLED)
                
                # Draw text
                cv2.putText(frame, label, (left, bottom - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Store results
                result = {
                    "frame": frame_count,
                    "name": recognized_name,
                    "confidence": round(confidence_score, 3),
                    "confidence_level": confidence_level,
                    "location": {"top": top, "right": right, "bottom": bottom, "left": left},
                    "details": details
                }
                recognition_results.append(result)
            
            # Write frame to output video
            out.write(frame)
            
            # Display frame (optional)
            cv2.imshow('Enhanced Face Recognition', frame)
            
            # Break on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        video_capture.release()
        out.release()
        cv2.destroyAllWindows()
        
        return {
            "total_frames_processed": frame_count,
            "faces_detected": len(recognition_results),
            "recognition_results": recognition_results,
            "enhanced_recognition": True
        }
        
    except Exception as e:
        return {"error": f"Real-time recognition failed: {str(e)}"} 