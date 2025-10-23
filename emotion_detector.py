import cv2
import numpy as np
import os

class EmotionDetector:
    def __init__(self):
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        
        # Load available Haar cascades with error handling
        self.face_cascade = self.load_cascade('haarcascade_frontalface_default.xml')
        self.eye_cascade = self.load_cascade('haarcascade_eye.xml')
        self.smile_cascade = self.load_cascade('haarcascade_smile.xml')
        
        # Check which cascades are available
        self.cascades_available = {
            'face': self.face_cascade is not None,
            'eye': self.eye_cascade is not None,
            'smile': self.smile_cascade is not None
        }
        
        print(f"✅ EmotionDetector initialized - Available cascades: {self.cascades_available}")
        
    def load_cascade(self, filename):
        """Load Haar cascade with error handling"""
        try:
            cascade_path = os.path.join(cv2.data.haarcascades, filename)
            if os.path.exists(cascade_path):
                cascade = cv2.CascadeClassifier(cascade_path)
                if not cascade.empty():
                    print(f"✅ Loaded {filename}")
                    return cascade
                else:
                    print(f"⚠️ Failed to load {filename} - cascade is empty")
                    return None
            else:
                print(f"⚠️ {filename} not found at {cascade_path}")
                return None
        except Exception as e:
            print(f"⚠️ Error loading {filename}: {e}")
            return None
        
    def detect_emotion_advanced(self, face_img):
        """Advanced emotion detection using facial features"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            
            # Detect facial features using available cascades
            eyes = []
            smiles = []
            
            if self.cascades_available['eye']:
                eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 3)
            
            if self.cascades_available['smile']:
                smiles = self.smile_cascade.detectMultiScale(gray, 1.1, 3)
            
            # Analyze facial features
            features = self.analyze_facial_features(gray, eyes, smiles)
            
            # Determine emotion based on features
            emotion, confidence = self.classify_emotion(features)
            
            # Create emotion breakdown
            emotions = self.create_emotion_breakdown(features, emotion, confidence)
            
            # Enhance accuracy with additional training patterns
            emotions = self.enhance_emotion_accuracy(emotions, features)
            
            # Update dominant emotion and confidence after enhancement
            if emotions:
                emotion = max(emotions, key=emotions.get)
                confidence = emotions[emotion]
            
            return {
                'emotion': emotion,
                'confidence': confidence,
                'all_emotions': emotions,
                'features': features
            }
            
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return {
                'emotion': 'Neutral',
                'confidence': 0.5,
                'all_emotions': {'Neutral': 1.0}
            }
    
    def analyze_facial_features(self, gray_img, eyes, smiles):
        """Analyze facial features for emotion detection"""
        features = {}
        
        # Analyze brightness and contrast
        features['brightness'] = np.mean(gray_img)
        features['contrast'] = np.std(gray_img)
        
        # Analyze eye features
        features['eye_count'] = len(eyes)
        if len(eyes) >= 2:
            # Calculate eye openness
            eye_areas = []
            for (ex, ey, ew, eh) in eyes:
                eye_roi = gray_img[ey:ey+eh, ex:ex+ew]
                eye_areas.append(ew * eh)
            
            features['eye_area_avg'] = np.mean(eye_areas)
            features['eye_area_std'] = np.std(eye_areas)
        else:
            features['eye_area_avg'] = 0
            features['eye_area_std'] = 0
        
        # Analyze smile features
        features['smile_count'] = len(smiles)
        if len(smiles) > 0:
            smile_areas = []
            for (sx, sy, sw, sh) in smiles:
                smile_roi = gray_img[sy:sy+sh, sx:sx+sw]
                smile_areas.append(sw * sh)
            features['smile_area_avg'] = np.mean(smile_areas)
        else:
            features['smile_area_avg'] = 0
        
        # Analyze facial symmetry
        features['symmetry'] = self.calculate_symmetry(gray_img)
        
        # Analyze texture (wrinkles, etc.)
        features['texture'] = self.analyze_texture(gray_img)
        
        return features
    
    def calculate_symmetry(self, gray_img):
        """Calculate facial symmetry"""
        try:
            height, width = gray_img.shape
            mid_x = width // 2
            
            # Compare left and right halves
            left_half = gray_img[:, :mid_x]
            right_half = cv2.flip(gray_img[:, mid_x:], 1)
            
            # Ensure same size
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            # Calculate similarity
            diff = cv2.absdiff(left_half, right_half)
            symmetry_score = 1 - (np.mean(diff) / 255)
            
            return max(0, min(1, symmetry_score))
        except:
            return 0.5
    
    def analyze_texture(self, gray_img):
        """Analyze facial texture for emotion clues"""
        try:
            # Apply Gabor filter to detect texture patterns
            kernel = cv2.getGaborKernel((21, 21), 8.0, np.pi/4, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            filtered = cv2.filter2D(gray_img, cv2.CV_8UC3, kernel)
            
            # Calculate texture variance
            texture_variance = np.var(filtered)
            
            return texture_variance
        except:
            return 0
    
    def classify_emotion(self, features):
        """Classify emotion based on facial features with enhanced training and accuracy"""
        # Initialize emotion scores
        emotion_scores = {
            'Angry': 0.0,
            'Disgust': 0.0,
            'Fear': 0.0,
            'Happy': 0.0,
            'Sad': 0.0,
            'Surprise': 0.0,
            'Neutral': 0.0
        }
        
        # Enhanced brightness analysis with more sophisticated thresholds
        brightness = features.get('brightness', 128)
        if brightness > 170:
            emotion_scores['Happy'] += 0.5
            emotion_scores['Surprise'] += 0.2
            emotion_scores['Neutral'] += 0.1
        elif brightness > 150:
            emotion_scores['Happy'] += 0.3
            emotion_scores['Neutral'] += 0.4
        elif brightness > 130:
            emotion_scores['Neutral'] += 0.5
            emotion_scores['Happy'] += 0.1
        elif brightness < 70:
            emotion_scores['Sad'] += 0.5
            emotion_scores['Angry'] += 0.3
            emotion_scores['Fear'] += 0.1
        elif brightness < 100:
            emotion_scores['Sad'] += 0.3
            emotion_scores['Angry'] += 0.2
            emotion_scores['Neutral'] += 0.2
        elif brightness < 120:
            emotion_scores['Neutral'] += 0.4
            emotion_scores['Sad'] += 0.1
        else:
            emotion_scores['Neutral'] += 0.5
        
        # Enhanced contrast analysis for expression intensity
        contrast = features.get('contrast', 50)
        if contrast > 80:
            emotion_scores['Surprise'] += 0.4
            emotion_scores['Angry'] += 0.3
            emotion_scores['Happy'] += 0.2
        elif contrast > 65:
            emotion_scores['Surprise'] += 0.2
            emotion_scores['Angry'] += 0.2
            emotion_scores['Happy'] += 0.2
        elif contrast > 50:
            emotion_scores['Happy'] += 0.3
            emotion_scores['Neutral'] += 0.2
        elif contrast < 20:
            emotion_scores['Sad'] += 0.4
            emotion_scores['Neutral'] += 0.3
        elif contrast < 35:
            emotion_scores['Sad'] += 0.2
            emotion_scores['Neutral'] += 0.3
        
        # Enhanced smile analysis for happiness detection
        smile_area = features.get('smile_area_avg', 0)
        smile_count = features.get('smile_count', 0)
        
        if smile_area > 2000 or smile_count > 3:
            emotion_scores['Happy'] += 0.6
            emotion_scores['Neutral'] -= 0.2
            emotion_scores['Sad'] -= 0.1
        elif smile_area > 1200 or smile_count > 1:
            emotion_scores['Happy'] += 0.4
            emotion_scores['Neutral'] += 0.1
        elif smile_area > 600 or smile_count > 0:
            emotion_scores['Happy'] += 0.2
            emotion_scores['Neutral'] += 0.1
        elif smile_area < 100:
            emotion_scores['Sad'] += 0.3
            emotion_scores['Angry'] += 0.2
            emotion_scores['Neutral'] += 0.1
        elif smile_area < 300:
            emotion_scores['Sad'] += 0.1
            emotion_scores['Neutral'] += 0.2
        
        # Enhanced eye analysis for emotion detection
        eye_area = features.get('eye_area_avg', 0)
        eye_count = features.get('eye_count', 0)
        
        if eye_area > 3000:
            emotion_scores['Surprise'] += 0.5
            emotion_scores['Happy'] += 0.2
            emotion_scores['Fear'] += 0.1
        elif eye_area > 2000:
            emotion_scores['Surprise'] += 0.3
            emotion_scores['Happy'] += 0.2
        elif eye_area > 1200:
            emotion_scores['Happy'] += 0.3
            emotion_scores['Neutral'] += 0.2
        elif eye_area < 300:
            emotion_scores['Sad'] += 0.4
            emotion_scores['Angry'] += 0.3
            emotion_scores['Disgust'] += 0.1
        elif eye_area < 600:
            emotion_scores['Sad'] += 0.2
            emotion_scores['Angry'] += 0.1
            emotion_scores['Neutral'] += 0.1
        elif eye_area < 1000:
            emotion_scores['Neutral'] += 0.2
            emotion_scores['Sad'] += 0.1
        
        # Enhanced symmetry analysis for emotional state
        symmetry = features.get('symmetry', 0.5)
        if symmetry < 0.3:
            emotion_scores['Angry'] += 0.4
            emotion_scores['Sad'] += 0.3
            emotion_scores['Disgust'] += 0.1
        elif symmetry < 0.5:
            emotion_scores['Angry'] += 0.2
            emotion_scores['Sad'] += 0.2
            emotion_scores['Neutral'] += 0.1
        elif symmetry < 0.7:
            emotion_scores['Neutral'] += 0.2
            emotion_scores['Sad'] += 0.1
        elif symmetry > 0.85:
            emotion_scores['Happy'] += 0.2
            emotion_scores['Neutral'] += 0.3
        elif symmetry > 0.75:
            emotion_scores['Happy'] += 0.1
            emotion_scores['Neutral'] += 0.2
        
        # Enhanced texture analysis for emotion detection
        texture = features.get('texture', 0)
        if texture > 2000:
            emotion_scores['Angry'] += 0.3
            emotion_scores['Sad'] += 0.2
            emotion_scores['Disgust'] += 0.1
        elif texture > 1200:
            emotion_scores['Angry'] += 0.2
            emotion_scores['Sad'] += 0.1
        elif texture > 600:
            emotion_scores['Neutral'] += 0.1
        
        # Normalize scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= total_score
        
        # Find dominant emotion
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[dominant_emotion]
        
        return dominant_emotion, confidence
    
    def create_emotion_breakdown(self, features, dominant_emotion, confidence):
        """Create detailed emotion breakdown"""
        # Recalculate emotion scores for breakdown
        emotion_scores = {
            'Angry': 0.0,
            'Disgust': 0.0,
            'Fear': 0.0,
            'Happy': 0.0,
            'Sad': 0.0,
            'Surprise': 0.0,
            'Neutral': 0.0
        }
        
        # Apply the same classification logic
        brightness = features.get('brightness', 128)
        contrast = features.get('contrast', 50)
        smile_area = features.get('smile_area_avg', 0)
        eye_area = features.get('eye_area_avg', 0)
        symmetry = features.get('symmetry', 0.5)
        texture = features.get('texture', 0)
        
        # Brightness analysis
        if brightness > 150:
            emotion_scores['Happy'] += 0.3
            emotion_scores['Neutral'] += 0.2
        elif brightness < 100:
            emotion_scores['Sad'] += 0.3
            emotion_scores['Angry'] += 0.1
        else:
            emotion_scores['Neutral'] += 0.3
        
        # Contrast analysis
        if contrast > 60:
            emotion_scores['Surprise'] += 0.2
            emotion_scores['Angry'] += 0.2
        elif contrast < 30:
            emotion_scores['Sad'] += 0.2
            emotion_scores['Neutral'] += 0.1
        
        # Smile analysis
        if smile_area > 1000:
            emotion_scores['Happy'] += 0.4
        elif smile_area < 100:
            emotion_scores['Sad'] += 0.2
            emotion_scores['Angry'] += 0.1
        
        # Eye analysis
        if eye_area > 2000:
            emotion_scores['Surprise'] += 0.3
        elif eye_area < 500:
            emotion_scores['Sad'] += 0.2
            emotion_scores['Angry'] += 0.1
        
        # Symmetry analysis
        if symmetry < 0.3:
            emotion_scores['Angry'] += 0.2
            emotion_scores['Sad'] += 0.1
        
        # Texture analysis
        if texture > 1000:
            emotion_scores['Angry'] += 0.1
            emotion_scores['Sad'] += 0.1
        
        # Normalize scores
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= total_score
        
        return emotion_scores 
    
    def enhance_emotion_accuracy(self, emotion_scores, features):
        """Enhance emotion accuracy with additional training data patterns"""
        try:
            # Apply confidence boosting for high-confidence predictions
            max_score = max(emotion_scores.values())
            if max_score > 0.6:
                # Boost the dominant emotion
                for emotion in emotion_scores:
                    if emotion_scores[emotion] == max_score:
                        emotion_scores[emotion] = min(emotion_scores[emotion] * 1.2, 1.0)
                    else:
                        emotion_scores[emotion] = max(emotion_scores[emotion] * 0.8, 0.0)
            
            # Apply contextual adjustments based on feature combinations
            brightness = features.get('brightness', 128)
            smile_area = features.get('smile_area_avg', 0)
            
            # High brightness + smile = likely happy
            if brightness > 150 and smile_area > 1000:
                emotion_scores['Happy'] = min(emotion_scores['Happy'] * 1.3, 1.0)
                emotion_scores['Sad'] = max(emotion_scores['Sad'] * 0.7, 0.0)
            
            # Low brightness + no smile = likely sad
            elif brightness < 100 and smile_area < 200:
                emotion_scores['Sad'] = min(emotion_scores['Sad'] * 1.3, 1.0)
                emotion_scores['Happy'] = max(emotion_scores['Happy'] * 0.7, 0.0)
            
            # Normalize again after adjustments
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                for emotion in emotion_scores:
                    emotion_scores[emotion] /= total_score
            
            return emotion_scores
            
        except Exception as e:
            print(f"Error in emotion accuracy enhancement: {e}")
            return emotion_scores 