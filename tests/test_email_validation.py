"""
Test email validation functionality
"""
import pytest
from utils import validate_email

class TestEmailValidation:
    """Test email validation function"""
    
    def test_valid_emails(self):
        """Test valid email addresses"""
        valid_emails = [
            'user@example.com',
            'test.user@example.com',
            'user+tag@example.co.uk',
            'user123@test-domain.com',
            'first.last@company.org',
            'admin@subdomain.example.com'
        ]
        
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid, f"Email {email} should be valid but got error: {error}"
            assert error is None
    
    def test_invalid_format(self):
        """Test invalid email formats"""
        invalid_emails = [
            'abc@123',  # Invalid domain (numbers only)
            'user@',  # Missing domain
            '@example.com',  # Missing username
            'user.example.com',  # Missing @
            'user @example.com',  # Space in email
            'user@domain',  # No TLD
            'user@.com',  # Missing domain name
            '',  # Empty string
            'plaintext',  # No @ symbol
        ]
        
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert not is_valid, f"Email {email} should be invalid"
            assert error is not None
    
    def test_disposable_emails(self):
        """Test disposable email detection"""
        disposable_emails = [
            'test@tempmail.com',
            'user@10minutemail.com',
            'fake@guerrillamail.com',
            'temp@mailinator.com'
        ]
        
        for email in disposable_emails:
            is_valid, error = validate_email(email)
            assert not is_valid, f"Disposable email {email} should be rejected"
            assert 'disposable' in error.lower() or 'temporary' in error.lower()
    
    def test_edge_cases(self):
        """Test edge cases"""
        # None
        is_valid, error = validate_email(None)
        assert not is_valid
        
        # Whitespace
        is_valid, error = validate_email('   ')
        assert not is_valid
        
        # Case insensitivity
        is_valid1, _ = validate_email('Test@Example.COM')
        is_valid2, _ = validate_email('test@example.com')
        assert is_valid1 == is_valid2
    
    def test_tld_validation(self):
        """Test top-level domain validation"""
        # Valid TLDs
        assert validate_email('user@example.com')[0] is True
        assert validate_email('user@example.org')[0] is True
        assert validate_email('user@example.co.uk')[0] is True
        
        # Invalid TLDs
        assert validate_email('user@example.c')[0] is False  # TLD too short
