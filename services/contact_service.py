"""
Core Contact Business Service.
Orchestrates validation, normalization, CRUD operations, soft-delete, and audit tracking.
"""
from typing import List, Optional, Tuple, Dict, Any
from database.repository import ContactRepository
from models.contact import Contact
from models.group import Group
from models.tag import Tag
from services.validation_service import ValidationService
from utils.logger import get_logger

logger = get_logger("ContactService")


class ContactService:
    """Service providing high-level contact management business logic."""

    def __init__(self, repo: ContactRepository = None):
        self.repo = repo or ContactRepository()

    def create_contact(self, contact: Contact) -> Tuple[Optional[Contact], Dict[str, str]]:
        """
        Normalize, validate, and create a new contact.
        Returns:
            (saved_contact, errors_dict)
        """
        contact.normalize()
        is_valid, errors = ValidationService.validate_contact(contact)
        if not is_valid:
            logger.warning(f"Validation failed while creating contact: {errors}")
            return None, errors

        saved = self.repo.add_contact(contact)
        return saved, {}

    def update_contact(self, contact: Contact) -> Tuple[Optional[Contact], Dict[str, str]]:
        """
        Normalize, validate, and update an existing contact.
        Returns:
            (updated_contact, errors_dict)
        """
        contact.normalize()
        is_valid, errors = ValidationService.validate_contact(contact)
        if not is_valid:
            logger.warning(f"Validation failed while updating contact ID {contact.id}: {errors}")
            return None, errors

        updated = self.repo.update_contact(contact)
        return updated, {}

    def get_contact(self, contact_id: int, include_deleted: bool = False) -> Optional[Contact]:
        """Fetch single contact by ID."""
        return self.repo.get_contact_by_id(contact_id, include_deleted=include_deleted)

    def delete_contact(self, contact_id: int, permanent: bool = False) -> bool:
        """Delete a contact (soft-delete by default, hard-delete if permanent=True)."""
        if permanent:
            return self.repo.hard_delete_contact(contact_id)
        return self.repo.soft_delete_contact(contact_id)

    def restore_contact(self, contact_id: int) -> bool:
        """Restore a soft-deleted contact."""
        return self.repo.restore_contact(contact_id)

    def toggle_favorite(self, contact_id: int) -> Optional[bool]:
        """Toggle favorite state of a contact."""
        return self.repo.toggle_favorite(contact_id)

    def list_contacts(
        self,
        include_deleted: bool = False,
        favorites_only: bool = False,
        group_name: Optional[str] = None,
        tag_name: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Tuple[List[Contact], int]:
        """List contacts with filtering and pagination."""
        return self.repo.get_all_contacts(
            include_deleted=include_deleted,
            favorites_only=favorites_only,
            group_name=group_name,
            tag_name=tag_name,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )

    def get_all_groups(self) -> List[Group]:
        """Fetch all groups."""
        return self.repo.get_all_groups()

    def create_group(self, name: str, description: str = "", color: str = "#2563eb", icon: str = "📁") -> Group:
        """Create new group."""
        return self.repo.create_group(Group(name=name, description=description, color=color, icon=icon))

    def delete_group(self, group_id: int) -> bool:
        """Delete a group."""
        return self.repo.delete_group(group_id)

    def get_all_tags(self) -> List[Tag]:
        """Fetch all tags."""
        return self.repo.get_all_tags()

    def create_tag(self, name: str, color: str = "#d4af37") -> Tag:
        """Create new tag."""
        return self.repo.create_tag(Tag(name=name, color=color))

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag."""
        return self.repo.delete_tag(tag_id)

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Return aggregated KPIs for dashboard."""
        return self.repo.get_dashboard_metrics()
