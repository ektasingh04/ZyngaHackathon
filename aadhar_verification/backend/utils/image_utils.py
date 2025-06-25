import os
import uuid
from PIL import Image
import cv2
import numpy as np
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from config import Config

class ImageUtils:
    def __init__(self):
        self.config = Config()
    
    def save_uploaded_file(self, file, prefix: str = '') -> str:
        """Save uploaded file with unique name"""
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{prefix}_{uuid.uuid4().hex}.{file_ext}"
        
        # Ensure upload directory exists
        os.makedirs(self.config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(self.config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        return file_path
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.config.ALLOWED_EXTENSIONS
    
    def resize_image(self, image_path: str, max_size: Tuple[int, int] = (1024, 1024)) -> str:
        """Resize image if it's too large"""
        try:
            with Image.open(image_path) as img:
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(image_path, optimize=True, quality=85)
            return image_path
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return image_path
    
    def validate_image(self, image_path: str) -> Dict[str, Any]:
        """Validate image file"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {'valid': False, 'error': 'File does not exist'}
            
            # Try to open with PIL
            with Image.open(image_path) as img:
                width, height = img.size
                format = img.format
                mode = img.mode
            
            # Basic validation
            if width < 100 or height < 100:
                return {'valid': False, 'error': 'Image too small (minimum 100x100)'}
            
            if format not in ['JPEG', 'PNG', 'BMP', 'GIF']:
                return {'valid': False, 'error': 'Unsupported image format'}
            
            return {
                'valid': True,
                'width': width,
                'height': height,
                'format': format,
                'mode': mode
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Invalid image file: {str(e)}'}
    
    def cleanup_file(self, file_path: str) -> bool:
        """Delete file safely"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
            return False