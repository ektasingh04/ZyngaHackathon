import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

# Import our services
from models.session import session_manager
from services.ocr_service import OCRService
from services.face_service import FaceService
from services.age_service import AgeService
from utils.image_utils import ImageUtils
from utils.validators import Validators
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])
    
    # Setup logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    
    # Initialize services
    ocr_service = OCRService()
    face_service = FaceService()
    age_service = AgeService()
    image_utils = ImageUtils()
    validators = Validators()
    
    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.error(f'Internal error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/upload-aadhaar', methods=['POST'])
    def upload_aadhaar():
        try:
            # Validate file upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            file_validation = validators.validate_file_upload(file)
            if not file_validation['valid']:
                return jsonify({'error': file_validation['error']}), 400
            
            # Save file
            file_path = image_utils.save_uploaded_file(file, 'aadhaar')
            
            # Validate image
            image_validation = image_utils.validate_image(file_path)
            if not image_validation['valid']:
                image_utils.cleanup_file(file_path)
                return jsonify({'error': image_validation['error']}), 400
            
            # Resize if needed
            image_utils.resize_image(file_path)
            
            # Extract DOB from Aadhaar
            dob, dob_confidence = ocr_service.extract_dob_from_aadhaar(file_path)
            
            # Calculate age if DOB found
            document_age = None
            if dob:
                document_age = age_service.calculate_age_from_dob(dob)
            
            # Create session
            session_id = session_manager.create_session()
            session_manager.update_session(
                session_id,
                aadhaar_path=file_path,
                dob=dob,
                dob_confidence=dob_confidence,
                extracted_age=document_age,
                status='aadhaar_uploaded'
            )
            
            app.logger.info(f'Aadhaar uploaded for session {session_id}')
            
            return jsonify({
                'session_id': session_id,
                'dob': dob,
                'dob_confidence': dob_confidence,
                'extracted_age': document_age,
                'message': 'Aadhaar uploaded successfully'
            })
            
        except Exception as e:
            app.logger.error(f'Error in upload_aadhaar: {str(e)}')
            return jsonify({'error': 'Failed to process Aadhaar upload'}), 500
    
    @app.route('/upload-selfie', methods=['POST'])
    def upload_selfie():
        try:
            # Validate session ID
            session_id = request.form.get('session_id')
            session_validation = validators.validate_session_id(session_id)
            if not session_validation['valid']:
                return jsonify({'error': session_validation['error']}), 400
            
            # Get session
            session = session_manager.get_session(session_id)
            if not session:
                return jsonify({'error': 'Invalid or expired session'}), 400
            
            # Check if both files are uploaded
            if not session.get('aadhaar_path') or not session.get('selfie_path'):
                return jsonify({'error': 'Both Aadhaar and selfie must be uploaded'}), 400
            
            # Perform face verification
            face_result = face_service.verify_faces(
                session['aadhaar_path'],
                session['selfie_path']
            )
            
            # Perform age estimation from selfie
            age_result = face_service.estimate_age_from_selfie(session['selfie_path'])
            
            # Age consistency check
            age_consistency = None
            if session.get('extracted_age') and age_result.get('estimated_age'):
                age_consistency = age_service.verify_age_consistency(
                    session['extracted_age'],
                    age_result['estimated_age']
                )
            
            # Determine overall verification status
            face_verified = face_result.get('verified', False)
            age_verified = True  # Default to true if no age data available
            
            if age_consistency:
                age_verified = age_consistency.get('consistent', False)
            
            overall_status = 'VERIFIED' if (face_verified and age_verified) else 'REJECTED'
            
            # Create verification result
            verification_result = {
                'session_id': session_id,
                'status': overall_status,
                'face_verification': face_result,
                'age_estimation': age_result,
                'age_consistency': age_consistency,
                'document_info': {
                    'dob': session.get('dob'),
                    'dob_confidence': session.get('dob_confidence'),
                    'extracted_age': session.get('extracted_age')
                },
                'eligibility': None,
                'timestamp': datetime.now().isoformat()
            }
            
            # Check eligibility if age is available
            if session.get('extracted_age'):
                eligibility = age_service.is_eligible_for_verification(session['extracted_age'])
                verification_result['eligibility'] = eligibility
            
            # Update session with results
            session_manager.update_session(
                session_id,
                verification_result=verification_result,
                status='verification_complete'
            )
            
            app.logger.info(f'Verification completed for session {session_id}: {overall_status}')
            
            return jsonify(verification_result)
            
        except Exception as e:
            app.logger.error(f'Error in verify: {str(e)}')
            return jsonify({'error': 'Verification process failed'}), 500
    
    @app.route('/session/<session_id>', methods=['GET'])
    def get_session_info(session_id):
        try:
            session_validation = validators.validate_session_id(session_id)
            if not session_validation['valid']:
                return jsonify({'error': session_validation['error']}), 400
            
            session = session_manager.get_session(session_id)
            if not session:
                return jsonify({'error': 'Session not found or expired'}), 404
            
            # Return session info without file paths for security
            session_info = {
                'session_id': session_id,
                'status': session.get('status'),
                'created_at': session.get('created_at').isoformat(),
                'dob': session.get('dob'),
                'dob_confidence': session.get('dob_confidence'),
                'extracted_age': session.get('extracted_age'),
                'has_aadhaar': session.get('aadhaar_path') is not None,
                'has_selfie': session.get('selfie_path') is not None
            }
            
            return jsonify(session_info)
            
        except Exception as e:
            app.logger.error(f'Error getting session info: {str(e)}')
            return jsonify({'error': 'Failed to retrieve session information'}), 500
    
    @app.route('/cleanup-sessions', methods=['POST'])
    def cleanup_sessions():
        try:
            session_manager.cleanup_expired_sessions()
            return jsonify({'message': 'Expired sessions cleaned up successfully'})
        except Exception as e:
            app.logger.error(f'Error cleaning up sessions: {str(e)}')
            return jsonify({'error': 'Failed to cleanup sessions'}), 500
    
    # Cleanup function to run periodically
    def cleanup_files_and_sessions():
        try:
            session_manager.cleanup_expired_sessions()
            # You might want to add file cleanup logic here
            app.logger.info('Cleanup completed')
        except Exception as e:
            app.logger.error(f'Error in cleanup: {str(e)}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("🚀 Starting Aadhaar Verification Backend...")
    print("📁 Upload directory: ./uploads")
    print("📋 Logs directory: ./logs")
    print("🌐 Server running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)