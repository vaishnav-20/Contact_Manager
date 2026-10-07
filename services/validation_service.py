"""
Validation Service for Contact Manager Pro.
Validates contact data before insertion or modification, collecting field-specific errors.
"""
from typing import Dict, Any, Tuple
from models.contact import Contact
from utils.validators import Validator


class ValidationService:
    """Service handling validation and business rule enforcement."""

    @staticmethod
    def validate_contact(contact: Contact) -> Tuple[bool, Dict[str, str]]:
        """
        Validate all fields of a contact instance.
        Returns:
            (is_valid: bool, errors: Dict[field_name, error_message])
        """
        errors: Dict[str, str] = {}

        # 1. First Name validation
        valid_name, err = Validator.validate_name(contact.first_name, contact.last_name)
        if not valid_name:
            errors["first_name"] = err

        # 2. Email validation
        if contact.email:
            valid_email, err = Validator.validate_email(contact.email)
            if not valid_email:
                errors["email"] = err

        # 3. Alternate Email validation
        if contact.alternate_email:
            valid_alt_email, err = Validator.validate_email(contact.alternate_email)
            if not valid_alt_email:
                errors["alternate_email"] = err

        # 4. Primary Phone validation
        if contact.phone:
            valid_phone, err = Validator.validate_phone(contact.phone)
            if not valid_phone:
                errors["phone"] = err

        # 5. Alternate Phone validation
        if contact.alternate_phone:
            valid_alt_phone, err = Validator.validate_phone(contact.alternate_phone)
            if not valid_alt_phone:
                errors["alternate_phone"] = err

        # 6. Website URL validation
        if contact.website:
            valid_url, err = Validator.validate_url(contact.website)
            if not valid_url:
                errors["website"] = err

        # 7. Date of Birth validation
        if contact.date_of_birth:
            valid_dob, err = Validator.validate_date(contact.date_of_birth)
            if not valid_dob:
                errors["date_of_birth"] = err

        return len(errors) == 0, errors
