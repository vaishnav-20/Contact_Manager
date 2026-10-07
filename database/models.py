"""
SQLAlchemy ORM Data Models for Contact Manager Pro.
Includes tables for contacts, groups, tags, many-to-many associations, audit logs, and settings.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, Index
)
from sqlalchemy.orm import relationship
from database.connection import Base


class ContactGroupDB(Base):
    """Junction table for Contact <-> Group many-to-many relationship."""
    __tablename__ = "contact_groups"
    
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)


class ContactTagDB(Base):
    """Junction table for Contact <-> Tag many-to-many relationship."""
    __tablename__ = "contact_tags"
    
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class GroupDB(Base):
    """Group table for organizational categorizations."""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), default="")
    color = Column(String(20), default="#2563eb")
    icon = Column(String(20), default="📁")
    
    # Relationship
    contacts = relationship("ContactDB", secondary="contact_groups", back_populates="groups")


class TagDB(Base):
    """Tag table for flexible keywords."""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(20), default="#d4af37")
    
    # Relationship
    contacts = relationship("ContactDB", secondary="contact_tags", back_populates="tags")


class ContactDB(Base):
    """Primary Contact database entity."""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Personal
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), default="", index=True)
    display_name = Column(String(200), default="")
    date_of_birth = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)
    profile_photo = Column(String(255), nullable=True)
    
    # Contact
    phone = Column(String(50), default="", index=True)
    alternate_phone = Column(String(50), nullable=True)
    email = Column(String(255), default="", index=True)
    alternate_email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Professional
    company = Column(String(150), default="", index=True)
    job_title = Column(String(150), default="")
    department = Column(String(100), default="")
    
    # Address
    address_line = Column(String(255), default="")
    city = Column(String(100), default="", index=True)
    state = Column(String(100), default="")
    country = Column(String(100), default="")
    postal_code = Column(String(20), default="")
    
    # Organization
    is_favorite = Column(Boolean, default=False, index=True)
    contact_type = Column(String(50), default="Personal")
    
    # Additional
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_contacted = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    groups = relationship("GroupDB", secondary="contact_groups", back_populates="contacts", lazy="joined")
    tags = relationship("TagDB", secondary="contact_tags", back_populates="contacts", lazy="joined")


class AuditLogDB(Base):
    """Audit Log tracking history of operations."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(Integer, nullable=True, index=True)
    action = Column(String(50), nullable=False)   # CREATE, UPDATE, DELETE, RESTORE, MERGE, IMPORT
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class SettingDB(Base):
    """Application preferences and configuration stored in database."""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, default="")
    description = Column(String(255), default="")


# Multi-column indexes for fast composite searches
Index("idx_contact_name_company", ContactDB.first_name, ContactDB.last_name, ContactDB.company)
Index("idx_contact_active_fav", ContactDB.is_deleted, ContactDB.is_favorite)
