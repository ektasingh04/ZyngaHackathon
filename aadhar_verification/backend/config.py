import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Upload settings
    UPLOAD_FOLDER = './uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    # OCR settings
    OCR_LANGUAGES = 'eng+hin'
    TESSERACT_CONFIG = '--oem 3 --psm 6'
    
    # Face verification settings
    FACE_VERIFICATION_MODEL = 'VGG-Face'
    FACE_VERIFICATION_DISTANCE_METRIC = 'cosine'
    FACE_VERIFICATION_THRESHOLD = 0.68
    
    # Age verification settings
    AGE_TOLERANCE = 10
    AGE_ESTIMATION_MODEL = 'Age'
    
    # Image quality thresholds
    BLUR_THRESHOLD = 100
    BRIGHTNESS_THRESHOLD = 50
    MIN_FACE_SIZE = 50
    
    # Session settings
    SESSION_TIMEOUT = timedelta(hours=1)
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = './logs/app.log'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}