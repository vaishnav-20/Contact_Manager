"""
Royal Theme & UI Styling Configuration for Contact Manager Pro.
Defines color tokens, typography, button label standards, and ttk widget styles.
"""
import tkinter as tk
from tkinter import ttk
from config.settings import AppConfig

# -------------------------------------------------------------
# ROYAL COLOR PALETTE
# -------------------------------------------------------------
COLORS = {
    # Surfaces & Backgrounds
    "bg_main": AppConfig.PALETTE.BG_MAIN,          # #0b132b - Deepest Midnight Navy
    "bg_sidebar": AppConfig.PALETTE.BG_SIDEBAR,    # #0d1b2a - Sidebar Navy
    "bg_card": AppConfig.PALETTE.BG_CARD,          # #1c2541 - Elevated Card Surface
    "bg_card_hover": AppConfig.PALETTE.BG_CARD_HOVER,  # #243256
    "bg_input": AppConfig.PALETTE.BG_INPUT,        # #131e3a - Input Field Background
    
    # Borders & Lines
    "border": AppConfig.PALETTE.BORDER_SUBTLE,     # #2b3b5c
    "border_focus": AppConfig.PALETTE.BORDER_FOCUS,# #d4af37 (Gold)
    "divider": AppConfig.PALETTE.DIVIDER,          # #1f2e4d
    
    # Accents & Royal Colors
    "gold": AppConfig.PALETTE.GOLD,                # #d4af37 (Imperial Gold)
    "gold_bright": AppConfig.PALETTE.GOLD_LIGHT,   # #f3c623
    "gold_hover": AppConfig.PALETTE.GOLD_HOVER,    # #b89727
    "sapphire": AppConfig.PALETTE.SAPPHIRE,        # #2563eb (Royal Sapphire)
    "sapphire_hover": AppConfig.PALETTE.SAPPHIRE_HOVER, # #1d4ed8
    "indigo": AppConfig.PALETTE.INDIGO,            # #4f46e5
    
    # Semantic Actions
    "success": AppConfig.PALETTE.SUCCESS,          # #059669 (Royal Emerald)
    "success_bg": AppConfig.PALETTE.SUCCESS_BG,
    "danger": AppConfig.PALETTE.DANGER,            # #dc2626 (Ruby Crimson)
    "danger_bg": AppConfig.PALETTE.DANGER_BG,
    "warning": AppConfig.PALETTE.WARNING,          # #f59e0b (Amber)
    "warning_bg": AppConfig.PALETTE.WARNING_BG,
    "info": AppConfig.PALETTE.INFO,                # #0284c7 (Sky Blue)
    
    # Typography
    "text_white": AppConfig.PALETTE.TEXT_WHITE,    # #f8fafc (Crisp Ivory)
    "text_muted": AppConfig.PALETTE.TEXT_MUTED,    # #94a3b8
    "text_dim": AppConfig.PALETTE.TEXT_DIM,        # #64748b
    "text_gold": AppConfig.PALETTE.TEXT_GOLD,      # #f3c623
}

# -------------------------------------------------------------
# ICON + WORDING DESIGN STANDARDS (NO MYSTERY ICONS)
# -------------------------------------------------------------
LABELS = {
    # Navigation Items
    "NAV_DASHBOARD": "🏠  Executive Cockpit",
    "NAV_CONTACTS": "👥  Contacts Directory",
    "NAV_FAVORITES": "⭐  VIP Favorites",
    "NAV_GROUPS": "📁  Groups & Tags",
    "NAV_ANALYTICS": "📊  Analytics Cockpit",
    "NAV_DUPLICATES": "🔀  Duplicate Detection",
    "NAV_IMPORT": "📥  Import Contacts",
    "NAV_EXPORT": "📤  Export Data",
    "NAV_BACKUP": "💾  Backup & Recovery",
    "NAV_SETTINGS": "⚙️  System Settings",
    "NAV_ASSISTANT": "🤖  ContactAI Assistant",
    
    # Primary Actions
    "ACTION_ADD": "➕ Add New Contact",
    "ACTION_EDIT": "✏️ Edit Details",
    "ACTION_DELETE": "🗑️ Delete Contact",
    "ACTION_FAVORITE": "⭐ Mark Favorite",
    "ACTION_UNFAVORITE": "☆ Remove Favorite",
    "ACTION_MERGE": "🔀 Merge Duplicates",
    "ACTION_SEARCH": "🔍 Search Contacts",
    "ACTION_FILTER": "🔎 Advanced Filter",
    "ACTION_REFRESH": "🔄 Refresh Data",
    "ACTION_SAVE": "💾 Save Contact",
    "ACTION_CANCEL": "❌ Cancel",
    "ACTION_IMPORT_NOW": "📥 Import File",
    "ACTION_EXPORT_NOW": "📤 Export File",
    "ACTION_BACKUP_NOW": "💾 Backup Now",
    "ACTION_RESTORE_NOW": "🔄 Restore Backup",
    "ACTION_VOICE_INPUT": "🎙️ Voice Input",
    "ACTION_SEND_MSG": "🚀 Send",
}

# -------------------------------------------------------------
# TYPOGRAPHY
# -------------------------------------------------------------
FONTS = {
    "title_large": ("Segoe UI", 18, "bold"),
    "title_medium": ("Segoe UI", 14, "bold"),
    "title_small": ("Segoe UI", 11, "bold"),
    "body_bold": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 10),
    "body_small": ("Segoe UI", 9),
    "micro": ("Segoe UI", 8),
    "mono": ("Consolas", 10),
    "badge": ("Segoe UI", 9, "bold"),
}


def apply_royal_theme(root: tk.Tk) -> ttk.Style:
    """Apply royal styling to ttk widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Window background
    root.configure(bg=COLORS["bg_main"])

    # Configure General Styles
    style.configure(".", background=COLORS["bg_main"], foreground=COLORS["text_white"], font=FONTS["body"])
    
    # Frames
    style.configure("Main.TFrame", background=COLORS["bg_main"])
    style.configure("Sidebar.TFrame", background=COLORS["bg_sidebar"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="solid", borderwidth=1)
    
    # Labels
    style.configure("CardTitle.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_muted"], font=FONTS["title_small"])
    style.configure("CardValue.TLabel", background=COLORS["bg_card"], foreground=COLORS["gold_bright"], font=FONTS["title_large"])
    style.configure("Heading.TLabel", background=COLORS["bg_main"], foreground=COLORS["text_white"], font=FONTS["title_medium"])
    style.configure("Muted.TLabel", background=COLORS["bg_main"], foreground=COLORS["text_muted"], font=FONTS["body_small"])

    # Action Buttons
    style.configure(
        "Primary.TButton",
        background=COLORS["sapphire"],
        foreground=COLORS["text_white"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        borderwidth=0
    )
    style.map("Primary.TButton", background=[("active", COLORS["sapphire_hover"])])

    style.configure(
        "Gold.TButton",
        background=COLORS["gold"],
        foreground=COLORS["bg_main"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        borderwidth=0
    )
    style.map("Gold.TButton", background=[("active", COLORS["gold_bright"])])

    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground=COLORS["text_white"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        borderwidth=0
    )
    style.map("Success.TButton", background=[("active", "#047857")])

    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground=COLORS["text_white"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        borderwidth=0
    )
    style.map("Danger.TButton", background=[("active", "#b91c1c")])

    style.configure(
        "Outline.TButton",
        background=COLORS["bg_card"],
        foreground=COLORS["text_white"],
        font=FONTS["body"],
        padding=(10, 5),
        borderwidth=1
    )
    style.map("Outline.TButton", background=[("active", COLORS["bg_card_hover"])])

    # Treeview Table
    style.configure(
        "Treeview",
        background=COLORS["bg_card"],
        foreground=COLORS["text_white"],
        fieldbackground=COLORS["bg_card"],
        rowheight=32,
        font=FONTS["body"],
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["bg_sidebar"],
        foreground=COLORS["gold_bright"],
        font=FONTS["title_small"],
        padding=(8, 6),
        borderwidth=0
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["sapphire"])],
        foreground=[("selected", COLORS["text_white"])]
    )

    # Scrollbars
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["bg_card"],
        troughcolor=COLORS["bg_main"],
        borderwidth=0,
        arrowsize=12
    )

    # Notebook Tabs
    style.configure(
        "TNotebook",
        background=COLORS["bg_main"],
        borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["bg_sidebar"],
        foreground=COLORS["text_muted"],
        font=FONTS["body_bold"],
        padding=(16, 8),
        borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["bg_card"])],
        foreground=[("selected", COLORS["gold_bright"])]
    )

    return style
