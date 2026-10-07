"""
Configuration settings for Contact Manager Pro.
Centralizes filesystem paths, database configuration, color palettes, and operational defaults.
"""
import os
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class RoyalPalette:
    """Royal Enterprise Color Palette tokens."""
    # Backgrounds
    BG_MAIN: str = "#0b132b"         # Deepest Midnight Navy
    BG_SIDEBAR: str = "#0d1b2a"      # Royal Sidebar Navy
    BG_CARD: str = "#1c2541"         # Elevated Surface Navy
    BG_CARD_HOVER: str = "#243256"   # Elevated Surface Hover
    BG_INPUT: str = "#131e3a"        # Dark Input Field Background
    
    # Borders & Dividers
    BORDER_SUBTLE: str = "#2b3b5c"   # Subtle Card Border
    BORDER_FOCUS: str = "#d4af37"    # Gold Focus Outline
    DIVIDER: str = "#1f2e4d"         # Thin divider line
    
    # Accents & Royal Colors
    GOLD: str = "#d4af37"            # Imperial Gold Accent
    GOLD_LIGHT: str = "#f3c623"      # Bright Gold for Active States
    GOLD_HOVER: str = "#b89727"      # Dark Gold on Hover
    SAPPHIRE: str = "#2563eb"        # Royal Sapphire Blue
    SAPPHIRE_HOVER: str = "#1d4ed8"  # Dark Sapphire
    INDIGO: str = "#4f46e5"          # Vibrant Royal Indigo
    
    # Status & Semantics
    SUCCESS: str = "#059669"         # Royal Emerald (Add, Valid, Active)
    SUCCESS_BG: str = "#064e3b"      # Success Badge Background
    DANGER: str = "#dc2626"          # Ruby Crimson (Delete, Trash, Error)
    DANGER_BG: str = "#7f1d1d"       # Danger Badge Background
    WARNING: str = "#f59e0b"         # Warm Amber (Favorites, Attention)
    WARNING_BG: str = "#78350f"      # Warning Badge Background
    INFO: str = "#0284c7"            # Sky Info
    
    # Typography
    TEXT_WHITE: str = "#f8fafc"      # High contrast headings & values
    TEXT_MUTED: str = "#94a3b8"      # Subtitles, labels, placeholders
    TEXT_DIM: str = "#64748b"        # Disabled, micro text
    TEXT_GOLD: str = "#f3c623"       # Golden highlight text


class AppConfig:
    """Global Application Configuration."""
    APP_NAME: str = "Contact Manager Pro"
    APP_VERSION: str = "2.0.0"
    AUTHOR: str = "Developer"
    
    # Directory paths
    ROOT_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    BACKUPS_DIR: Path = BASE_DIR / "backups"
    LOGS_DIR: Path = BASE_DIR / "logs"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    
    # File paths
    DATABASE_PATH: Path = DATA_DIR / "contacts.db"
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    LOG_FILE: Path = LOGS_DIR / "application.log"
    APP_ICON_PNG: Path = ASSETS_DIR / "app_icon.png"
    APP_ICON_ICO: Path = ASSETS_DIR / "app_icon.ico"
    
    # Color scheme
    PALETTE = RoyalPalette
    
    # Pagination & Performance
    DEFAULT_PAGE_SIZE: int = 20
    MAX_RECENT_DASHBOARD: int = 8
    
    # Search & Deduplication Thresholds
    DUPLICATE_FUZZY_THRESHOLD: float = 0.82  # 82% similarity triggers candidate match
    
    # Assistant configuration
    AI_ASSISTANT_NAME: str = "ContactAI"
    AI_OFFLINE_MODE: bool = True
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        for path in [cls.DATA_DIR, cls.EXPORTS_DIR, cls.BACKUPS_DIR, cls.LOGS_DIR, cls.ASSETS_DIR]:
            path.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
AppConfig.ensure_directories()
