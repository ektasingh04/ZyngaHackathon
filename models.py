from app import db
from datetime import datetime

class VerificationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    aadhar_path = db.Column(db.String(200))
    selfie_path = db.Column(db.String(200))
    extracted_dob = db.Column(db.String(20))
    extracted_age = db.Column(db.Integer)
    ocr_confidence = db.Column(db.Float)
    face_match_verified = db.Column(db.Boolean)
    face_match_confidence = db.Column(db.Float)
    estimated_age_range = db.Column(db.String(20))
    estimated_exact_age = db.Column(db.Integer)
    age_verification_passed = db.Column(db.Boolean)
    image_quality_issues = db.Column(db.Text)  # JSON string of quality issues
    verification_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'extracted_dob': self.extracted_dob,
            'extracted_age': self.extracted_age,
            'ocr_confidence': self.ocr_confidence,
            'face_match_verified': self.face_match_verified,
            'face_match_confidence': self.face_match_confidence,
            'estimated_age_range': self.estimated_age_range,
            'estimated_exact_age': self.estimated_exact_age,
            'age_verification_passed': self.age_verification_passed,
            'image_quality_issues': self.image_quality_issues,
            'verification_complete': self.verification_complete,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
