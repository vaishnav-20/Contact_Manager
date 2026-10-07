"""
Helper functions and general utilities.
"""
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

def utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)

def sanitize_filename(name: str) -> str:
    """Strip invalid characters for file saving."""
    keepcharacters = (" ", ".", "_", "-")
    return "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()

def ensure_file_dir(filepath: str | Path) -> None:
    """Ensure parent directory of a file exists."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
