import pytest
from src.utils.validators import (
    validate_email,
    validate_password,
    validate_ssn,
    validate_phone,
    sanitize_input
)

def test_validate_email():
    # Valid emails
    assert validate_email("test@example.com")[0] is True
    assert validate_email("user.name@domain.co.uk")[0] is True
    
    # Invalid emails
    assert validate_email("invalid.email")[0] is False
    assert validate_email("no@domain")[0] is False
    assert validate_email("@domain.com")[0] is False

def test_validate_password():
    # Valid password
    assert validate_password("StrongP@ss123")[0] is True
    
    # Invalid passwords
    assert validate_password("weak")[0] is False  # Too short
    assert validate_password("NoSpecialChar123")[0] is False  # No special char
    assert validate_password("no-upper-123!")[0] is False  # No uppercase
    assert validate_password("NO-LOWER-123!")[0] is False  # No lowercase
    assert validate_password("NoNumbers!!")[0] is False  # No numbers

def test_validate_ssn():
    # Valid SSNs
    assert validate_ssn("123-45-6789")[0] is True
    assert validate_ssn("123456789")[0] is True
    
    # Invalid SSNs
    assert validate_ssn("123-45-678")[0] is False  # Too short
    assert validate_ssn("123-45-67890")[0] is False  # Too long
    assert validate_ssn("abc-de-fghi")[0] is False  # Non-numeric

def test_validate_phone():
    # Valid phone numbers
    assert validate_phone("1234567890")[0] is True
    assert validate_phone("(123) 456-7890")[0] is True
    assert validate_phone("+11234567890")[0] is True
    
    # Invalid phone numbers
    assert validate_phone("123456789")[0] is False  # Too short
    assert validate_phone("12345678901")[0] is False  # Too long
    assert validate_phone("abc-def-ghij")[0] is False  # Non-numeric

def test_sanitize_input():
    # Test HTML removal
    assert sanitize_input("<script>alert('test')</script>") == "alert('test')"
    assert sanitize_input("<p>Hello</p>") == "Hello"
    
    # Test dangerous character removal
    assert sanitize_input("Hello < World >") == "Hello  World "
    
    # Test whitespace handling
    assert sanitize_input("  Hello  World  ") == "Hello  World" 