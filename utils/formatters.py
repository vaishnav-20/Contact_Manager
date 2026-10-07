"""
Formatting utilities for contact display, phone numbers, and dates.
"""
from datetime import datetime
from typing import Optional

class Formatter:
    """Formatter helper class."""

    @staticmethod
    def format_phone_display(phone: str) -> str:
        """Format normalized phone numbers for aesthetic display."""
        if not phone:
            return ""
            
        p = phone.strip()
        # If Indian standard (+91XXXXXXXXXX) -> +91 98765 43210
        if p.startswith("+91") and len(p) == 13:
            return f"+91 {p[3:8]} {p[8:]}"
        # If 10 digits -> 98765 43210
        if len(p) == 10 and p.isdigit():
            return f"{p[:5]} {p[5:]}"
        # US/Intl format (+1XXXXXXXXXX) -> +1 (XXX) XXX-XXXX
        if p.startswith("+1") and len(p) == 12:
            return f"+1 ({p[2:5]}) {p[5:8]}-{p[8:]}"
            
        return p

    @staticmethod
    def format_name(first_name: str, last_name: str = "", display_name: str = "") -> str:
        """Return best display name for a contact."""
        if display_name and display_name.strip():
            return display_name.strip()
        
        parts = [p.strip() for p in [first_name, last_name] if p and p.strip()]
        return " ".join(parts) if parts else "Unnamed Contact"

    @staticmethod
    def format_date_display(dt: Optional[datetime]) -> str:
        """Format datetime to readable string: 'Sep 09, 2026'."""
        if not dt:
            return ""
        return dt.strftime("%b %d, %Y")

    @staticmethod
    def format_datetime_display(dt: Optional[datetime]) -> str:
        """Format datetime to readable string with time: 'Sep 09, 2026 19:30'."""
        if not dt:
            return ""
        return dt.strftime("%b %d, %Y %H:%M")

    @staticmethod
    def format_number(num: int) -> str:
        """Format number with thousands comma: 1,248."""
        return f"{num:,}"
