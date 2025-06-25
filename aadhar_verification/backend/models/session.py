import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from config import Config

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.config = Config()
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'aadhaar_path': None,
            'selfie_path': None,
            'dob': None,
            'dob_confidence': 0,
            'extracted_age': None,
            'verification_result': None,
            'status': 'created'
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        session = self.sessions.get(session_id)
        if session and self._is_session_valid(session):
            return session
        elif session:
            # Clean up expired session
            del self.sessions[session_id]
        return None
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        session = self.get_session(session_id)
        if session:
            session.update(kwargs)
            return True
        return False
    
    def _is_session_valid(self, session: Dict[str, Any]) -> bool:
        """Check if session is still valid"""
        return datetime.now() - session['created_at'] < self.config.SESSION_TIMEOUT
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session['created_at'] > self.config.SESSION_TIMEOUT
        ]
        for sid in expired_sessions:
            del self.sessions[sid]

# Global session manager instance
session_manager = SessionManager()