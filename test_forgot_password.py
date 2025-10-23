#!/usr/bin/env python3
"""
Test script for forgot password functionality
"""

import requests
import json

def test_forgot_password():
    base_url = "http://127.0.0.1:5000"
    
    print("=== Testing Forgot Password Functionality ===\n")
    
    # Test 1: Submit forgot password form with non-existent email
    print("Test 1: Non-existent email")
    data = {
        'email': 'nonexistent@example.com'
    }
    
    try:
        response = requests.post(f"{base_url}/forgot-password", data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print("✅ Test 1 completed\n")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}\n")
    
    # Test 2: Submit forgot password form with existing email (admin)
    print("Test 2: Existing email (admin)")
    data = {
        'email': 'admin@faceanalysis.com'
    }
    
    try:
        response = requests.post(f"{base_url}/forgot-password", data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print("✅ Test 2 completed\n")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}\n")
    
    # Test 3: Check if forgot password page loads
    print("Test 3: Forgot password page load")
    try:
        response = requests.get(f"{base_url}/forgot-password")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Forgot password page loads successfully")
        else:
            print("❌ Forgot password page failed to load")
        print("✅ Test 3 completed\n")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}\n")

def test_database_queries():
    """Test database queries for password reset requests"""
    print("=== Testing Database Queries ===\n")
    
    try:
        from database import db
        
        # Test getting password reset requests
        requests = db.get_password_reset_requests()
        print(f"Total password reset requests: {len(requests)}")
        
        if requests:
            print("\nRecent password reset requests:")
            for req in requests[:3]:  # Show first 3
                print(f"- ID: {req['id']}, Email: {req['email']}, Status: {req['status']}")
        
        print("✅ Database queries test completed\n")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}\n")

if __name__ == "__main__":
    print("Starting forgot password tests...\n")
    
    # Test the web functionality
    test_forgot_password()
    
    # Test database functionality
    test_database_queries()
    
    print("=== Test Summary ===")
    print("1. Make sure Flask app is running: python app.py")
    print("2. Install flask-mail: pip install flask-mail")
    print("3. Set up email credentials in environment variables")
    print("4. Test forgot password functionality")
    print("5. Check admin panel for password reset requests") 