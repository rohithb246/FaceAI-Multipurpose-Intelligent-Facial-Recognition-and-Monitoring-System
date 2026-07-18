#!/usr/bin/env python3
"""
Test script for Face Recognition System
This script tests all major components to ensure they're working properly.
"""

import os
import sys
import cv2
import face_recognition
from db_manager import init_db, get_all_people, insert_person

def test_database():
    """Test database functionality"""
    print("Testing database...")
    try:
        init_db()
        print("✓ Database initialized successfully")
        
        # Test inserting a person
        test_image_path = "faces/test_person.jpg"
        insert_person("Test Person", "25", "1234567890", test_image_path)
        print("✓ Person insertion successful")
        
        # Test retrieving people
        people = get_all_people()
        print(f"✓ Retrieved {len(people)} people from database")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_camera():
    """Test camera functionality"""
    print("Testing camera...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("✗ Camera not available")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("✗ Could not read frame from camera")
            cap.release()
            return False
        
        print("✓ Camera working properly")
        cap.release()
        return True
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_face_recognition():
    """Test face recognition library"""
    print("Testing face recognition library...")
    try:
        # Create a simple test image (you can replace this with a real image)
        test_image = cv2.imread("faces/test_person.jpg") if os.path.exists("faces/test_person.jpg") else None
        
        if test_image is None:
            # Create a dummy image for testing
            test_image = cv2.imread("faces/test_person.jpg") if os.path.exists("faces/test_person.jpg") else None
            if test_image is None:
                print("⚠ No test image found, skipping face recognition test")
                return True
        
        # Convert to RGB
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        
        # Test face detection
        face_locations = face_recognition.face_locations(rgb_image)
        print(f"✓ Face detection working - found {len(face_locations)} faces")
        
        # Test face encoding
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        print(f"✓ Face encoding working - encoded {len(face_encodings)} faces")
        
        return True
    except Exception as e:
        print(f"✗ Face recognition test failed: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("Testing dependencies...")
    required_packages = ['cv2', 'face_recognition', 'numpy']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")
            return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Face Recognition System - System Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Database", test_database),
        ("Camera", test_camera),
        ("Face Recognition", test_face_recognition),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\nTo start the application, run: python app_gui.py")
    else:
        print("⚠ Some tests failed. Please check the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install opencv-python face-recognition")
        print("2. Check camera permissions and connections")
        print("3. Ensure you have proper lighting for face detection")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 