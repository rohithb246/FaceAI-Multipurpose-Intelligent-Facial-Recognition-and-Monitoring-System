# Face Recognition System

A Python-based face recognition system with GUI interface that can register new people and recognize them in real-time using your computer's camera.

## Features

- **Face Registration**: Capture and register new people with their details (name, age, phone)
- **Real-time Recognition**: Recognize registered people in real-time using webcam
- **User-friendly GUI**: Simple and intuitive graphical interface
- **Database Storage**: SQLite database to store person details and face images
- **Face Detection**: Automatic face detection during registration and recognition
- **Error Handling**: Comprehensive error handling and user feedback

## Requirements

- Python 3.7 or higher
- Webcam
- Good lighting conditions for better face detection

## Installation

1. **Clone or download this project**

2. **Install required dependencies**:
   ```bash
   pip install opencv-python
   pip install face-recognition
   pip install numpy
   ```

3. **Run the test script to verify everything is working**:
   ```bash
   python test_system.py
   ```

## Usage

### Starting the Application

Run the main GUI application:
```bash
python app_gui.py
```

### How to Use

1. **Register New Person**:
   - Click "Register New Person" button
   - Enter the person's details (name, age, phone)
   - Position the person's face in front of the camera
   - Wait for face detection (green rectangle will appear)
   - Press 's' to capture the face
   - The system will save the image and store the details

2. **Start Recognition**:
   - Click "Start Recognition" button
   - The camera will open and start detecting faces
   - Recognized people will be shown with their details
   - Unknown faces will be marked as "Unknown"
   - Press 'q' to quit recognition

3. **View Registered People**:
   - Click "View Registered People" to see all registered individuals
   - This shows names, ages, phone numbers, and image paths

## File Structure

```
face_recognition_system/
├── app_gui.py          # Main GUI application
├── main.py             # Face recognition logic
├── capture_face.py     # Face capture and registration
├── db_manager.py       # Database operations
├── test_system.py      # System testing script
├── people.db           # SQLite database
├── faces/              # Directory for stored face images
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Camera not working**:
   - Check if your webcam is connected and working
   - Ensure no other application is using the camera
   - Check camera permissions in your operating system

2. **Face not detected**:
   - Ensure good lighting conditions
   - Position face clearly in front of the camera
   - Make sure face is not too close or too far from camera

3. **Recognition not working**:
   - Make sure you have registered people first
   - Check that face images were saved properly in the `faces/` directory
   - Try registering the person again with better lighting

4. **Dependencies not found**:
   - Run: `pip install opencv-python face-recognition numpy`
   - On Windows, you might need: `pip install cmake` before installing face-recognition

### Performance Tips

- Use good lighting for better face detection
- Keep faces at a reasonable distance from the camera
- Register multiple images of the same person for better recognition
- Close other applications using the camera

## Technical Details

- **Face Detection**: Uses the `face_recognition` library with HOG (Histogram of Oriented Gradients) model
- **Face Recognition**: Uses face encodings with a tolerance of 0.6 for matching
- **Database**: SQLite database with table structure for storing person details
- **GUI**: Tkinter-based interface with threading for non-blocking operations
- **Image Processing**: OpenCV for camera operations and image handling

## Security Notes

- Face images are stored locally on your computer
- The system does not transmit any data over the internet
- Consider the privacy implications of storing face images

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues:
1. Run the test script: `python test_system.py`
2. Check the troubleshooting section above
3. Ensure all dependencies are properly installed
4. Verify your camera is working with other applications 