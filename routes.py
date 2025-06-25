import os
import uuid
import json
from flask import render_template, request, jsonify, current_app, session
from werkzeug.utils import secure_filename
from app import app, db
from models import VerificationSession
from verification_service import VerificationService

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_verification', methods=['POST'])
def start_verification():
    """Initialize a new verification session"""
    session_id = str(uuid.uuid4())
    session['verification_session_id'] = session_id
    
    # Create new verification session in database
    verification_session = VerificationSession(session_id=session_id)
    db.session.add(verification_session)
    db.session.commit()
    
    return jsonify({'success': True, 'session_id': session_id})

@app.route('/upload_aadhar', methods=['POST'])
def upload_aadhar():
    """Handle Aadhar card image upload and DOB extraction"""
    if 'verification_session_id' not in session:
        return jsonify({'success': False, 'error': 'No active verification session'})
    
    if 'aadhar_image' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['aadhar_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Please upload an image.'})
    
    try:
        # Save uploaded file
        filename = secure_filename(f"aadhar_{session['verification_session_id']}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get verification session
        verification_session = VerificationSession.query.filter_by(
            session_id=session['verification_session_id']
        ).first()
        
        if not verification_session:
            return jsonify({'success': False, 'error': 'Invalid session'})
        
        # Extract DOB using OCR
        verification_service = VerificationService()
        dob, confidence = verification_service.extract_dob(filepath)
        
        if not dob:
            return jsonify({'success': False, 'error': 'Could not extract date of birth from the document'})
        
        age = verification_service.calculate_age(dob)
        
        # Update verification session
        verification_session.aadhar_path = filepath
        verification_session.extracted_dob = dob
        verification_session.extracted_age = age
        verification_session.ocr_confidence = confidence
        db.session.commit()
        
        return jsonify({
            'success': True,
            'dob': dob,
            'age': age,
            'confidence': confidence
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing Aadhar upload: {str(e)}")
        return jsonify({'success': False, 'error': f'Error processing image: {str(e)}'})

@app.route('/upload_selfie', methods=['POST'])
def upload_selfie():
    """Handle selfie upload and complete verification"""
    if 'verification_session_id' not in session:
        return jsonify({'success': False, 'error': 'No active verification session'})
    
    if 'selfie_image' not in request.files:
        return jsonify({'success': False, 'error': 'No selfie uploaded'})
    
    file = request.files['selfie_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    try:
        # Save uploaded selfie
        filename = secure_filename(f"selfie_{session['verification_session_id']}.{file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get verification session
        verification_session = VerificationSession.query.filter_by(
            session_id=session['verification_session_id']
        ).first()
        
        if not verification_session or not verification_session.aadhar_path:
            return jsonify({'success': False, 'error': 'Invalid session or missing Aadhar image'})
        
        verification_service = VerificationService()
        
        # Check image quality
        quality_issues = verification_service.check_image_quality(filepath)
        
        # Perform face verification
        face_matched, face_confidence = verification_service.verify_face_match(
            verification_session.aadhar_path, filepath
        )
        
        # Estimate age from selfie
        age_range, exact_age = None, None
        age_verification_passed = False
        
        if face_matched:
            age_range, exact_age = verification_service.estimate_visual_age_range(filepath)
            if age_range and verification_session.extracted_age:
                age_verification_passed = verification_service.compare_ages(
                    verification_session.extracted_age, age_range
                )
        
        # Update verification session
        verification_session.selfie_path = filepath
        verification_session.face_match_verified = face_matched
        verification_session.face_match_confidence = face_confidence
        verification_session.estimated_age_range = age_range
        verification_session.estimated_exact_age = exact_age
        verification_session.age_verification_passed = age_verification_passed
        verification_session.image_quality_issues = json.dumps(quality_issues)
        verification_session.verification_complete = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'face_matched': face_matched,
            'face_confidence': face_confidence,
            'estimated_age_range': age_range,
            'estimated_exact_age': exact_age,
            'age_verification_passed': age_verification_passed,
            'quality_issues': quality_issues,
            'verification_complete': True
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing selfie: {str(e)}")
        return jsonify({'success': False, 'error': f'Error processing selfie: {str(e)}'})

@app.route('/verification_status')
def verification_status():
    """Get current verification session status"""
    if 'verification_session_id' not in session:
        return jsonify({'success': False, 'error': 'No active verification session'})
    
    verification_session = VerificationSession.query.filter_by(
        session_id=session['verification_session_id']
    ).first()
    
    if not verification_session:
        return jsonify({'success': False, 'error': 'Invalid session'})
    
    return jsonify({
        'success': True,
        'session': verification_session.to_dict()
    })
