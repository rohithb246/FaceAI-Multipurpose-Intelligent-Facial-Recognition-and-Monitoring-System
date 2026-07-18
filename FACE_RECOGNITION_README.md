# Face Recognition Integration - FaceAI

## 🎯 Overview

This document explains the integrated face recognition system that combines the working face recognition functionality with the main FaceAI application.

## 📁 File Structure

```
Age-gender-detection/
├── face_recognition_system/
│   ├── db_manager.py              # Database management functions
│   ├── capture_face.py            # Face capture and registration
│   ├── face_recognition_core.py   # Core face recognition functions
│   ├── faces/                     # Directory for stored face images
│   └── people.db                  # SQLite database for face data
├── face_recognition_integration.py # Main integration wrapper
├── templates/
│   ├── user-dashboard.html        # User dashboard showing face details
│   ├── admin-face-registration.html # Admin face registration page
│   └── face-recognition.html      # Face recognition interface
└── app.py                         # Main Flask application
```

## 🔄 Workflow

### 1. Admin Registration Process
1. **Admin adds user** via admin panel (`/admin`)
2. **Admin registers user's face** via "Register Face" button
3. **Face details stored** in `face_recognition_system/people.db`
4. **User can view their details** in user dashboard

### 2. User Experience
1. **User logs in** → redirected to `/user-dashboard`
2. **Dashboard shows** face registration status and details
3. **User can test recognition** via `/face-recognition`
4. **Real-time recognition** works with registered faces

## 🛠️ Key Components

### Database Schema (`people.db`)
```sql
CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    image_path TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Core Functions

#### `face_recognition_core.py`
- `load_known_faces()` - Load all registered faces from database
- `recognize_faces_in_image(image)` - Recognize faces in given image
- `get_annotated_image(image, results)` - Add annotations to image
- `recognize_faces_realtime()` - Real-time camera recognition

#### `db_manager.py`
- `init_db()` - Initialize database
- `insert_person(name, age, phone, image_path, user_id)` - Add new person
- `get_all_people()` - Get all registered people
- `get_person_by_user_id(user_id)` - Get person by user ID

#### `capture_face.py`
- `capture_and_register(name, age, phone, user_id)` - Capture and register face
- `capture_face_for_recognition()` - Capture face for testing

## 🚀 Usage

### For Admins

#### Add New User
1. Go to `/admin`
2. Click "➕ Add New User"
3. Fill in user details
4. Click "Add User"

#### Register User Face
1. In admin panel, click "Register Face" for any user
2. Enter age and contact details
3. Capture face using camera
4. Face is automatically registered

### For Users

#### View Dashboard
1. Login to system
2. Automatically redirected to `/user-dashboard`
3. View face registration status and details

#### Test Face Recognition
1. Go to `/face-recognition`
2. Start camera
3. Capture image
4. See recognition results

## 🔧 API Endpoints

### Face Recognition
- `POST /api/face-recognize` - Recognize faces in uploaded image

### Admin Face Registration
- `GET /admin/register-face/<user_id>` - Admin face registration page
- `POST /api/admin/register-face` - Register user face

### User Dashboard
- `GET /user-dashboard` - User dashboard with face details

## 📊 Database Integration

The system uses two databases:
1. **Main database** (`users.db`) - User accounts and authentication
2. **Face database** (`face_recognition_system/people.db`) - Face recognition data

Users are linked via `user_id` field in the face database.

## 🎨 User Interface

### User Dashboard Features
- ✅ Account information display
- ✅ Face registration status
- ✅ Registered face details (age, contact)
- ✅ Navigation to other features
- ✅ Responsive design

### Admin Interface Features
- ✅ User management with face registration
- ✅ Camera-based face capture
- ✅ Real-time face detection
- ✅ Database integration

## 🔒 Security Features

- **Admin-only registration** - Only admins can register user faces
- **User isolation** - Users can only see their own face details
- **Secure storage** - Face images stored with unique filenames
- **Database validation** - Proper user ID linking

## 🧪 Testing

Run the test script to verify integration:
```bash
python test_face_recognition.py
```

## 📝 Notes

- Face recognition requires the `face_recognition` package
- Camera access is required for face registration
- Images are stored in `face_recognition_system/faces/`
- Database is automatically initialized on first use

## 🎉 Success Indicators

✅ **Face recognition integration working**
✅ **Admin can register user faces**
✅ **Users can view their face details**
✅ **Real-time recognition functional**
✅ **Database properly linked**
✅ **User workflow complete** 