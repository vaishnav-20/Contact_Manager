"""
Repository pattern implementation for SQLite / SQLAlchemy data access.
Encapsulates transactions, CRUD operations, relationships, audit logs, and complex querying.
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import or_, and_, desc, asc, func
from sqlalchemy.orm import Session, joinedload

from database.connection import get_db_session
from database.models import ContactDB, GroupDB, TagDB, ContactGroupDB, ContactTagDB, AuditLogDB, SettingDB
from models.contact import Contact
from models.group import Group
from models.tag import Tag
from utils.logger import get_logger

logger = get_logger("Repository")


class ContactRepository:
    """Repository handling all database operations."""

    def __init__(self, db_url: str = None):
        self.db_url = db_url

    # -------------------------------------------------------------
    # ENTITY CONVERSIONS
    # -------------------------------------------------------------
    @staticmethod
    def _to_domain(db_entity: ContactDB) -> Contact:
        """Convert ORM model to domain Contact entity."""
        if not db_entity:
            return None
            
        group_names = [g.name for g in db_entity.groups] if db_entity.groups else []
        tag_names = [t.name for t in db_entity.tags] if db_entity.tags else []

        return Contact(
            id=db_entity.id,
            first_name=db_entity.first_name,
            last_name=db_entity.last_name or "",
            display_name=db_entity.display_name or "",
            date_of_birth=db_entity.date_of_birth,
            gender=db_entity.gender,
            profile_photo=db_entity.profile_photo,
            phone=db_entity.phone or "",
            alternate_phone=db_entity.alternate_phone,
            email=db_entity.email or "",
            alternate_email=db_entity.alternate_email,
            website=db_entity.website,
            company=db_entity.company or "",
            job_title=db_entity.job_title or "",
            department=db_entity.department or "",
            address_line=db_entity.address_line or "",
            city=db_entity.city or "",
            state=db_entity.state or "",
            country=db_entity.country or "",
            postal_code=db_entity.postal_code or "",
            groups=group_names,
            tags=tag_names,
            is_favorite=bool(db_entity.is_favorite),
            contact_type=db_entity.contact_type or "Personal",
            notes=db_entity.notes or "",
            created_at=db_entity.created_at,
            updated_at=db_entity.updated_at,
            last_contacted=db_entity.last_contacted,
            is_deleted=bool(db_entity.is_deleted)
        )

    def _sync_groups_and_tags(self, session: Session, db_contact: ContactDB, group_names: List[str], tag_names: List[str]):
        """Synchronize many-to-many associations for groups and tags."""
        # Sync Groups
        current_groups = []
        for g_name in group_names:
            clean_name = g_name.strip()
            if not clean_name:
                continue
            group_obj = session.query(GroupDB).filter(func.lower(GroupDB.name) == clean_name.lower()).first()
            if not group_obj:
                group_obj = GroupDB(name=clean_name)
                session.add(group_obj)
                session.flush()
            current_groups.append(group_obj)
        db_contact.groups = current_groups

        # Sync Tags
        current_tags = []
        for t_name in tag_names:
            clean_name = t_name.strip()
            if not clean_name:
                continue
            tag_obj = session.query(TagDB).filter(func.lower(TagDB.name) == clean_name.lower()).first()
            if not tag_obj:
                tag_obj = TagDB(name=clean_name)
                session.add(tag_obj)
                session.flush()
            current_tags.append(tag_obj)
        db_contact.tags = current_tags

    # -------------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------------
    def add_contact(self, contact: Contact) -> Contact:
        """Create a new contact in the database."""
        with get_db_session(self.db_url) as session:
            now = datetime.now(timezone.utc)
            db_contact = ContactDB(
                first_name=contact.first_name,
                last_name=contact.last_name,
                display_name=contact.display_name or f"{contact.first_name} {contact.last_name}".strip(),
                date_of_birth=contact.date_of_birth,
                gender=contact.gender,
                profile_photo=contact.profile_photo,
                phone=contact.phone,
                alternate_phone=contact.alternate_phone,
                email=contact.email,
                alternate_email=contact.alternate_email,
                website=contact.website,
                company=contact.company,
                job_title=contact.job_title,
                department=contact.department,
                address_line=contact.address_line,
                city=contact.city,
                state=contact.state,
                country=contact.country,
                postal_code=contact.postal_code,
                is_favorite=contact.is_favorite,
                contact_type=contact.contact_type,
                notes=contact.notes,
                created_at=now,
                updated_at=now,
                is_deleted=contact.is_deleted
            )
            session.add(db_contact)
            session.flush()

            self._sync_groups_and_tags(session, db_contact, contact.groups, contact.tags)
            session.flush()
            
            # Audit log
            audit = AuditLogDB(
                contact_id=db_contact.id,
                action="CREATE",
                details=f"Created contact {contact.full_name} ({contact.phone or contact.email})"
            )
            session.add(audit)
            
            # Reconstruct domain model with generated ID
            saved_contact = self._to_domain(db_contact)
            logger.info(f"Added new contact ID {saved_contact.id}: {saved_contact.full_name}")
            return saved_contact

    def get_contact_by_id(self, contact_id: int, include_deleted: bool = False) -> Optional[Contact]:
        """Fetch single contact by ID."""
        with get_db_session(self.db_url) as session:
            query = session.query(ContactDB).filter(ContactDB.id == contact_id)
            if not include_deleted:
                query = query.filter(ContactDB.is_deleted == False)
            db_contact = query.first()
            return self._to_domain(db_contact)

    def update_contact(self, contact: Contact) -> Optional[Contact]:
        """Update existing contact."""
        if not contact.id:
            raise ValueError("Cannot update contact without an ID.")
            
        with get_db_session(self.db_url) as session:
            db_contact = session.query(ContactDB).filter(ContactDB.id == contact.id).first()
            if not db_contact:
                return None

            db_contact.first_name = contact.first_name
            db_contact.last_name = contact.last_name
            db_contact.display_name = contact.display_name or f"{contact.first_name} {contact.last_name}".strip()
            db_contact.date_of_birth = contact.date_of_birth
            db_contact.gender = contact.gender
            db_contact.profile_photo = contact.profile_photo
            db_contact.phone = contact.phone
            db_contact.alternate_phone = contact.alternate_phone
            db_contact.email = contact.email
            db_contact.alternate_email = contact.alternate_email
            db_contact.website = contact.website
            db_contact.company = contact.company
            db_contact.job_title = contact.job_title
            db_contact.department = contact.department
            db_contact.address_line = contact.address_line
            db_contact.city = contact.city
            db_contact.state = contact.state
            db_contact.country = contact.country
            db_contact.postal_code = contact.postal_code
            db_contact.is_favorite = contact.is_favorite
            db_contact.contact_type = contact.contact_type
            db_contact.notes = contact.notes
            db_contact.updated_at = datetime.now(timezone.utc)
            db_contact.is_deleted = contact.is_deleted

            self._sync_groups_and_tags(session, db_contact, contact.groups, contact.tags)
            
            audit = AuditLogDB(
                contact_id=contact.id,
                action="UPDATE",
                details=f"Updated contact {contact.full_name}"
            )
            session.add(audit)
            session.flush()
            
            logger.info(f"Updated contact ID {contact.id}: {contact.full_name}")
            return self._to_domain(db_contact)

    def soft_delete_contact(self, contact_id: int) -> bool:
        """Mark contact as deleted (is_deleted = True)."""
        with get_db_session(self.db_url) as session:
            db_contact = session.query(ContactDB).filter(ContactDB.id == contact_id).first()
            if not db_contact:
                return False
            db_contact.is_deleted = True
            db_contact.updated_at = datetime.now(timezone.utc)
            
            audit = AuditLogDB(
                contact_id=contact_id,
                action="DELETE",
                details=f"Soft-deleted contact ID {contact_id}"
            )
            session.add(audit)
            logger.info(f"Soft deleted contact ID {contact_id}")
            return True

    def restore_contact(self, contact_id: int) -> bool:
        """Restore soft-deleted contact."""
        with get_db_session(self.db_url) as session:
            db_contact = session.query(ContactDB).filter(ContactDB.id == contact_id).first()
            if not db_contact:
                return False
            db_contact.is_deleted = False
            db_contact.updated_at = datetime.now(timezone.utc)
            
            audit = AuditLogDB(
                contact_id=contact_id,
                action="RESTORE",
                details=f"Restored contact ID {contact_id}"
            )
            session.add(audit)
            logger.info(f"Restored contact ID {contact_id}")
            return True

    def hard_delete_contact(self, contact_id: int) -> bool:
        """Permanently remove contact record from database."""
        with get_db_session(self.db_url) as session:
            db_contact = session.query(ContactDB).filter(ContactDB.id == contact_id).first()
            if not db_contact:
                return False
            session.delete(db_contact)
            
            audit = AuditLogDB(
                contact_id=contact_id,
                action="HARD_DELETE",
                details=f"Permanently deleted contact ID {contact_id}"
            )
            session.add(audit)
            logger.info(f"Hard deleted contact ID {contact_id}")
            return True

    def toggle_favorite(self, contact_id: int) -> Optional[bool]:
        """Toggle favorite status of a contact, returning new state."""
        with get_db_session(self.db_url) as session:
            db_contact = session.query(ContactDB).filter(ContactDB.id == contact_id).first()
            if not db_contact:
                return None
            db_contact.is_favorite = not db_contact.is_favorite
            db_contact.updated_at = datetime.now(timezone.utc)
            new_val = db_contact.is_favorite
            logger.info(f"Toggled favorite for contact ID {contact_id} -> {new_val}")
            return new_val

    # -------------------------------------------------------------
    # QUERY & LISTING OPERATIONS
    # -------------------------------------------------------------
    def get_all_contacts(
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
        """Fetch filtered and paginated contacts list with total count."""
        with get_db_session(self.db_url) as session:
            query = session.query(ContactDB)
            
            if not include_deleted:
                query = query.filter(ContactDB.is_deleted == False)
            if favorites_only:
                query = query.filter(ContactDB.is_favorite == True)
                
            if group_name:
                query = query.filter(ContactDB.groups.any(func.lower(GroupDB.name) == group_name.lower()))
            if tag_name:
                query = query.filter(ContactDB.tags.any(func.lower(TagDB.name) == tag_name.lower()))
                
            total = query.count()
            
            # Sorting
            sort_col = ContactDB.first_name
            if sort_by == "company":
                sort_col = ContactDB.company
            elif sort_by == "created_at":
                sort_col = ContactDB.created_at
            elif sort_by == "updated_at":
                sort_col = ContactDB.updated_at
            elif sort_by == "city":
                sort_col = ContactDB.city
            elif sort_by == "id":
                sort_col = ContactDB.id
                
            query = query.order_by(asc(sort_col) if sort_order.lower() == "asc" else desc(sort_col))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            results = query.all()
            return [self._to_domain(c) for c in results], total

    def search_contacts(
        self,
        search_query: str,
        include_deleted: bool = False,
        favorites_only: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Tuple[List[Contact], int]:
        """Full-text search across name, phone, email, company, city, tags, notes."""
        if not search_query or not search_query.strip():
            return self.get_all_contacts(include_deleted=include_deleted, favorites_only=favorites_only, limit=limit, offset=offset)

        q = f"%{search_query.strip()}%"
        with get_db_session(self.db_url) as session:
            query = session.query(ContactDB).filter(
                or_(
                    ContactDB.first_name.ilike(q),
                    ContactDB.last_name.ilike(q),
                    ContactDB.display_name.ilike(q),
                    ContactDB.phone.ilike(q),
                    ContactDB.alternate_phone.ilike(q),
                    ContactDB.email.ilike(q),
                    ContactDB.company.ilike(q),
                    ContactDB.job_title.ilike(q),
                    ContactDB.city.ilike(q),
                    ContactDB.country.ilike(q),
                    ContactDB.notes.ilike(q),
                    ContactDB.tags.any(TagDB.name.ilike(q)),
                    ContactDB.groups.any(GroupDB.name.ilike(q))
                )
            )
            
            if not include_deleted:
                query = query.filter(ContactDB.is_deleted == False)
            if favorites_only:
                query = query.filter(ContactDB.is_favorite == True)
                
            total = query.count()
            query = query.order_by(asc(ContactDB.first_name))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            results = query.all()
            return [self._to_domain(c) for c in results], total

    def advanced_search(
        self,
        name: Optional[str] = None,
        company: Optional[str] = None,
        city: Optional[str] = None,
        group_name: Optional[str] = None,
        tag_name: Optional[str] = None,
        favorites_only: bool = False,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Tuple[List[Contact], int]:
        """Multi-field advanced search."""
        with get_db_session(self.db_url) as session:
            query = session.query(ContactDB)
            
            if not include_deleted:
                query = query.filter(ContactDB.is_deleted == False)
            if favorites_only:
                query = query.filter(ContactDB.is_favorite == True)
                
            if name and name.strip():
                qn = f"%{name.strip()}%"
                query = query.filter(or_(ContactDB.first_name.ilike(qn), ContactDB.last_name.ilike(qn)))
            if company and company.strip():
                query = query.filter(ContactDB.company.ilike(f"%{company.strip()}%"))
            if city and city.strip():
                query = query.filter(ContactDB.city.ilike(f"%{city.strip()}%"))
            if group_name and group_name.strip():
                query = query.filter(ContactDB.groups.any(func.lower(GroupDB.name) == group_name.strip().lower()))
            if tag_name and tag_name.strip():
                query = query.filter(ContactDB.tags.any(func.lower(TagDB.name) == tag_name.strip().lower()))

            total = query.count()
            query = query.order_by(asc(ContactDB.first_name))
            
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
                
            results = query.all()
            return [self._to_domain(c) for c in results], total

    # -------------------------------------------------------------
    # GROUPS & TAGS
    # -------------------------------------------------------------
    def get_all_groups(self) -> List[Group]:
        """Fetch all groups."""
        with get_db_session(self.db_url) as session:
            groups = session.query(GroupDB).order_by(asc(GroupDB.name)).all()
            return [Group(id=g.id, name=g.name, description=g.description, color=g.color, icon=g.icon) for g in groups]

    def create_group(self, group: Group) -> Group:
        """Create new group."""
        with get_db_session(self.db_url) as session:
            existing = session.query(GroupDB).filter(func.lower(GroupDB.name) == group.name.strip().lower()).first()
            if existing:
                return Group(id=existing.id, name=existing.name, description=existing.description, color=existing.color, icon=existing.icon)
            
            g = GroupDB(name=group.name.strip(), description=group.description, color=group.color, icon=group.icon)
            session.add(g)
            session.flush()
            return Group(id=g.id, name=g.name, description=g.description, color=g.color, icon=g.icon)

    def get_all_tags(self) -> List[Tag]:
        """Fetch all tags."""
        with get_db_session(self.db_url) as session:
            tags = session.query(TagDB).order_by(asc(TagDB.name)).all()
            return [Tag(id=t.id, name=t.name, color=t.color) for t in tags]

    def create_tag(self, tag: Tag) -> Tag:
        """Create new tag."""
        with get_db_session(self.db_url) as session:
            existing = session.query(TagDB).filter(func.lower(TagDB.name) == tag.name.strip().lower()).first()
            if existing:
                return Tag(id=existing.id, name=existing.name, color=existing.color)
            
            t = TagDB(name=tag.name.strip(), color=tag.color)
            session.add(t)
            session.flush()
            return Tag(id=t.id, name=t.name, color=t.color)

    def delete_group(self, group_id: int) -> bool:
        """Delete a group."""
        with get_db_session(self.db_url) as session:
            g = session.query(GroupDB).filter(GroupDB.id == group_id).first()
            if not g:
                return False
            session.delete(g)
            return True

    def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag."""
        with get_db_session(self.db_url) as session:
            t = session.query(TagDB).filter(TagDB.id == tag_id).first()
            if not t:
                return False
            session.delete(t)
            return True

    # -------------------------------------------------------------
    # SETTINGS STORE
    # -------------------------------------------------------------
    def get_setting(self, key: str, default: str = "") -> str:
        """Retrieve setting value."""
        with get_db_session(self.db_url) as session:
            s = session.query(SettingDB).filter(SettingDB.key == key).first()
            return s.value if s else default

    def set_setting(self, key: str, value: str, description: str = "") -> None:
        """Persist or update setting."""
        with get_db_session(self.db_url) as session:
            s = session.query(SettingDB).filter(SettingDB.key == key).first()
            if s:
                s.value = value
                if description:
                    s.description = description
            else:
                s = SettingDB(key=key, value=value, description=description)
                session.add(s)
            session.flush()

    # -------------------------------------------------------------
    # METRICS & STATS
    # -------------------------------------------------------------
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Aggregate key KPI metrics for dashboard."""
        with get_db_session(self.db_url) as session:
            total_active = session.query(func.count(ContactDB.id)).filter(ContactDB.is_deleted == False).scalar() or 0
            total_favorites = session.query(func.count(ContactDB.id)).filter(
                and_(ContactDB.is_deleted == False, ContactDB.is_favorite == True)
            ).scalar() or 0
            total_deleted = session.query(func.count(ContactDB.id)).filter(ContactDB.is_deleted == True).scalar() or 0
            total_groups = session.query(func.count(GroupDB.id)).scalar() or 0
            
            # Missing Fields Count
            missing_email = session.query(func.count(ContactDB.id)).filter(
                and_(ContactDB.is_deleted == False, or_(ContactDB.email == "", ContactDB.email.is_(None)))
            ).scalar() or 0
            missing_phone = session.query(func.count(ContactDB.id)).filter(
                and_(ContactDB.is_deleted == False, or_(ContactDB.phone == "", ContactDB.phone.is_(None)))
            ).scalar() or 0
            
            # Data completeness % (has both email and phone)
            complete_profiles = session.query(func.count(ContactDB.id)).filter(
                and_(
                    ContactDB.is_deleted == False,
                    ContactDB.email != "",
                    ContactDB.email.is_not(None),
                    ContactDB.phone != "",
                    ContactDB.phone.is_not(None)
                )
            ).scalar() or 0
            
            quality_score = int((complete_profiles / total_active * 100)) if total_active > 0 else 100

            return {
                "total_active": total_active,
                "total_favorites": total_favorites,
                "total_deleted": total_deleted,
                "total_groups": total_groups,
                "missing_email": missing_email,
                "missing_phone": missing_phone,
                "complete_profiles": complete_profiles,
                "quality_score": quality_score
            }

    def get_audit_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent audit logs."""
        with get_db_session(self.db_url) as session:
            logs = session.query(AuditLogDB).order_by(desc(AuditLogDB.timestamp)).limit(limit).all()
            return [
                {
                    "id": l.id,
                    "contact_id": l.contact_id,
                    "action": l.action,
                    "details": l.details,
                    "timestamp": l.timestamp
                }
                for l in logs
            ]

    def log_audit(self, action: str, contact_id: Optional[int] = None, details: str = "") -> None:
        """Record an action into the audit trail."""
        with get_db_session(self.db_url) as session:
            audit = AuditLogDB(
                contact_id=contact_id,
                action=action,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(audit)
            session.flush()
