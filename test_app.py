from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello! FaceAI is working!</h1><p>Your Flask application is running successfully.</p>'

@app.route('/test')
def test():
    return '<h1>Test Page</h1><p>This is a test page to verify the application is working.</p>'

if __name__ == '__main__':
    print("Starting simple test application...")
    print("Access the application at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000) 