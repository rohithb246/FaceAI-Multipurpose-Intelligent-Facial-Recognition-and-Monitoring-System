#!/usr/bin/env python3
"""
Test script to analyze a specific image file
"""

import cv2
import face_recognition
import os

def test_image(image_path):
    """Test a specific image file"""
    print(f"Testing image: {image_path}")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(image_path):
        print("❌ File does not exist!")
        return False
    
    # Check file size
    file_size = os.path.getsize(image_path)
    print(f"File size: {file_size} bytes")
    
    # Try to load with OpenCV
    try:
        cv_image = cv2.imread(image_path)
        if cv_image is None:
            print("❌ OpenCV cannot load the image!")
            return False
        
        print(f"✅ OpenCV loaded image successfully")
        print(f"   Image dimensions: {cv_image.shape}")
        print(f"   Image type: {cv_image.dtype}")
        
        # Show some pixel values
        print(f"   Sample pixel values (top-left): {cv_image[0, 0]}")
        
    except Exception as e:
        print(f"❌ OpenCV error: {e}")
        return False
    
    # Try to load with face_recognition
    try:
        image = face_recognition.load_image_file(image_path)
        print(f"✅ Face recognition library loaded image")
        print(f"   Image dimensions: {image.shape}")
        
    except Exception as e:
        print(f"❌ Face recognition error: {e}")
        return False
    
    # Try face detection
    try:
        face_locations = face_recognition.face_locations(image)
        print(f"✅ Face detection completed")
        print(f"   Found {len(face_locations)} faces")
        
        if face_locations:
            for i, (top, right, bottom, left) in enumerate(face_locations):
                print(f"   Face {i+1}: top={top}, right={right}, bottom={bottom}, left={left}")
        else:
            print("   ⚠️  No faces detected!")
            return False
            
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return False
    
    # Try face encoding
    try:
        face_encodings = face_recognition.face_encodings(image, face_locations)
        print(f"✅ Face encoding completed")
        print(f"   Encoded {len(face_encodings)} faces")
        
        if face_encodings:
            print(f"   Encoding length: {len(face_encodings[0])}")
            return True
        else:
            print("   ⚠️  No face encodings generated!")
            return False
            
    except Exception as e:
        print(f"❌ Face encoding error: {e}")
        return False

def main():
    """Main function"""
    # Test the specific image from the database
    image_path = "faces/2e5ddeff7c344929835527b9ced5a82a.jpg"
    
    print("Image Analysis Tool")
    print("=" * 50)
    
    success = test_image(image_path)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Image is valid and contains detectable faces!")
    else:
        print("❌ Image has problems and should be replaced.")
        print("💡 Try re-registering the person with a better quality image.")

if __name__ == "__main__":
    main() 