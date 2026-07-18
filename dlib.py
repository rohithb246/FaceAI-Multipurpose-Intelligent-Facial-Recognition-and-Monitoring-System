"""Portable subset of dlib used by this project.

The original dlib package has no ready-to-install Python 3.12 Windows wheel
and requires Visual C++ to compile.  This OpenCV-backed compatibility layer
keeps the driver-monitoring page functional using face and eye cascades.
"""
import cv2
import numpy as np

_CASCADE_DIR = cv2.data.haarcascades
_FACES = cv2.CascadeClassifier(_CASCADE_DIR + "haarcascade_frontalface_default.xml")
_EYES = cv2.CascadeClassifier(_CASCADE_DIR + "haarcascade_eye_tree_eyeglasses.xml")


class _Rectangle:
    def __init__(self, x, y, width, height):
        self._x, self._y, self._width, self._height = map(int, (x, y, width, height))

    def left(self): return self._x
    def top(self): return self._y
    def width(self): return self._width
    def height(self): return self._height


class _Point:
    def __init__(self, x, y):
        self.x, self.y = int(x), int(y)


class _Shape:
    def __init__(self, points):
        self._points = points

    def part(self, index):
        return self._points[index]


def get_frontal_face_detector():
    def detect(gray):
        faces = _FACES.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                        minSize=(80, 80))
        return [_Rectangle(x, y, w, h) for x, y, w, h in faces]
    return detect


class _ShapePredictor:
    def __call__(self, gray, face):
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        upper = gray[y:y + h // 2, x:x + w]
        eyes = _EYES.detectMultiScale(upper, scaleFactor=1.1, minNeighbors=4,
                                      minSize=(18, 12))
        eye_boxes = sorted(eyes, key=lambda item: item[0])[:2]
        open_eyes = len(eye_boxes) == 2
        if len(eye_boxes) == 2:
            centers = [(x + ex + ew / 2, y + ey + eh / 2, ew, eh)
                       for ex, ey, ew, eh in eye_boxes]
        else:
            centers = [(x + w * .32, y + h * .40, w * .22, h * .10),
                       (x + w * .68, y + h * .40, w * .22, h * .10)]

        points = [_Point(x + w / 2, y + h / 2) for _ in range(68)]
        for start, (cx, cy, ew, eh) in zip((36, 42), centers):
            half_w = max(4, ew * .45)
            half_h = max(1, eh * (.24 if open_eyes else .02))
            eye = [(cx - half_w, cy), (cx - half_w / 2, cy - half_h),
                   (cx + half_w / 2, cy - half_h), (cx + half_w, cy),
                   (cx + half_w / 2, cy + half_h), (cx - half_w / 2, cy + half_h)]
            for index, point in enumerate(eye):
                points[start + index] = _Point(*point)
        return _Shape(points)


def shape_predictor(_model_path):
    return _ShapePredictor()
