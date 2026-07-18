"""OpenCV-compatible fallback for the external ``face_recognition`` package.

It supports the subset used by this application when dlib is not installed.
It is intended for local demos, not production biometric authentication.
"""
import cv2
import numpy as np

_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def load_image_file(file):
    image = cv2.imread(str(file))
    if image is None:
        raise ValueError("Unable to load image")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def face_locations(image, number_of_times_to_upsample=1, model="hog"):
    if image is None:
        return []
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if image.ndim == 3 else image
    scale = 1.05 if number_of_times_to_upsample > 1 else 1.1
    faces = _FACE_CASCADE.detectMultiScale(gray, scaleFactor=scale,
                                           minNeighbors=5, minSize=(48, 48))
    return [(int(y), int(x + w), int(y + h), int(x)) for x, y, w, h in faces]


def face_encodings(face_image, known_face_locations=None, num_jitters=1, model="small"):
    locations = known_face_locations if known_face_locations is not None else face_locations(face_image)
    encodings = []
    for top, right, bottom, left in locations:
        crop = face_image[max(0, top):max(0, bottom), max(0, left):max(0, right)]
        if crop.size == 0:
            continue
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if crop.ndim == 3 else crop
        gray = cv2.equalizeHist(cv2.resize(gray, (64, 64)))
        descriptor = gray.astype(np.float32).reshape(-1)
        descriptor -= descriptor.mean()
        norm = np.linalg.norm(descriptor)
        if norm:
            descriptor /= norm
        encodings.append(descriptor)
    return encodings


def face_distance(face_encodings, face_to_compare):
    if not face_encodings:
        return np.array([])
    comparisons = np.asarray(face_encodings, dtype=np.float32)
    target = np.asarray(face_to_compare, dtype=np.float32)
    cosine = np.clip(comparisons @ target, -1.0, 1.0)
    return 1.0 - cosine


def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)
