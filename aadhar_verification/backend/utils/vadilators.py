import re
from typing import Dict, Any, Optional

class Validators:
    @staticmethod
    def validate_session_id(session_id: str) -> Dict[str, Any]:
        """Validate session ID format"""
        if not session_id:
            return {'valid': False, 'error': 'Session ID is required'}
        
        # Check if it's a valid UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, session_id):
            return {'valid': False, 'error': 'Invalid session ID format'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_file_upload(file) -> Dict[str, Any]:
        """Validate uploaded file"""
        if not file:
            return {'valid': False, 'error': 'No file provided'}
        
        if file.filename == '':
            return {'valid': False, 'error': 'No file selected'}
        
        # Check file extension
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'bmp'}):
            return {'valid': False, 'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_date_format(date_str: str) -> Dict[str, Any]:
        """Validate date string format"""
        if not date_str:
            return {'valid': False, 'error': 'Date is required'}
        
        # Common date patterns
        date_patterns = [
            r'^\d{2}[-/]\d{2}[-/]\d{4}$',  # DD-MM-YYYY or DD/MM/YYYY
            r'^\d{4}[-/]\d{2}[-/]\d{2}$',  # YYYY-MM-DD or YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, date_str):
                return {'valid': True}
        
        return {'valid': False, 'error': 'Invalid date format. Expected: DD-MM-YYYY or YYYY-MM-DD'}