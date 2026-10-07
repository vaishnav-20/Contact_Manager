"""
SQLAlchemy ORM model for the authentication database (data/users.db).
Stores user accounts separately from contact data.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from database.connection import Base


class UserDB(Base):
    """User account table — stored in the shared auth database."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    display_name = Column(String(150), nullable=False, default="")
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
