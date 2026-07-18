<<<<<<< HEAD
#!/usr/bin/env python3
"""
Test script for face recognition integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from face_recognition_integration import face_manager
    print("✅ Face recognition integration imported successfully")
    
    # Test database initialization
    print("\n🔧 Testing database initialization...")
    face_manager.init_db()
    print("✅ Database initialized successfully")
    
    # Test getting all people
    print("\n👥 Testing get all people...")
    people = face_manager.get_all_people()
    print(f"✅ Found {len(people)} registered people in database")
    
    if people:
        print("\n📋 Registered people:")
        for person in people:
            id, name, age, phone, image_path, user_id, created_at = person
            print(f"  - {name} (Age: {age}, Phone: {phone}, User ID: {user_id})")
    
    print("\n🎉 Face recognition system is ready!")
    print("\n📁 Files created:")
    print("  - face_recognition_system/db_manager.py")
    print("  - face_recognition_system/capture_face.py") 
    print("  - face_recognition_system/face_recognition_core.py")
    print("  - face_recognition_system/faces/ (directory)")
    print("  - face_recognition_system/people.db")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all required packages are installed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
=======
#!/usr/bin/env python3
"""
Test script for face recognition integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from face_recognition_integration import face_manager
    print("✅ Face recognition integration imported successfully")
    
    # Test database initialization
    print("\n🔧 Testing database initialization...")
    face_manager.init_db()
    print("✅ Database initialized successfully")
    
    # Test getting all people
    print("\n👥 Testing get all people...")
    people = face_manager.get_all_people()
    print(f"✅ Found {len(people)} registered people in database")
    
    if people:
        print("\n📋 Registered people:")
        for person in people:
            id, name, age, phone, image_path, user_id, created_at = person
            print(f"  - {name} (Age: {age}, Phone: {phone}, User ID: {user_id})")
    
    print("\n🎉 Face recognition system is ready!")
    print("\n📁 Files created:")
    print("  - face_recognition_system/db_manager.py")
    print("  - face_recognition_system/capture_face.py") 
    print("  - face_recognition_system/face_recognition_core.py")
    print("  - face_recognition_system/faces/ (directory)")
    print("  - face_recognition_system/people.db")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all required packages are installed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
>>>>>>> a8a36cb1c8a89472d874daa0bf4ce03cfbef9114
    traceback.print_exc() 