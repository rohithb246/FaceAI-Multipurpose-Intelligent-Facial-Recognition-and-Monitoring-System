#!/usr/bin/env python3
"""
Enhanced Face Recognition System
Solves similar face misclassification issues with:
- Adaptive thresholds
- Confidence scoring
- Multi-factor analysis
- Better model handling
"""

import face_recognition as fr
import numpy as np
import cv2
from typing import List, Tuple, Dict, Optional
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFaceRecognition:
    """
    Enhanced face recognition system with adaptive thresholds and confidence scoring
    """
    
    def __init__(self, base_tolerance: float = 0.6, confidence_threshold: float = 0.7):
        self.base_tolerance = base_tolerance
        self.confidence_threshold = confidence_threshold
        self.recognition_history = {}
        self.face_quality_cache = {}
        
        # Adaptive threshold parameters - balanced (previous working set)
        self.low_confidence_threshold = 0.25
        self.medium_confidence_threshold = 0.45
        self.high_confidence_threshold = 0.65
        
        # Multi-factor weights - balanced
        self.distance_weight = 0.35
        self.similarity_weight = 0.35
        self.quality_weight = 0.2
        self.historical_weight = 0.1
        
        # Similar face detection parameters - balanced
        self.similar_face_threshold = 0.7
        self.similar_face_boost = 1.3
        
        # Live recognition specific parameters - disabled by default
        self.live_recognition_mode = False
        self.live_tolerance_boost = 1.0
        self.live_confidence_boost = 1.0
        
    def assess_image_quality(self, image) -> float:
        """
        Assess image quality for face recognition
        Returns quality score from 0.0 to 1.0
        """
        try:
            # Convert to grayscale for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Factor 1: Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 500.0, 1.0)  # Normalize to 0-1
            
            # Factor 2: Brightness (histogram analysis)
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 128) / 128  # Optimal around 128
            
            # Factor 3: Contrast (standard deviation)
            contrast = np.std(gray)
            contrast_score = min(contrast / 50.0, 1.0)  # Normalize to 0-1
            
            # Factor 4: Face size (larger faces are better)
            face_locations = fr.face_locations(image)
            if face_locations:
                # Calculate face area
                top, right, bottom, left = face_locations[0]
                face_area = (right - left) * (bottom - top)
                image_area = image.shape[0] * image.shape[1]
                size_score = min(face_area / (image_area * 0.1), 1.0)  # Optimal if face is 10% of image
            else:
                size_score = 0.0
            
            # Weighted quality score
            quality_score = (
                0.3 * sharpness_score +
                0.25 * brightness_score +
                0.25 * contrast_score +
                0.2 * size_score
            )
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.warning(f"Error assessing image quality: {e}")
            return 0.5  # Default medium quality
    
    def calculate_adaptive_threshold(self, image_quality: float, lighting_condition: str = "normal") -> float:
        """
        Calculate adaptive threshold based on image quality and conditions
        Balanced (previous working set) with mild relaxation
        """
        # Base threshold adjustments - balanced
        if image_quality > 0.8:
            quality_multiplier = 0.9
        elif image_quality > 0.6:
            quality_multiplier = 1.0
        else:
            quality_multiplier = 1.15
        
        # Lighting condition adjustments - balanced
        lighting_multipliers = {
            "bright": 1.0,
            "normal": 1.05,
            "dim": 1.15,
            "mixed": 1.2
        }
        
        lighting_multiplier = lighting_multipliers.get(lighting_condition, 1.05)
        
        # Apply live recognition boost if enabled
        if self.live_recognition_mode:
            live_boost = self.live_tolerance_boost
        else:
            live_boost = 1.0
        
        # Calculate adaptive threshold
        adaptive_threshold = self.base_tolerance * quality_multiplier * lighting_multiplier * live_boost
        
        # Ensure threshold stays within reasonable bounds - balanced
        return max(0.45, min(0.9, adaptive_threshold))
    
    def calculate_face_similarity(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two face encodings
        Returns similarity score from -1 to 1 (higher is more similar)
        """
        try:
            # Normalize encodings
            norm1 = np.linalg.norm(encoding1)
            norm2 = np.linalg.norm(encoding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(encoding1, encoding2) / (norm1 * norm2)
            return similarity
            
        except Exception as e:
            logger.warning(f"Error calculating face similarity: {e}")
            return 0.0
    
    def get_historical_accuracy(self, person_id: int) -> float:
        """
        Get historical recognition accuracy for a person
        Returns accuracy score from 0.0 to 1.0
        """
        # Ensure person_id is a Python int
        person_id = int(person_id)
        
        if person_id not in self.recognition_history:
            return 0.5  # Default medium accuracy
        
        history = self.recognition_history[person_id]
        if not history:
            return 0.5
        
        # Calculate success rate from recent recognitions
        recent_history = history[-10:]  # Last 10 attempts
        success_count = sum(1 for attempt in recent_history if attempt['success'])
        return float(success_count / len(recent_history))  # Ensure return is Python float
    
    def update_recognition_history(self, person_id: int, success: bool, confidence: float):
        """
        Update recognition history for learning
        """
        # Ensure person_id is a Python int
        person_id = int(person_id)
        
        if person_id not in self.recognition_history:
            self.recognition_history[person_id] = []
        
        self.recognition_history[person_id].append({
            'timestamp': datetime.now(),
            'success': success,
            'confidence': float(confidence)  # Ensure confidence is Python float
        })
        
        # Keep only last 50 attempts
        if len(self.recognition_history[person_id]) > 50:
            self.recognition_history[person_id] = self.recognition_history[person_id][-50:]
    
    def recognize_face_enhanced(self, 
                              known_encodings: List[np.ndarray], 
                              face_encoding: np.ndarray,
                              known_names: List[str],
                              image_quality: float = None) -> Tuple[str, float, str, Dict]:
        """
        Enhanced face recognition with multi-stage approach for better similar face handling
        
        Returns:
        - recognized_name: Name of recognized person or "Unknown"
        - confidence_score: Confidence score from 0.0 to 1.0
        - confidence_level: "high", "medium", "low", or "unknown"
        - details: Additional recognition details
        """
        try:
            if not known_encodings or len(known_encodings) == 0:
                return "Unknown", 0.0, "unknown", {"reason": "No known faces in database"}
            
            # Assess image quality if not provided
            if image_quality is None:
                image_quality = 0.7  # Default medium quality
            
            # Stage 1: Calculate distances and find initial candidates
            distances = fr.face_distance(known_encodings, face_encoding)
            min_distance_idx = np.argmin(distances)
            min_distance = distances[min_distance_idx]
            
            # Stage 2: Multi-threshold approach for similar faces
            # Primary threshold (more lenient)
            primary_threshold = self.calculate_adaptive_threshold(image_quality)
            
            # Secondary threshold (even more lenient for similar faces)
            secondary_threshold = primary_threshold * 1.2
            
            # Find candidates using both thresholds
            primary_candidates = distances < primary_threshold
            secondary_candidates = distances < secondary_threshold
            
            # Stage 3: Enhanced candidate selection
            if any(primary_candidates):
                # Use primary candidates (high confidence)
                candidate_indices = np.where(primary_candidates)[0]
                threshold_used = "primary"
            elif any(secondary_candidates):
                # Use secondary candidates (lower confidence but still valid)
                candidate_indices = np.where(secondary_candidates)[0]
                threshold_used = "secondary"
                # Apply similarity boost for secondary candidates
                logger.info(f"Using secondary threshold for similar face detection")
            else:
                # No candidates found - check if we have a very close match
                if min_distance < (secondary_threshold * 1.1):
                    # Very close match - might be a similar face
                    candidate_indices = np.array([min_distance_idx])
                    threshold_used = "similar_face"
                    logger.info(f"Very close match detected - treating as similar face")
                else:
                    return "Unknown", 0.0, "unknown", {
                        "reason": f"All faces exceed thresholds (primary: {primary_threshold:.3f}, secondary: {secondary_threshold:.3f})",
                        "min_distance": float(min_distance)
                    }
            
            # Stage 4: Enhanced confidence scoring with similarity detection
            candidate_encodings = [known_encodings[i] for i in candidate_indices]
            candidate_names = [known_names[i] for i in candidate_indices]
            candidate_distances = [distances[i] for i in candidate_indices]
            
            confidence_scores = []
            similarity_scores = []
            
            for i, idx in enumerate(candidate_indices):
                # Calculate base confidence
                base_score = self.calculate_confidence_score(
                    candidate_encodings[i],
                    face_encoding,
                    candidate_distances[i],
                    image_quality,
                    int(idx)
                )
                
                # Calculate similarity score
                similarity = self.calculate_face_similarity(candidate_encodings[i], face_encoding)
                similarity_scores.append(similarity)
                
                # Apply similarity boost for similar faces
                if similarity > self.similar_face_threshold:
                    similarity_boost = self.similar_face_boost
                    logger.info(f"Similar face detected for {candidate_names[i]} - applying boost")
                else:
                    similarity_boost = 1.0
                
                # Apply threshold-based adjustments
                if threshold_used == "secondary":
                    threshold_boost = 0.9  # Slight penalty for secondary threshold
                elif threshold_used == "similar_face":
                    threshold_boost = 0.95  # Very slight penalty for similar face threshold
                else:
                    threshold_boost = 1.0
                
                # Apply live recognition confidence boost if enabled
                if self.live_recognition_mode:
                    live_confidence_boost = self.live_confidence_boost
                else:
                    live_confidence_boost = 1.0
                
                # Final confidence score
                final_score = base_score * similarity_boost * threshold_boost * live_confidence_boost
                confidence_scores.append(final_score)
            
            # Stage 5: Enhanced best match selection
            best_match_idx = np.argmax(confidence_scores)
            best_confidence = confidence_scores[best_match_idx]
            best_name = candidate_names[best_match_idx]
            best_distance = candidate_distances[best_match_idx]
            best_similarity = similarity_scores[best_match_idx]
            
            # Stage 6: Confidence level determination with similarity consideration
            if best_confidence > 0.75:
                confidence_level = "high"
            elif best_confidence > 0.55:
                confidence_level = "medium"
            else:
                confidence_level = "low"
            
            # Stage 7: Update recognition history
            person_id = int(candidate_indices[best_match_idx])
            self.update_recognition_history(person_id, True, best_confidence)
            
            # Stage 8: Prepare detailed response
            details = {
                "distance": float(best_distance),
                "similarity": float(best_similarity),
                "primary_threshold": float(primary_threshold),
                "secondary_threshold": float(secondary_threshold),
                "threshold_used": threshold_used,
                "image_quality": float(image_quality),
                "confidence_level": confidence_level,
                "candidates_considered": int(len(candidate_indices)),
                "all_distances": [float(d) for d in candidate_distances],
                "all_confidences": [float(s) for s in confidence_scores],
                "all_similarities": [float(s) for s in similarity_scores],
                "recognition_method": "enhanced_multi_stage"
            }
            
            logger.info(f"Recognized: {best_name} with confidence {best_confidence:.3f} ({confidence_level}) using {threshold_used} threshold")
            return best_name, best_confidence, confidence_level, details
            
        except Exception as e:
            logger.error(f"Error in enhanced face recognition: {e}")
            return "Unknown", 0.0, "unknown", {"error": str(e)}
    
    def calculate_confidence_score(self, 
                                 candidate_encoding: np.ndarray,
                                 face_encoding: np.ndarray,
                                 distance: float,
                                 image_quality: float,
                                 person_id: int) -> float:
        """
        Calculate comprehensive confidence score using multiple factors
        Enhanced for similar face detection
        """
        try:
            # Factor 1: Distance-based score (35% weight)
            # More lenient distance scoring for similar faces
            normalized_distance = distance / self.base_tolerance
            if normalized_distance < 1.0:
                distance_score = 1.0 - normalized_distance
            else:
                # For distances beyond threshold, use exponential decay
                distance_score = max(0.0, np.exp(-2.0 * (normalized_distance - 1.0)))
            
            distance_score = max(0.0, min(1.0, distance_score))
            
            # Factor 2: Cosine similarity (35% weight) - enhanced for similar faces
            similarity = self.calculate_face_similarity(candidate_encoding, face_encoding)
            # Enhanced similarity scoring with better handling of similar faces
            if similarity > 0.8:
                # High similarity - boost the score
                similarity_score = 0.8 + (similarity - 0.8) * 2.0  # Boost high similarities
            else:
                similarity_score = (similarity + 1.0) / 2.0  # Standard conversion
            
            similarity_score = max(0.0, min(1.0, similarity_score))
            
            # Factor 3: Image quality (20% weight)
            quality_score = image_quality
            
            # Factor 4: Historical accuracy (10% weight)
            historical_score = self.get_historical_accuracy(person_id)
            
            # Enhanced weighted combination with similarity boost
            base_score = (
                self.distance_weight * distance_score +
                self.similarity_weight * similarity_score +
                self.quality_weight * quality_score +
                self.historical_weight * historical_score
            )
            
            # Apply similarity boost for very similar faces
            if similarity > 0.9:
                similarity_boost = 1.1  # 10% boost for very similar faces
                logger.info(f"Applying similarity boost for very similar face (similarity: {similarity:.3f})")
            elif similarity > 0.8:
                similarity_boost = 1.05  # 5% boost for similar faces
            else:
                similarity_boost = 1.0
            
            final_score = base_score * similarity_boost
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.warning(f"Error calculating confidence score: {e}")
            return 0.5
    
    def compare_faces_enhanced(self, 
                              known_encodings: List[np.ndarray],
                              face_encoding: np.ndarray,
                              tolerance: float = None) -> List[bool]:
        """
        Enhanced face comparison with better threshold handling
        """
        if tolerance is None:
            tolerance = self.base_tolerance
        
        distances = fr.face_distance(known_encodings, face_encoding)
        return distances <= tolerance
    
    def detect_similar_faces(self, 
                           known_encodings: List[np.ndarray],
                           face_encoding: np.ndarray,
                           similarity_threshold: float = None) -> List[Tuple[int, float]]:
        """
        Detect similar faces using cosine similarity
        Returns list of (index, similarity_score) tuples
        """
        if similarity_threshold is None:
            similarity_threshold = self.similar_face_threshold
        
        similar_faces = []
        
        for i, known_encoding in enumerate(known_encodings):
            similarity = self.calculate_face_similarity(known_encoding, face_encoding)
            if similarity > similarity_threshold:
                similar_faces.append((i, similarity))
        
        # Sort by similarity (highest first)
        similar_faces.sort(key=lambda x: x[1], reverse=True)
        return similar_faces
    
    def analyze_face_similarity_distribution(self, 
                                          known_encodings: List[np.ndarray],
                                          face_encoding: np.ndarray) -> Dict:
        """
        Analyze the distribution of face similarities for better understanding
        """
        similarities = []
        for known_encoding in known_encodings:
            similarity = self.calculate_face_similarity(known_encoding, face_encoding)
            similarities.append(similarity)
        
        similarities = np.array(similarities)
        
        return {
            "mean_similarity": float(np.mean(similarities)),
            "std_similarity": float(np.std(similarities)),
            "max_similarity": float(np.max(similarities)),
            "min_similarity": float(np.min(similarities)),
            "similarity_range": float(np.max(similarities) - np.min(similarities)),
            "high_similarity_count": int(np.sum(similarities > 0.8)),
            "medium_similarity_count": int(np.sum((similarities > 0.6) & (similarities <= 0.8))),
            "low_similarity_count": int(np.sum(similarities <= 0.6))
        }
    
    def get_recognition_statistics(self) -> Dict:
        """
        Get statistics about recognition performance
        """
        stats = {
            "total_recognitions": 0,
            "successful_recognitions": 0,
            "average_confidence": 0.0,
            "person_accuracy": {},
            "threshold_usage": {
                "low": 0,
                "medium": 0,
                "high": 0
            }
        }
        
        total_confidence = 0.0
        recognition_count = 0
        
        for person_id, history in self.recognition_history.items():
            if not history:
                continue
            
            person_stats = {
                "total_attempts": len(history),
                "successful_attempts": sum(1 for h in history if h['success']),
                "average_confidence": float(np.mean([h['confidence'] for h in history]))  # Convert numpy float to Python float
            }
            
            stats["person_accuracy"][int(person_id)] = person_stats  # Ensure person_id is Python int
            stats["total_recognitions"] += person_stats["total_attempts"]
            stats["successful_recognitions"] += person_stats["successful_attempts"]
            
            for attempt in history:
                total_confidence += attempt['confidence']
                recognition_count += 1
        
        if recognition_count > 0:
            stats["average_confidence"] = float(total_confidence / recognition_count)  # Ensure it's Python float
        
        # Ensure all values are Python types
        stats["total_recognitions"] = int(stats["total_recognitions"])
        stats["successful_recognitions"] = int(stats["successful_recognitions"])
        
        return stats
    
    def tune_for_similar_faces(self, enable: bool = True):
        """
        Tune the system specifically for better similar face recognition (balanced previous working set)
        """
        if enable:
            # Balanced parameters (previous working set)
            self.base_tolerance = 0.65
            self.similar_face_threshold = 0.7
            self.similar_face_boost = 1.3
            
            self.low_confidence_threshold = 0.25
            self.medium_confidence_threshold = 0.45
            self.high_confidence_threshold = 0.65
            
            self.distance_weight = 0.35
            self.similarity_weight = 0.35
            self.quality_weight = 0.2
            self.historical_weight = 0.1
            
            # Disable live recognition extra boosts for stability
            self.live_recognition_mode = False
            self.live_tolerance_boost = 1.0
            self.live_confidence_boost = 1.0
            
            logger.info("System tuned for similar face recognition (balanced)")
        else:
            # Reset to default parameters
            self.base_tolerance = 0.6
            self.similar_face_threshold = 0.75
            self.similar_face_boost = 1.2
            
            self.low_confidence_threshold = 0.3
            self.medium_confidence_threshold = 0.5
            self.high_confidence_threshold = 0.7
            
            self.distance_weight = 0.35
            self.similarity_weight = 0.35
            self.quality_weight = 0.2
            self.historical_weight = 0.1
            
            logger.info("System reset to default parameters")

# Global instance
enhanced_face_recognition = EnhancedFaceRecognition() 