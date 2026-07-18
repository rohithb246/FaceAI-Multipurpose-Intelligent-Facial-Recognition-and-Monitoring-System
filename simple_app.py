<<<<<<< HEAD
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>FaceAI - Working!</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background-color: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .success { color: #27ae60; font-weight: bold; }
            .info { background: #3498db; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 FaceAI Application is Working!</h1>
            <p class="success">✅ Flask server is running successfully</p>
            <div class="info">
                <strong>Access URLs:</strong><br>
                • <a href="http://127.0.0.1:8080" style="color: white;">http://127.0.0.1:8080</a><br>
                • <a href="http://localhost:8080" style="color: white;">http://localhost:8080</a>
            </div>
            <p>Your FaceAI application is now ready for development!</p>
            <p><strong>Next steps:</strong></p>
            <ul>
                <li>Install additional dependencies for full features</li>
                <li>Configure email settings</li>
                <li>Set up database</li>
            </ul>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting FaceAI Application")
    print("=" * 50)
    print("📱 Access your application at:")
    print("   http://127.0.0.1:8080")
    print("   http://localhost:8080")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=8080)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
=======
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>FaceAI - Working!</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background-color: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .success { color: #27ae60; font-weight: bold; }
            .info { background: #3498db; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 FaceAI Application is Working!</h1>
            <p class="success">✅ Flask server is running successfully</p>
            <div class="info">
                <strong>Access URLs:</strong><br>
                • <a href="http://127.0.0.1:8080" style="color: white;">http://127.0.0.1:8080</a><br>
                • <a href="http://localhost:8080" style="color: white;">http://localhost:8080</a>
            </div>
            <p>Your FaceAI application is now ready for development!</p>
            <p><strong>Next steps:</strong></p>
            <ul>
                <li>Install additional dependencies for full features</li>
                <li>Configure email settings</li>
                <li>Set up database</li>
            </ul>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting FaceAI Application")
    print("=" * 50)
    print("📱 Access your application at:")
    print("   http://127.0.0.1:8080")
    print("   http://localhost:8080")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=8080)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
>>>>>>> a8a36cb1c8a89472d874daa0bf4ce03cfbef9114
        print("💡 Try running as administrator or check if port 8080 is available") 