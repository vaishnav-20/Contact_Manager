"""
Authentication Service — Multi-User Login & Registration.

Uses PBKDF2-HMAC-SHA256 (Python stdlib) for password hashing.
Each registered user gets their own isolated SQLite contact database
at: data/users/<username>.db

No external dependencies needed — works offline in .exe deployment.
"""
import hashlib
import hmac
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from config.settings import AppConfig
from database.connection import get_engine, get_db_session, Base
from utils.logger import get_logger

logger = get_logger("AuthService")

# Auth DB lives in data/users.db (separate from any user's contact DB)
AUTH_DB_PATH = AppConfig.DATA_DIR / "users.db"
AUTH_DB_URL = f"sqlite:///{AUTH_DB_PATH}"

# Per-user contact databases live in data/users/
USERS_DATA_DIR = AppConfig.DATA_DIR / "users"


@dataclass
class UserAccount:
    """Lightweight in-memory user account."""
    id: int
    username: str
    display_name: str
    db_url: str  # SQLite URL for this user's contact database


def _init_auth_db():
    """Ensure the auth database and users table exist."""
    USERS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    from database.auth_models import UserDB  # noqa: imported for side-effect
    engine = get_engine(AUTH_DB_URL)
    Base.metadata.create_all(bind=engine)


def _hash_password(password: str, salt: bytes = None) -> Tuple[str, str]:
    """
    Hash a password with PBKDF2-HMAC-SHA256.
    Returns (hex_hash, hex_salt).
    """
    if salt is None:
        salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=260_000
    )
    return key.hex(), salt.hex()


def _verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """Verify a plaintext password against stored hash and salt."""
    salt = bytes.fromhex(stored_salt)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=260_000
    )
    return hmac.compare_digest(key.hex(), stored_hash)


def _get_user_db_url(username: str) -> str:
    """Return the SQLite URL for a user's personal contact database."""
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", username.lower())
    db_path = USERS_DATA_DIR / f"{safe_name}.db"
    return f"sqlite:///{db_path}"


class AuthService:
    """Manages user registration, login, and per-user DB provisioning."""

    def __init__(self):
        _init_auth_db()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        username: str,
        display_name: str,
        password: str,
        confirm_password: str
    ) -> Tuple[Optional[UserAccount], str]:
        """
        Register a new user account.
        Returns (UserAccount, "") on success, or (None, error_message) on failure.
        """
        # Validate inputs
        username = username.strip()
        display_name = display_name.strip()
        password = password.strip()
        confirm_password = confirm_password.strip()

        if not username:
            return None, "Username cannot be empty."
        if not re.match(r"^[a-zA-Z0-9_.-]{3,30}$", username):
            return None, "Username must be 3–30 characters: letters, digits, _ . - only."
        if not display_name:
            return None, "Display name cannot be empty."
        if len(password) < 6:
            return None, "Password must be at least 6 characters."
        if password != confirm_password:
            return None, "Passwords do not match."

        from database.auth_models import UserDB

        with get_db_session(AUTH_DB_URL) as session:
            existing = session.query(UserDB).filter_by(username=username.lower()).first()
            if existing:
                return None, f"Username '{username}' is already taken. Please choose another."

            pw_hash, pw_salt = _hash_password(password)
            # store as  hash:salt
            combined = f"{pw_hash}:{pw_salt}"

            user_row = UserDB(
                username=username.lower(),
                display_name=display_name,
                password_hash=combined,
                created_at=datetime.now(timezone.utc)
            )
            session.add(user_row)
            session.flush()
            user_id = user_row.id

        db_url = _get_user_db_url(username)
        logger.info(f"Registered new user: {username} (id={user_id})")
        return UserAccount(id=user_id, username=username.lower(), display_name=display_name, db_url=db_url), ""

    def login(self, username: str, password: str) -> Tuple[Optional[UserAccount], str]:
        """
        Authenticate a user.
        Returns (UserAccount, "") on success, (None, error_message) on failure.
        """
        username = username.strip().lower()
        password = password.strip()

        if not username or not password:
            return None, "Please enter both username and password."

        from database.auth_models import UserDB

        with get_db_session(AUTH_DB_URL) as session:
            user_row = session.query(UserDB).filter_by(username=username).first()
            if not user_row:
                return None, "No account found with that username."

            stored = user_row.password_hash
            try:
                pw_hash, pw_salt = stored.split(":", 1)
            except ValueError:
                return None, "Account data corrupted. Please contact support."

            if not _verify_password(password, pw_hash, pw_salt):
                return None, "Incorrect password. Please try again."

            # Update last_login
            user_row.last_login = datetime.now(timezone.utc)
            display = user_row.display_name
            uid = user_row.id

        db_url = _get_user_db_url(username)
        logger.info(f"User logged in: {username}")
        return UserAccount(id=uid, username=username, display_name=display, db_url=db_url), ""

    @staticmethod
    def get_user_db_url(username: str) -> str:
        """Public helper: get a user's contact DB URL."""
        return _get_user_db_url(username)
