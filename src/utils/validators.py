import re
from typing import Optional, Tuple
from src.utils.config import APP_CONFIG

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, None

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < APP_CONFIG['PASSWORD_MIN_LENGTH']:
        return False, f"Password must be at least {APP_CONFIG['PASSWORD_MIN_LENGTH']} characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def validate_ssn(ssn: str) -> Tuple[bool, Optional[str]]:
    """Validate SSN format"""
    pattern = r'^\d{3}-?\d{2}-?\d{4}$'
    if not re.match(pattern, ssn):
        return False, "Invalid SSN format. Use XXX-XX-XXXX"
    return True, None

def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate phone number format"""
    pattern = r'^\+?1?\d{10}$'
    if not re.match(pattern, phone.replace('-', '').replace('(', '').replace(')', '')):
        return False, "Invalid phone number format"
    return True, None

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove any script tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    # Remove any potentially dangerous characters
    text = re.sub(r'[<>]', '', text)
    return text.strip() 