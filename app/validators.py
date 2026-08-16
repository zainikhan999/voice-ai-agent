import re
from datetime import date, datetime

# List of valid 50 US States + District of Columbia (DC)
VALID_US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC"
}

# Regex patterns
NAME_REGEX = re.compile(r"^[A-Za-z' -]{1,50}$")
ZIP_REGEX = re.compile(r"^\d{5}(-\d{4})?$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
ALPHANUMERIC_REGEX = re.compile(r"^[a-zA-Z0-9]+$")


def validate_and_normalize_phone(phone_str: str) -> str:
    """
    Validates and normalizes US phone number.
    Strips non-digits. Allows 10-digit number or 11-digit starting with country code '1'.
    Returns clean 10-digit string.
    """
    if not phone_str:
        raise ValueError("Phone number is required.")
    
    digits = re.sub(r"\D", "", phone_str)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    
    if len(digits) != 10:
        raise ValueError(f"Invalid US phone number format: '{phone_str}'. Must be a valid 10-digit US phone number.")
    
    return digits


def validate_name(name: str, field_name: str = "Name") -> str:
    """Validates name is 1-50 chars and contains only letters, hyphens, apostrophes, and spaces."""
    if not name or not name.strip():
        raise ValueError(f"{field_name} is required.")
    cleaned = name.strip()
    if len(cleaned) < 1 or len(cleaned) > 50:
        raise ValueError(f"{field_name} must be between 1 and 50 characters long.")
    if not NAME_REGEX.match(cleaned):
        raise ValueError(f"{field_name} '{cleaned}' can only contain letters, hyphens, apostrophes, and spaces.")
    return cleaned


def validate_state(state_code: str) -> str:
    """Validates that state is a valid 2-letter US state or DC abbreviation."""
    if not state_code:
        raise ValueError("State code is required.")
    cleaned = state_code.strip().upper()
    if cleaned not in VALID_US_STATES:
        raise ValueError(f"Invalid US state abbreviation: '{state_code}'. Must be a valid 2-letter US state code.")
    return cleaned


def validate_zip_code(zip_code: str) -> str:
    """Validates ZIP code format (5-digit '12345' or ZIP+4 '12345-6789')."""
    if not zip_code:
        raise ValueError("ZIP code is required.")
    cleaned = zip_code.strip()
    if not ZIP_REGEX.match(cleaned):
        raise ValueError(f"Invalid ZIP code format: '{zip_code}'. Must be 5 digits (e.g. 90210) or ZIP+4 (e.g. 90210-1234).")
    return cleaned


def validate_date_of_birth(dob: date) -> date:
    """Validates that date of birth is not in the future."""
    if not dob:
        raise ValueError("Date of birth is required.")
    today = date.today()
    if dob > today:
        raise ValueError(f"Date of birth '{dob}' cannot be in the future.")
    return dob


def validate_email(email_str: str | None) -> str | None:
    """Validates email format if provided."""
    if not email_str or not email_str.strip():
        return None
    cleaned = email_str.strip()
    if not EMAIL_REGEX.match(cleaned):
        raise ValueError(f"Invalid email address format: '{email_str}'.")
    return cleaned


def validate_insurance_member_id(member_id: str | None) -> str | None:
    """Validates insurance member ID is alphanumeric if provided."""
    if not member_id or not member_id.strip():
        return None
    cleaned = member_id.strip()
    if not ALPHANUMERIC_REGEX.match(cleaned):
        raise ValueError(f"Insurance member ID '{member_id}' must be alphanumeric.")
    return cleaned
