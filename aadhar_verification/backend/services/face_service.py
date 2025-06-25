import cv2
import numpy as np
from deepface import DeepFace
from typing import Dict, Any, Optional, Tuple
from config import Config
import os

class FaceService:
    def __init__(self):
        self.config = Config()
    
    def verify_faces(self, aadhaar_path: str, selfie_path: str) -> Dict[str, Any]:
        """Verify if faces in Aadhaar and selfie match"""
        try:
            # Check if both images have detectable faces
            aadhaar_faces = self._detect_faces(aadhaar_path)
            selfie_faces = self._detect_faces(selfie_path)
            
            if not aadhaar_faces['face_detected']:
                return {
                    'verified': False,
                    'confidence': 0,
                    'distance': 1.0,
                    'error': 'No face detected in Aadhaar image'
                }
            
            if not selfie_faces['face_detected']:
                return {
                    'verified': False,
                    'confidence': 0,
                    'distance': 1.0,
                    'error': 'No face detected in selfie image'
                }
            
            # Perform face verification using DeepFace
            result = DeepFace.verify(
                img1_path=aadhaar_path,
                img2_path=selfie_path,
                model_name=self.config.FACE_VERIFICATION_MODEL,
                distance_metric=self.config.FACE_VERIFICATION_DISTANCE_METRIC,
                enforce_detection=True
            )
            
            return {
                'verified': result['verified'],
                'confidence': (1 - result['distance']) * 100,
                'distance': result['distance'],
                'threshold': result['threshold'],
                'model': self.config.FACE_VERIFICATION_MODEL,
                'error': None
            }
            
        except Exception as e:
            return {
                'verified': False,
                'confidence': 0,
                'distance': 1.0,
                'error': f'Face verification failed: {str(e)}'
            }
    
    def estimate_age_from_selfie(self, image_path: str) -> Dict[str, Any]:
        """Estimate age from selfie using DeepFace"""
        try:
            # Check image quality first
            quality_check = self._check_image_quality(image_path)
            if not quality_check['acceptable']:
                return {
                    'estimated_age': None,
                    'age_range': None,
                    'confidence': 0,
                    'error': f'Poor image quality: {quality_check["issues"]}'
                }
            
            # Perform age estimation
            analysis = DeepFace.analyze(
                img_path=image_path,
                actions=['age'],
                model_name=self.config.AGE_ESTIMATION_MODEL,
                enforce_detection=True
            )
            
            # Handle both single face and multiple faces
            if isinstance(analysis, list):
                analysis = analysis[0]  # Take first face if multiple detected
            
            estimated_age = analysis['age']
            age_range = self._calculate_age_range(estimated_age)
            
            return {
                'estimated_age': estimated_age,
                'age_range': age_range,
                'confidence': 85,  # DeepFace doesn't provide confidence for age
                'error': None
            }
            
        except Exception as e:
            return {
                'estimated_age': None,
                'age_range': None,
                'confidence': 0,
                'error': f'Age estimation failed: {str(e)}'
            }
    
    def _detect_faces(self, image_path: str) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            # Use OpenCV for face detection
            image = cv2.imread(image_path)
            if image is None:
                return {'face_detected': False, 'face_count': 0}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Filter faces by minimum size
            valid_faces = [face for face in faces if face[2] >= self.config.MIN_FACE_SIZE and face[3] >= self.config.MIN_FACE_SIZE]
            
            return {
                'face_detected': len(valid_faces) > 0,
                'face_count': len(valid_faces),
                'faces': valid_faces.tolist()
            }
            
        except Exception as e:
            return {'face_detected': False, 'face_count': 0, 'error': str(e)}
    
    def _check_image_quality(self, image_path: str) -> Dict[str, Any]:
        """Check if image quality is acceptable for processing"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'acceptable': False, 'issues': ['Cannot read image']}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            issues = []
            
            # Check blur
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            if blur_score < self.config.BLUR_THRESHOLD:
                issues.append('Image too blurry')
            
            # Check brightness
            brightness = np.mean(gray)
            if brightness < self.config.BRIGHTNESS_THRESHOLD:
                issues.append('Image too dark')
            elif brightness > 255 - self.config.BRIGHTNESS_THRESHOLD:
                issues.append('Image too bright')
            
            return {
                'acceptable': len(issues) == 0,
                'issues': issues,
                'blur_score': blur_score,
                'brightness': brightness
            }
            
        except Exception as e:
            return {'acceptable': False, 'issues': [f'Quality check failed: {str(e)}']}
    
    def _calculate_age_range(self, estimated_age: int) -> Dict[str, int]:
        """Calculate age range with tolerance"""
        tolerance = self.config.AGE_TOLERANCE
        return {
            'min_age': max(0, estimated_age - tolerance),
            'max_age': estimated_age + tolerance
        }