#!/usr/bin/env python3
"""
Database Cleanup Script for Face Recognition System
This script helps identify and fix problematic database entries.
"""

import os
import sqlite3
import face_recognition
import cv2

def check_database_entries():
    """Check all database entries and identify problems"""
    print("=" * 60)
    print("Database Cleanup and Analysis")
    print("=" * 60)
    
    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()
    
    # Get all people from database
    cursor.execute("SELECT * FROM persons")
    people = cursor.fetchall()
    
    if not people:
        print("No people found in database.")
        return
    
    print(f"Found {len(people)} people in database:")
    print("-" * 60)
    
    valid_entries = []
    problematic_entries = []
    
    for person in people:
        id, name, age, phone, image_path = person
        print(f"\nChecking: {name}")
        print(f"  ID: {id}")
        print(f"  Age: {age}")
        print(f"  Phone: {phone}")
        print(f"  Image: {image_path}")
        
        # Check if image file exists
        if not os.path.exists(image_path):
            print(f"  ❌ ERROR: Image file not found!")
            problematic_entries.append((id, name, "File not found"))
            continue
        
        # Check if image can be loaded
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"  ❌ ERROR: Cannot load image file!")
                problematic_entries.append((id, name, "Cannot load image"))
                continue
            
            print(f"  ✓ Image file exists and can be loaded")
            
            # Convert to RGB for face detection
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Check for faces
            face_locations = face_recognition.face_locations(rgb_image)
            if not face_locations:
                print(f"  ❌ ERROR: No face detected in image!")
                problematic_entries.append((id, name, "No face detected"))
                continue
            
            print(f"  ✓ Face detected in image")
            
            # Check if face can be encoded
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            if not face_encodings:
                print(f"  ❌ ERROR: Cannot encode face!")
                problematic_entries.append((id, name, "Cannot encode face"))
                continue
            
            print(f"  ✓ Face can be encoded successfully")
            valid_entries.append(person)
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            problematic_entries.append((id, name, str(e)))
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total entries: {len(people)}")
    print(f"Valid entries: {len(valid_entries)}")
    print(f"Problematic entries: {len(problematic_entries)}")
    
    if problematic_entries:
        print("\nProblematic entries:")
        for id, name, problem in problematic_entries:
            print(f"  - {name} (ID: {id}): {problem}")
    
    return valid_entries, problematic_entries

def cleanup_database(problematic_entries):
    """Remove problematic entries from database"""
    if not problematic_entries:
        print("No problematic entries to clean up.")
        return
    
    print(f"\nCleaning up {len(problematic_entries)} problematic entries...")
    
    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()
    
    for id, name, problem in problematic_entries:
        print(f"Removing {name} (ID: {id}) - {problem}")
        
        # Get image path before deleting
        cursor.execute("SELECT image_path FROM persons WHERE id = ?", (id,))
        result = cursor.fetchone()
        if result:
            image_path = result[0]
            
            # Delete from database
            cursor.execute("DELETE FROM persons WHERE id = ?", (id,))
            
            # Try to delete image file if it exists
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"  ✓ Deleted image file: {image_path}")
                except Exception as e:
                    print(f"  ⚠ Could not delete image file: {e}")
    
    conn.commit()
    conn.close()
    print("Database cleanup completed!")

def reset_database():
    """Reset the entire database (use with caution!)"""
    print("\n⚠ WARNING: This will delete ALL data from the database!")
    response = input("Are you sure you want to reset the database? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Database reset cancelled.")
        return
    
    # Delete all image files
    if os.path.exists('faces'):
        for file in os.listdir('faces'):
            if file.endswith(('.jpg', '.jpeg', '.png')):
                try:
                    os.remove(os.path.join('faces', file))
                    print(f"Deleted: {file}")
                except Exception as e:
                    print(f"Could not delete {file}: {e}")
    
    # Reset database
    conn = sqlite3.connect('people.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM persons")
    conn.commit()
    conn.close()
    
    print("Database reset completed!")

def main():
    """Main cleanup function"""
    print("Face Recognition System - Database Cleanup")
    print("=" * 60)
    
    # Check current state
    valid_entries, problematic_entries = check_database_entries()
    
    if not problematic_entries:
        print("\n✅ Database is clean! All entries are valid.")
        return
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Clean up problematic entries (recommended)")
    print("2. Reset entire database (deletes everything)")
    print("3. Exit without changes")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        cleanup_database(problematic_entries)
    elif choice == '2':
        reset_database()
    elif choice == '3':
        print("No changes made.")
    else:
        print("Invalid choice. No changes made.")

if __name__ == "__main__":
    main() 