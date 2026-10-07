"""
Data Validation and Normalization Engine.
Validates names, emails, phone numbers, dates, and URLs according to strict industry standards.
"""
import re
from datetime import datetime
from typing import Tuple, Optional

# Precompiled Regexes
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

PHONE_CLEAN_REGEX = re.compile(r"[^\d+]")
PHONE_VALID_REGEX = re.compile(r"^\+?[0-9]{7,15}$")
URL_REGEX = re.compile(
    r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
)


class Validator:
    """Validator providing static validation and normalization methods."""

    @staticmethod
    def validate_name(first_name: str, last_name: str = "") -> Tuple[bool, Optional[str]]:
        """Validate contact name."""
        if not first_name or not first_name.strip():
            return False, "First name is mandatory and cannot be blank."
        
        cleaned_first = first_name.strip()
        if len(cleaned_first) < 1:
            return False, "First name must contain at least 1 character."
        if len(cleaned_first) > 100:
            return False, "First name cannot exceed 100 characters."
            
        # Check for invalid control characters
        if re.search(r"[\x00-\x1f\x7f]", cleaned_first):
            return False, "First name contains invalid control characters."
            
        if last_name and len(last_name.strip()) > 100:
            return False, "Last name cannot exceed 100 characters."

        return True, None

    @staticmethod
    def normalize_name(name: str) -> str:
        """Strip and title-case names."""
        if not name:
            return ""
        # Collapse multi spaces and title case
        parts = name.strip().split()
        return " ".join(p.capitalize() for p in parts)

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email address format."""
        if not email or not email.strip():
            return True, None  # Email can be optional unless specified
        
        email_clean = email.strip()
        if len(email_clean) > 254:
            return False, "Email address is too long (max 254 chars)."
        
        if not EMAIL_REGEX.match(email_clean):
            return False, "Invalid email address format (e.g. name@domain.com)."
            
        return True, None

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email address to lowercase stripped format."""
        if not email:
            return ""
        return email.strip().lower()

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number string."""
        if not phone or not phone.strip():
            return True, None  # Phone can be optional
        
        # Strip common formatting characters: spaces, hyphens, parentheses, dots
        cleaned = PHONE_CLEAN_REGEX.sub("", phone.strip())
        
        if not PHONE_VALID_REGEX.match(cleaned):
            return False, "Invalid phone number. Must contain 7 to 15 digits (e.g. +91 9876543210 or 9876543210)."
            
        return True, None

    @staticmethod
    def normalize_phone(phone: str, default_country_code: str = "+91") -> str:
        """
        Normalize phone numbers into standard format (+CC XXXXXXXXXX).
        Handles local numbers and international prefixes.
        """
        if not phone:
            return ""
        
        # Keep leading + if present, strip all other non-digits
        cleaned = phone.strip()
        has_plus = cleaned.startswith("+")
        digits_only = "".join(ch for ch in cleaned if ch.isdigit())
        
        if not digits_only:
            return ""
            
        if has_plus:
            return f"+{digits_only}"
            
        # If 10 digits (e.g. Indian standard mobile), prepend default country code if configured
        if len(digits_only) == 10 and default_country_code:
            cc = default_country_code if default_country_code.startswith("+") else f"+{default_country_code}"
            return f"{cc}{digits_only}"
            
        return digits_only

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """Validate website URL."""
        if not url or not url.strip():
            return True, None
        
        url_clean = url.strip()
        if not URL_REGEX.match(url_clean):
            return False, "Invalid URL format (e.g. https://example.com)."
        return True, None

    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
        """Validate date string against common formats (YYYY-MM-DD, DD/MM/YYYY)."""
        if not date_str or not date_str.strip():
            return True, None
            
        clean_date = date_str.strip()
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                datetime.strptime(clean_date, fmt)
                return True, None
            except ValueError:
                continue
        return False, "Invalid date format. Expected YYYY-MM-DD or DD/MM/YYYY."
