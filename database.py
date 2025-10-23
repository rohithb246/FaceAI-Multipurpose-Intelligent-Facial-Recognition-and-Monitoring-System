import sqlite3
import os
from datetime import datetime, timedelta
import hashlib
import secrets

class Database:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create password reset requests table for admin tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                user_id INTEGER,
                request_ip TEXT,
                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                email_sent BOOLEAN DEFAULT 0,
                email_sent_time TIMESTAMP,
                token_created TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create admin user if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO users (full_name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin User', 'admin@faceanalysis.com', 
              hashlib.sha256('admin123'.encode()).hexdigest(), 'admin', datetime.now()))
        
        conn.commit()
        conn.close()
    
    def add_user(self, full_name, email, password, role='user'):
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (full_name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, email, password_hash, role, datetime.now()))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return user_id
        except sqlite3.IntegrityError:
            return None  # Email already exists
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, password_hash, role, created_at, last_login, is_active
            FROM users WHERE email = ?
        ''', (email,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id': user_data[0],
                'full_name': user_data[1],
                'email': user_data[2],
                'password_hash': user_data[3],
                'role': user_data[4],
                'created_at': user_data[5],
                'last_login': user_data[6],
                'is_active': user_data[7]
            }
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, password_hash, role, created_at, last_login, is_active
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id': user_data[0],
                'full_name': user_data[1],
                'email': user_data[2],
                'password_hash': user_data[3],
                'role': user_data[4],
                'created_at': user_data[5],
                'last_login': user_data[6],
                'is_active': user_data[7]
            }
        return None
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now(), user_id))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """Get all users from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, role, created_at, last_login, is_active
            FROM users ORDER BY created_at DESC
        ''')
        
        users_data = cursor.fetchall()
        conn.close()
        
        users = {}
        for user_data in users_data:
            users[user_data[0]] = {
                'id': user_data[0],
                'full_name': user_data[1],
                'email': user_data[2],
                'role': user_data[3],
                'created_at': user_data[4],
                'last_login': user_data[5],
                'is_active': user_data[6]
            }
        
        return users
    
    def delete_user(self, user_id):
        """Delete a user from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_user_role(self, user_id, new_role):
        """Update user role"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def create_password_reset_token(self, user_id, expires_in_hours=24):
        """Create a password reset token for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate a secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            # Invalidate any existing tokens for this user
            cursor.execute('''
                UPDATE password_reset_tokens 
                SET used = 1 
                WHERE user_id = ? AND used = 0
            ''', (user_id,))
            
            # Create new token
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, token, expires_at))
            
            conn.commit()
            conn.close()
            return token
        except:
            return None
    
    def get_user_by_reset_token(self, token):
        """Get user by reset token if it's valid and not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.full_name, u.email, u.password_hash, u.role, u.created_at, u.last_login, u.is_active
            FROM users u
            JOIN password_reset_tokens prt ON u.id = prt.user_id
            WHERE prt.token = ? AND prt.used = 0 AND prt.expires_at > ?
        ''', (token, datetime.now()))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id': user_data[0],
                'full_name': user_data[1],
                'email': user_data[2],
                'password_hash': user_data[3],
                'role': user_data[4],
                'created_at': user_data[5],
                'last_login': user_data[6],
                'is_active': user_data[7]
            }
        return None
    
    def mark_reset_token_used(self, token):
        """Mark a reset token as used"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE password_reset_tokens 
                SET used = 1 
                WHERE token = ?
            ''', (token,))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_user_password(self, user_id, new_password):
        """Update user's password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ? 
                WHERE id = ?
            ''', (password_hash, user_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def log_password_reset_request(self, email, user_id=None, request_ip=None):
        """Log a password reset request for admin tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO password_reset_requests (email, user_id, request_ip, status)
                VALUES (?, ?, ?, ?)
            ''', (email, user_id, request_ip, 'pending'))
            
            request_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return request_id
        except:
            return None
    
    def update_password_reset_request(self, request_id, status, email_sent=False, token=None, user_id=None):
        """Update password reset request status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                # Update user_id if provided
                cursor.execute('''
                    UPDATE password_reset_requests 
                    SET user_id = ?, status = ?
                    WHERE id = ?
                ''', (user_id, status, request_id))
            elif email_sent:
                cursor.execute('''
                    UPDATE password_reset_requests 
                    SET status = ?, email_sent = 1, email_sent_time = ?, token_created = ?
                    WHERE id = ?
                ''', (status, datetime.now(), token, request_id))
            else:
                cursor.execute('''
                    UPDATE password_reset_requests 
                    SET status = ?, token_created = ?
                    WHERE id = ?
                ''', (status, token, request_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_password_reset_requests(self):
        """Get all password reset requests for admin panel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prr.id, prr.email, prr.user_id, prr.request_ip, prr.request_time, 
                   prr.status, prr.email_sent, prr.email_sent_time, prr.token_created,
                   u.full_name, u.role
            FROM password_reset_requests prr
            LEFT JOIN users u ON prr.user_id = u.id
            ORDER BY prr.request_time DESC
        ''')
        
        requests_data = cursor.fetchall()
        conn.close()
        
        requests = []
        for req_data in requests_data:
            requests.append({
                'id': req_data[0],
                'email': req_data[1],
                'user_id': req_data[2],
                'request_ip': req_data[3],
                'request_time': req_data[4],
                'status': req_data[5],
                'email_sent': req_data[6],
                'email_sent_time': req_data[7],
                'token_created': req_data[8],
                'user_name': req_data[9] if req_data[9] else 'Unknown User',
                'user_role': req_data[10] if req_data[10] else 'Unknown'
            })
        
        return requests

# Initialize database
db = Database() 