# A Gender and Age Detection program by Mahesh Sawant

import cv2
import argparse

print(cv2.__version__)
print(dir(cv2.dnn))

def highlightFace(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    faceBoxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            faceBoxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    return frameOpencvDnn, faceBoxes

# Parse argument
parser = argparse.ArgumentParser()
parser.add_argument('--image', help='Path to image or video file')
args = parser.parse_args()

# Load models
<<<<<<< HEAD
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

faceProto = os.path.join(script_dir, "opencv_face_detector.pbtxt")
faceModel = os.path.join(script_dir, "opencv_face_detector_uint8.pb")
ageProto = os.path.join(script_dir, "age_deploy.prototxt")
ageModel = os.path.join(script_dir, "age_net.caffemodel")
genderProto = os.path.join(script_dir, "gender_deploy.prototxt")
genderModel = os.path.join(script_dir, "gender_net.caffemodel")

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
=======
faceProto = "opencv_face_detector.pbtxt"
faceModel = "opencv_face_detector_uint8.pb"
ageProto = "age_deploy.prototxt"
ageModel = "age_net.caffemodel"
genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(20-25)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
>>>>>>> a8a36cb1c8a89472d874daa0bf4ce03cfbef9114
genderList = ['Male', 'Female']

faceNet = cv2.dnn.readNet(faceModel, faceProto)
ageNet = cv2.dnn.readNet(ageModel, ageProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)

# Capture video or image
video = cv2.VideoCapture(args.image if args.image else 0)
padding = 20

# Run detection once (remove loop for image mode)
hasFrame, frame = video.read()
if not hasFrame:
    print("No frame captured.")
    exit()

resultImg, faceBoxes = highlightFace(faceNet, frame)

if not faceBoxes:
    print("No face detected")
else:
    for faceBox in faceBoxes:
        face = frame[max(0, faceBox[1]-padding):min(faceBox[3]+padding, frame.shape[0]-1),
                     max(0, faceBox[0]-padding):min(faceBox[2]+padding, frame.shape[1]-1)]

        blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

        genderNet.setInput(blob)
        genderPreds = genderNet.forward()
        gender = genderList[genderPreds[0].argmax()]

        ageNet.setInput(blob)
        agePreds = ageNet.forward()
        age = ageList[agePreds[0].argmax()]

        print(f"Gender: {gender}")
        print(f"Age: {age[1:-1]} years")

        # Draw label on image
        label = f'{gender}, {age}'
        cv2.putText(resultImg, label, (faceBox[0], faceBox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

# Save final annotated image
success = cv2.imwrite("output.jpg", resultImg)
if success:
    print("✅ Result saved to output.jpg")
else:
    print("❌ Failed to save image.")
