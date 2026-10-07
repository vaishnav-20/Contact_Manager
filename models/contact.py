"""
Domain Contact Model.
Full-featured OOP representation supporting 25+ fields across Personal, Contact,
Professional, Address, Organizational, and Metadata categories.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from utils.formatters import Formatter
from utils.validators import Validator


@dataclass
class Contact:
    """Contact Entity with full portfolio specification fields."""
    # Identity & Primary Key
    id: Optional[int] = None
    
    # Personal Information
    first_name: str = ""
    last_name: str = ""
    display_name: str = ""
    date_of_birth: Optional[str] = None    # YYYY-MM-DD
    gender: Optional[str] = None          # Male, Female, Other, Prefer not to say
    profile_photo: Optional[str] = None   # File path or avatar identifier
    
    # Contact Information
    phone: str = ""
    alternate_phone: Optional[str] = None
    email: str = ""
    alternate_email: Optional[str] = None
    website: Optional[str] = None
    
    # Professional Information
    company: str = ""
    job_title: str = ""
    department: str = ""
    
    # Address Information
    address_line: str = ""
    city: str = ""
    state: str = ""
    country: str = ""
    postal_code: str = ""
    
    # Organization
    groups: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    contact_type: str = "Personal"        # Personal, Work, Client, Vendor, Partner
    
    # Additional Metadata
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    is_deleted: bool = False              # Soft delete flag

    @property
    def full_name(self) -> str:
        """Return formatted full name."""
        return Formatter.format_name(self.first_name, self.last_name, self.display_name)

    @property
    def formatted_phone(self) -> str:
        """Return pretty-formatted phone number for UI."""
        return Formatter.format_phone_display(self.phone)

    @property
    def groups_str(self) -> str:
        """Return comma-separated string of groups."""
        return ", ".join(self.groups) if self.groups else ""

    @property
    def tags_str(self) -> str:
        """Return comma-separated string of tags."""
        return ", ".join(self.tags) if self.tags else ""

    @property
    def location_str(self) -> str:
        """Return formatted City, Country summary."""
        parts = [p for p in [self.city, self.country] if p and p.strip()]
        return ", ".join(parts) if parts else ""

    def normalize(self) -> None:
        """Run standard normalization across all fields."""
        self.first_name = Validator.normalize_name(self.first_name)
        self.last_name = Validator.normalize_name(self.last_name)
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}".strip()
        else:
            self.display_name = self.display_name.strip()
            
        self.email = Validator.normalize_email(self.email)
        if self.alternate_email:
            self.alternate_email = Validator.normalize_email(self.alternate_email)
            
        self.phone = Validator.normalize_phone(self.phone)
        if self.alternate_phone:
            self.alternate_phone = Validator.normalize_phone(self.alternate_phone)
            
        self.company = self.company.strip()
        self.job_title = self.job_title.strip()
        self.department = self.department.strip()
        self.city = Validator.normalize_name(self.city)
        self.state = Validator.normalize_name(self.state)
        self.country = Validator.normalize_name(self.country)
        self.postal_code = self.postal_code.strip()
        self.notes = self.notes.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert Contact object to a serializable dictionary."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "profile_photo": self.profile_photo,
            "phone": self.phone,
            "alternate_phone": self.alternate_phone,
            "email": self.email,
            "alternate_email": self.alternate_email,
            "website": self.website,
            "company": self.company,
            "job_title": self.job_title,
            "department": self.department,
            "address_line": self.address_line,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "groups": list(self.groups),
            "tags": list(self.tags),
            "is_favorite": self.is_favorite,
            "contact_type": self.contact_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_contacted": self.last_contacted.isoformat() if self.last_contacted else None,
            "is_deleted": self.is_deleted
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Contact":
        """Reconstruct Contact from dictionary data."""
        def parse_dt(val):
            if isinstance(val, str) and val:
                try:
                    return datetime.fromisoformat(val)
                except ValueError:
                    return None
            elif isinstance(val, datetime):
                return val
            return None

        groups_raw = data.get("groups", [])
        if isinstance(groups_raw, str):
            groups = [g.strip() for g in groups_raw.split(",") if g.strip()]
        else:
            groups = list(groups_raw or [])

        tags_raw = data.get("tags", [])
        if isinstance(tags_raw, str):
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        else:
            tags = list(tags_raw or [])

        return cls(
            id=data.get("id"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            display_name=data.get("display_name", ""),
            date_of_birth=data.get("date_of_birth"),
            gender=data.get("gender"),
            profile_photo=data.get("profile_photo"),
            phone=data.get("phone", ""),
            alternate_phone=data.get("alternate_phone"),
            email=data.get("email", ""),
            alternate_email=data.get("alternate_email"),
            website=data.get("website"),
            company=data.get("company", ""),
            job_title=data.get("job_title", ""),
            department=data.get("department", ""),
            address_line=data.get("address_line", ""),
            city=data.get("city", ""),
            state=data.get("state", ""),
            country=data.get("country", ""),
            postal_code=data.get("postal_code", ""),
            groups=groups,
            tags=tags,
            is_favorite=bool(data.get("is_favorite", False)),
            contact_type=data.get("contact_type", "Personal"),
            notes=data.get("notes", ""),
            created_at=parse_dt(data.get("created_at")),
            updated_at=parse_dt(data.get("updated_at")),
            last_contacted=parse_dt(data.get("last_contacted")),
            is_deleted=bool(data.get("is_deleted", False))
        )
