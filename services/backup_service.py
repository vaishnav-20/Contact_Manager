"""
Backup and Disaster Recovery Service for Contact Manager Pro.
Creates atomic snapshots of the SQLite database and handles verified restore operations.
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from config.settings import AppConfig
from utils.logger import get_logger

logger = get_logger("BackupService")


class BackupService:
    """Service managing database backup snapshots and restores."""

    def __init__(self, db_path: Path = None, backup_dir: Path = None):
        self.db_path = db_path or AppConfig.DATABASE_PATH
        self.backup_dir = backup_dir or AppConfig.BACKUPS_DIR
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, custom_label: str = "") -> Path:
        """
        Create atomic backup snapshot using SQLite online backup API.
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Source database file not found at {self.db_path}")

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        label_part = f"_{custom_label.strip()}" if custom_label.strip() else ""
        backup_filename = f"contacts_backup_{timestamp}{label_part}.db"
        dest_path = self.backup_dir / backup_filename

        # Perform atomic online backup using sqlite3.Connection.backup
        src_conn = sqlite3.connect(str(self.db_path))
        dest_conn = sqlite3.connect(str(dest_path))
        try:
            with dest_conn:
                src_conn.backup(dest_conn)
            logger.info(f"Database backup created successfully: {dest_path}")
            return dest_path
        finally:
            dest_conn.close()
            src_conn.close()

    def list_backups(self) -> List[Dict[str, Any]]:
        """Return list of historical backups sorted newest first."""
        backups: List[Dict[str, Any]] = []
        if not self.backup_dir.exists():
            return []

        for p in self.backup_dir.glob("*.db"):
            stat = p.stat()
            size_kb = round(stat.st_size / 1024, 2)
            backups.append({
                "filename": p.name,
                "filepath": str(p),
                "size_kb": size_kb,
                "created_at": datetime.fromtimestamp(stat.st_ctime)
            })

        backups.sort(key=lambda b: b["created_at"], reverse=True)
        return backups

    def restore_backup(self, backup_filepath: str | Path) -> bool:
        """
        Restore database from chosen backup snapshot.
        Verifies backup integrity before replacing active database.
        """
        src_path = Path(backup_filepath)
        if not src_path.exists():
            raise FileNotFoundError(f"Backup file not found at {src_path}")

        # Verify integrity of target backup file
        test_conn = sqlite3.connect(str(src_path))
        try:
            cursor = test_conn.cursor()
            cursor.execute("PRAGMA quick_check")
            result = cursor.fetchone()
            if not result or result[0] != "ok":
                raise ValueError("Backup file failed integrity check.")
        finally:
            test_conn.close()

        # Backup current database as safety restore point before overwriting
        safety_path = self.backup_dir / f"pre_restore_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if self.db_path.exists():
            shutil.copy2(self.db_path, safety_path)

        # Overwrite current DB with backup
        shutil.copy2(src_path, self.db_path)
        logger.info(f"Database successfully restored from: {src_path}")
        return True
