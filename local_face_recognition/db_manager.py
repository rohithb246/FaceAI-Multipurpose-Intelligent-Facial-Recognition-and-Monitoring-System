import sqlite3
import os

# Use the same database as the main application
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS face_recognition_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    # This table is read by get_all_people().  Creating it here (rather than
    # on the first registration) makes a clean installation usable before a
    # face has been enrolled.
    c.execute('''CREATE TABLE IF NOT EXISTS face_recognition_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    age INTEGER,
                    contact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    conn.commit()
    conn.close()

def insert_person(user_id, image_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO face_recognition_data (user_id, image_path) VALUES (?, ?)",
              (user_id, image_path))
    conn.commit()
    conn.close()

def insert_person_with_details(user_id, age, contact, image_path):
    """Insert a person with all details including user_id"""
    conn = None
    try:
        print(f"🔍 Inserting person: user_id={user_id}, age={age}, contact={contact}, image_path={image_path}")
        
        # First, make sure the face_recognition_details table exists
        conn = sqlite3.connect(DB_PATH, timeout=20.0)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS face_recognition_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    age INTEGER,
                    contact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
        conn.commit()
        
        # Insert the face image path
        c.execute("INSERT INTO face_recognition_data (user_id, image_path) VALUES (?, ?)",
                  (user_id, image_path))
        face_data_id = c.lastrowid
        print(f"✅ Inserted face data with ID: {face_data_id}")
        
        # Insert or update user details
        c.execute("SELECT id FROM face_recognition_details WHERE user_id = ?", (user_id,))
        existing = c.fetchone()
        
        if existing:
            c.execute("UPDATE face_recognition_details SET age = ?, contact = ? WHERE user_id = ?",
                      (age, contact, user_id))
            print(f"✅ Updated existing face details for user {user_id}")
        else:
            c.execute("INSERT INTO face_recognition_details (user_id, age, contact) VALUES (?, ?, ?)",
                      (user_id, age, contact))
            print(f"✅ Inserted new face details for user {user_id}")
        
        conn.commit()
        print(f"✅ Database insertion completed successfully")
        
        return face_data_id
        
    except Exception as e:
        print(f"❌ Error inserting person details: {e}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def get_all_people():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT f.id, u.full_name, 
               COALESCE(d.age, ''), 
               COALESCE(d.contact, ''), 
               f.image_path,
               f.created_at
        FROM face_recognition_data f
        JOIN users u ON f.user_id = u.id
        LEFT JOIN face_recognition_details d ON f.user_id = d.user_id
        WHERE u.is_active = 1 OR u.email LIKE 'unknown_%@temp.com'
    """)
    people = c.fetchall()
    conn.close()
    return people

def get_user_face_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT f.id, f.image_path, f.created_at 
        FROM face_recognition_data f 
        WHERE f.user_id = ?
    """, (user_id,))
    face_data = c.fetchall()
    conn.close()
    return face_data

def delete_face_data(face_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM face_recognition_data WHERE id = ?", (face_id,))
    conn.commit()
    conn.close()

def delete_person(person_id):
    """Delete a person and their face data"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20.0)  # Increase timeout to handle locks
        c = conn.cursor()
        
        # First get the user_id and image_path from face_recognition_data
        c.execute("SELECT user_id, image_path FROM face_recognition_data WHERE id = ?", (person_id,))
        result = c.fetchone()
        
        if result:
            user_id, image_path = result
            
            # Delete from face_recognition_details first
            c.execute("DELETE FROM face_recognition_details WHERE user_id = ?", (user_id,))
            
            # Delete from face_recognition_data
            c.execute("DELETE FROM face_recognition_data WHERE id = ?", (person_id,))
            
            # Also delete the actual image file if it exists
            if image_path:
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"✅ Deleted image file: {image_path}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not delete image file {image_path}: {e}")
            
            # If this was a temporary user (unknown person), also delete from users table
            c.execute("SELECT email FROM users WHERE id = ?", (user_id,))
            user_result = c.fetchone()
            if user_result and user_result[0] and user_result[0].startswith('unknown_'):
                c.execute("DELETE FROM users WHERE id = ?", (user_id,))
                print(f"✅ Deleted temporary user with ID: {user_id}")
            
            conn.commit()
            print(f"✅ Successfully deleted person with ID: {person_id}")
            return True
        else:
            print(f"❌ Person with ID {person_id} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting person: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
