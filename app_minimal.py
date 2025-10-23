from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
import os
import secrets
from datetime import datetime, timedelta

# Import database module
try:
    from database import db
except ImportError:
    # Create a simple mock database if the real one isn't available
    class MockDB:
        def get_user_by_id(self, user_id):
            return None
        def get_all_users(self):
            return []
    db = MockDB()

# Import email config
try:
    from email_config import get_email_config
except ImportError:
    def get_email_config():
        return {
            'MAIL_SERVER': 'smtp.gmail.com',
            'MAIL_PORT': 587,
            'MAIL_USE_TLS': True,
            'MAIL_USERNAME': 'your-email@gmail.com',
            'MAIL_PASSWORD': 'your-password'
        }

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Email configuration
    email_config = get_email_config()
    app.config.update(email_config)
    
    return app

app = create_app()
mail = Mail(app)

@app.route('/')
def home():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('face-analysis.html', user=user, users=all_users)

@app.route('/face-analysis')
def face_analysis():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('face-analysis.html', user=user, users=all_users)

@app.route('/services')
def services():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('services.html', user=user, users=all_users)

@app.route('/about')
def about():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('about.html', user=user, users=all_users)

@app.route('/demo')
def demo():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('demo.html', user=user, users=all_users)

@app.route('/contact')
def contact():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('contact.html', user=user, users=all_users)

@app.route('/signup')
def signup():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('signup.html', user=user, users=all_users)

@app.route('/login')
def login():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    all_users = db.get_all_users()
    return render_template('login.html', user=user, users=all_users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/analyze', methods=['POST'])
def analyze():
    # Mock response for now
    return jsonify({
        'success': True,
        'message': 'Face analysis feature is being set up. Please install required dependencies.',
        'age': 'N/A',
        'gender': 'N/A',
        'emotion': 'N/A'
    })

if __name__ == '__main__':
    print("Starting FaceAI application...")
    print("Note: This is a minimal version. Some features may not work without additional dependencies.")
    app.run(debug=True, host='0.0.0.0', port=5000) 