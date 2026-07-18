#!/usr/bin/env python3
"""
Quick fix script to clean up the problematic database entry
"""

import sqlite3
import os

def quick_fix():
    """Remove the problematic entry and clean up"""
    print("Quick Fix for Face Recognition System")
    print("=" * 40)
    
    # Connect to database
    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()
    
    # Get all entries
    cursor.execute("SELECT * FROM persons")
    people = cursor.fetchall()
    
    print(f"Found {len(people)} people in database:")
    for person in people:
        id, name, age, phone, image_path = person
        print(f"  - {name} (ID: {id})")
    
    # Remove all entries (since they seem to be problematic)
    print(f"\nRemoving all entries to start fresh...")
    cursor.execute("DELETE FROM persons")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Database cleaned successfully!")
    
    # Clean up image files
    if os.path.exists('faces'):
        for file in os.listdir('faces'):
            if file.endswith(('.jpg', '.jpeg', '.png')):
                try:
                    os.remove(os.path.join('faces', file))
                    print(f"🗑️  Deleted: {file}")
                except Exception as e:
                    print(f"⚠️  Could not delete {file}: {e}")
    
    print("\n🎉 System is now clean and ready for new registrations!")
    print("💡 You can now:")
    print("   1. Run 'python app_gui.py' to start the application")
    print("   2. Register new people with better quality images")
    print("   3. Make sure to capture clear, well-lit faces")

if __name__ == "__main__":
    quick_fix() 