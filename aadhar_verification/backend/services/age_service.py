from datetime import datetime
from typing import Optional, Dict, Any
from dateutil.relativedelta import relativedelta

class AgeService:
    def __init__(self):
        pass
    
    def calculate_age_from_dob(self, dob_str: str) -> Optional[int]:
        """Calculate current age from date of birth string"""
        try:
            # Handle different date formats
            dob_str = dob_str.replace('/', '-')
            
            # Try different date formats
            date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%m-%d-%Y']
            
            for fmt in date_formats:
                try:
                    dob = datetime.strptime(dob_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return None
            
            # Calculate age
            today = datetime.today()
            age = relativedelta(today, dob).years
            
            return age
            
        except Exception as e:
            print(f"Error calculating age: {str(e)}")
            return None
    
    def verify_age_consistency(self, document_age: int, estimated_age: int, tolerance: int = 10) -> Dict[str, Any]:
        """Verify if document age and estimated age are consistent"""
        age_difference = abs(document_age - estimated_age)
        is_consistent = age_difference <= tolerance
        
        return {
            'consistent': is_consistent,
            'document_age': document_age,
            'estimated_age': estimated_age,
            'age_difference': age_difference,
            'tolerance': tolerance,
            'confidence': max(0, 100 - (age_difference * 5))  # Confidence decreases with difference
        }
    
    def get_age_group(self, age: int) -> str:
        """Get age group classification"""
        if age < 13:
            return 'Child'
        elif age < 18:
            return 'Minor'
        elif age < 25:
            return 'Young Adult'
        elif age < 35:
            return 'Adult'
        elif age < 50:
            return 'Middle Age'
        elif age < 65:
            return 'Senior'
        else:
            return 'Elderly'
    
    def is_eligible_for_verification(self, age: int, min_age: int = 18) -> Dict[str, Any]:
        """Check if person is eligible for verification based on age"""
        eligible = age >= min_age
        
        return {
            'eligible': eligible,
            'age': age,
            'min_required_age': min_age,
            'age_group': self.get_age_group(age)
        }