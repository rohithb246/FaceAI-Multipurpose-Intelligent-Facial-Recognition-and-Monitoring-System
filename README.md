# FaceAI — Age, Gender, Face Recognition & Driver Monitoring

FaceAI is a Flask web application for local face analysis. It provides age and gender prediction, heuristic emotion detection, user accounts, local face registration/recognition, and a browser-camera driver-monitoring page that warns about sustained eye closure.

> **Important:** This is an educational/local demonstration project. Do not use it for safety-critical driving decisions, biometric security, identity verification, surveillance, or decisions affecting people. Obtain consent before processing anyone's face image.

## Features

- **Age and gender analysis** using bundled OpenCV Caffe DNN models.
- **Emotion estimation** using OpenCV Haar-cascade facial features.
- **Face registration and recognition** backed by SQLite and local image files.
- **Driver monitoring** from a browser camera feed, with blink counting and a sustained-eye-closure alert.
- **User authentication**: sign-up, sign-in, profile, password reset flow, and role-based admin pages.
- **Admin tools**: manage users, face registrations, feedback, and recognition settings.
- **AI chatbot** with local rule-based responses.

## Technology

| Area | Tools |
| --- | --- |
| Web server | Flask, Flask-CORS, Flask-Mail |
| Computer vision | OpenCV, NumPy |
| Storage | SQLite (`users.db`) |
| UI | HTML, CSS, JavaScript, Bootstrap |
| Models | OpenCV face detector and Caffe age/gender models |

The repository includes OpenCV compatibility modules named `face_recognition.py` and `dlib.py`. They allow the face-recognition and driver-monitoring pages to run on modern Windows/Python installations without compiling the native `dlib` package. They are intended for demonstrations and trade accuracy for portability.

## Project layout

```text
.
├── app.py                         # Main Flask application
├── requirements.txt               # Runtime dependencies
├── run_app.bat                    # Windows launcher for the local runtime
├── database.py                    # SQLite users, password reset, feedback logic
├── face_recognition.py            # OpenCV face-recognition compatibility layer
├── dlib.py                        # OpenCV driver-monitoring compatibility layer
├── driver_monitoring_web.py       # Browser-frame driver monitoring logic
├── emotion_detector.py            # Haar-cascade emotion estimator
├── local_face_recognition/        # Face image/database helpers
├── templates/                     # Flask/Jinja HTML templates
├── static/                        # CSS, images, and browser JavaScript
├── users.db                       # Local development database (not for production)
├── opencv_face_detector_uint8.pb  # Face detector model
├── age_net.caffemodel             # Age model
└── gender_net.caffemodel          # Gender model
```

## Requirements

- Python **3.10–3.12**
- Windows, macOS, or Linux
- A webcam and a browser with camera permission for driver monitoring
- Internet access only for the first dependency installation

OpenCV 5 is intentionally excluded: it removed the Caffe importer required by the bundled age/gender models.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-user>/FaceAI.git
cd FaceAI
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

On this repository's prepared Windows workspace, `run_app.bat` starts the local `.runtime` environment. For a fresh GitHub clone, create `.venv` with the steps above instead.

## Default local admin account

The development database creates this account when it is empty:

```text
Email:    admin@faceanalysis.com
Password: admin123
```

Change the password immediately after first login. Never deploy this default credential or commit a real production database.

## How to use

### Age, gender, and emotion analysis

1. Open **Face Analysis**.
2. Capture or upload a clear, front-facing image.
3. Submit the image to see age, gender, emotion, and confidence estimates.

### Face recognition

1. Sign in as an administrator.
2. Register a face from the admin registration page using a clear, well-lit, front-facing image.
3. Sign in as a user and open **Face Recognition**.
4. Allow camera access and capture a similarly lit face.

For the best local-demo results, use one face per image, keep the face centered, and re-register when camera angle or lighting changes.

### Driver monitoring

1. Open **Driver Monitoring**.
2. Select **Start Monitoring** and permit camera access.
3. Keep one face visible in good, even lighting.
4. A brief closure increments the blink count after the eyes reopen.
5. Keeping both eyes closed for roughly 0.6 seconds raises the visual drowsiness alert; reopening eyes clears it.

The driver monitor is not a medical device or a real-world driver-safety system.

## Main routes and API endpoints

| Route | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Home / face analysis page |
| `/login` | GET | Login page |
| `/api/login` | POST | Authenticate a user |
| `/api/signup` | POST | Create a user account |
| `/analyze` | POST | Analyze a base64-encoded face image |
| `/api/face-recognize` | POST | Recognize a registered face (authenticated) |
| `/api/driver-monitoring` | POST | Process a base64 browser-camera frame |
| `/api/driver-monitoring/reset` | POST | Reset blink and closure counters |
| `/admin` | GET | Administrator dashboard |
| `/api/admin/registered-people` | GET | Registered people (admin) |

### Driver-monitoring request example

```json
{
  "frame": "data:image/jpeg;base64,<base64-image>"
}
```

The response includes `drowsiness_detected`, `total_blinks`, `drowsy_counter`, eye metrics, and a processed image.

## Configuration and data

- Set `SECRET_KEY` before any shared or production deployment.
- Configure mail settings in environment variables or `email_config.py` before using password-reset email.
- `users.db` is a local SQLite database. Back it up before testing destructive admin operations.
- Face images are stored under `local_face_recognition/faces/` when people are registered.

## Troubleshooting

### `Caffe importer has been removed`

You installed OpenCV 5. Reinstall the supported version:

```bash
python -m pip install --upgrade --force-reinstall "opencv-python<5"
```

### `No module named 'dlib'` or `No module named 'face_recognition'`

Use the latest repository files and restart the app. The project includes OpenCV compatibility modules, so native `dlib` is not required for the local demo.

### Camera does not start

- Use `http://127.0.0.1:5000` or `http://localhost:5000`.
- Allow camera permission in the browser.
- Close other programs using the webcam.
- Ensure a face is well lit and visible in the frame.

### The dashboard says `face_manager` is unavailable

Stop the server and start it again after pulling the latest code:

```bash
python app.py
```

## Preparing the repository for GitHub

Before committing:

1. Do not commit virtual environments, caches, real `.env` files, or production databases.
2. Keep model files only if your Git host accepts their size; otherwise use Git LFS or document a download step.
3. Remove default credentials and set a strong `SECRET_KEY` for any deployed environment.
4. Add screenshots or a short demo video to improve the GitHub project page.

```bash
git add README.md .gitignore requirements.txt app.py
git status
git commit -m "Document FaceAI setup and usage"
git push origin main
```

## License

This repository includes an [MIT License](LICENSE). Review the licenses and terms for all bundled models and third-party dependencies before distributing the project.
