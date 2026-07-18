import sqlite3
import os

def init_db():
    """Initialize the face recognition database"""
    db_path = os.path.join(os.path.dirname(__file__), 'people.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    phone TEXT,
                    image_path TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def insert_person(name, age, phone, image_path, user_id=None):
    """Insert a person with all details"""
    db_path = os.path.join(os.path.dirname(__file__), 'people.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO persons (name, age, phone, image_path, user_id) VALUES (?, ?, ?, ?, ?)",
              (name, age, phone, image_path, user_id))
    conn.commit()
    conn.close()

def get_all_people():
    """Get all registered people"""
    db_path = os.path.join(os.path.dirname(__file__), 'people.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM persons")
    people = c.fetchall()
    conn.close()
    return people

def get_person_by_user_id(user_id):
    """Get person details by user_id"""
    db_path = os.path.join(os.path.dirname(__file__), 'people.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM persons WHERE user_id = ?", (user_id,))
    person = c.fetchone()
    conn.close()
    return person

def delete_person(person_id):
    """Delete a person by ID"""
    db_path = os.path.join(os.path.dirname(__file__), 'people.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM persons WHERE id = ?", (person_id,))
    conn.commit()
    conn.close()

def update_person(person_id, name, age, phone):
    """Update person details"""
    db_path = os.path.join(os.path.dirname(__file__), 'people.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE persons SET name = ?, age = ?, phone = ? WHERE id = ?", 
              (name, age, phone, person_id))
    conn.commit()
    conn.close()
