import cv2
import pytesseract
import re
import numpy as np
from datetime import datetime
from typing import Tuple, Optional, List
from config import Config

class OCRService:
    def __init__(self):
        self.config = Config()
        self.dob_patterns = [
            r'DOB[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'Date of Birth[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'(\d{2}[/-]\d{2}[/-]\d{4})',
            r'जन्म तिथि[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})'
        ]
    
    def extract_dob_from_aadhaar(self, image_path: str) -> Tuple[Optional[str], int]:
        """Extract date of birth from Aadhaar card image"""
        try:
            # Read and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return None, 0
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply image enhancement
            enhanced = self._enhance_image_for_ocr(gray)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(
                enhanced, 
                lang=self.config.OCR_LANGUAGES,
                config=self.config.TESSERACT_CONFIG
            )
            
            # Find DOB using patterns
            dob, confidence = self._find_dob_in_text(text)
            
            return dob, confidence
            
        except Exception as e:
            print(f"Error in DOB extraction: {str(e)}")
            return None, 0
    
    def _enhance_image_for_ocr(self, gray_image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better OCR results"""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
        
        # Apply adaptive thresholding
        threshold = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _find_dob_in_text(self, text: str) -> Tuple[Optional[str], int]:
        """Find DOB in extracted text using regex patterns"""
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        for i, pattern in enumerate(self.dob_patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                dob = matches[0].strip()
                # Higher confidence for more specific patterns
                confidence = 90 - (i * 20)
                
                # Validate the extracted date
                if self._validate_date_format(dob):
                    return dob, confidence
        
        return None, 0
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate if the extracted date is in correct format"""
        try:
            # Try to parse the date
            date_str = date_str.replace('/', '-')
            datetime.strptime(date_str, '%d-%m-%Y')
            return True
        except:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except:
                return False