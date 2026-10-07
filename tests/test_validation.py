"""
Unit tests for Validator and Formatter engines.
"""
import pytest
from utils.validators import Validator
from utils.formatters import Formatter
from models.contact import Contact


def test_name_validation():
    """Test first name constraints."""
    valid, err = Validator.validate_name("Arun")
    assert valid is True
    assert err is None

    # Empty name should fail
    valid, err = Validator.validate_name("")
    assert valid is False
    assert "First name is mandatory" in err

    valid, err = Validator.validate_name("   ")
    assert valid is False


def test_name_normalization():
    """Test capitalization and spacing normalization."""
    assert Validator.normalize_name("arun kumar") == "Arun Kumar"
    assert Validator.normalize_name("  PRIYA   SHARMA  ") == "Priya Sharma"


def test_email_validation():
    """Test standard RFC email regex validation."""
    valid, err = Validator.validate_email("arun@microsoft.com")
    assert valid is True

    valid, err = Validator.validate_email("user.name+tag@sub.domain.co.in")
    assert valid is True

    # Invalid formats
    assert Validator.validate_email("invalid-email")[0] is False
    assert Validator.validate_email("test@")[0] is False
    assert Validator.validate_email("@domain.com")[0] is False


def test_email_normalization():
    """Test lowercasing and trimming."""
    assert Validator.normalize_email("  ARUN@GMAIL.COM  ") == "arun@gmail.com"


def test_phone_normalization_and_validation():
    """Test phone digits normalization and formats."""
    # 10-digit standard Indian mobile
    norm = Validator.normalize_phone("9876543210")
    assert norm == "+919876543210"

    # Already prefixed
    norm_intl = Validator.normalize_phone("+91 98765-43210")
    assert norm_intl == "+919876543210"

    # Valid check
    valid, _ = Validator.validate_phone("+91 9876543210")
    assert valid is True

    # Invalid characters / too short
    valid, err = Validator.validate_phone("123")
    assert valid is False


def test_phone_display_formatting():
    """Test pretty printing phone numbers."""
    disp = Formatter.format_phone_display("+919876543210")
    assert disp == "+91 98765 43210"
