"""
Main Application Shell (ContactManagerApp).
Assembles the Royal Sidebar, Header Ribbon, Smooth Page Transitions, and Floating ContactAI Assistant.
Receives an authenticated UserAccount so each user gets their own isolated contact database.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from config.settings import AppConfig
from database.connection import init_db
from database.repository import ContactRepository
from services.contact_service import ContactService
from services.search_service import SearchService
from services.analytics_service import AnalyticsService
from services.duplicate_service import DuplicateService
from services.import_service import ImportService
from services.export_service import ExportService
from services.backup_service import BackupService
from services.ai_assistant_service import AIAssistantService

from gui.theme import COLORS, FONTS, LABELS, apply_royal_theme
from gui.animations import add_hover_effect

# Sub-package imports (organised by feature folder)
from gui.dashboard.dashboard import DashboardView
from gui.contacts.contacts import ContactsView
from gui.contacts.contact_form import ContactFormDialog
from gui.duplicates.duplicate_view import DuplicateView
from gui.groups.groups import GroupsView
from gui.analytics.analytics import AnalyticsView
from gui.assistant.ai_assistant_view import AIAssistantView
from gui.import_wizard.import_view import ImportView
from gui.export.export_view import ExportView
from gui.settings.settings_view import SettingsView
from gui.backup.backup_view import BackupView


class ContactManagerApp:
    """Master Application Window — user-scoped CRM shell."""

    def __init__(
        self,
        user,                          # UserAccount dataclass
        on_logout: Optional[Callable[[], None]] = None,
        root: tk.Tk = None
    ):
        self.user = user
        self.on_logout = on_logout

        self.root = root or tk.Tk()
        self.root.title(f"{AppConfig.APP_NAME} — {user.display_name}")
        self.root.geometry("1280x820")
        self.root.minsize(1050, 680)

        # Set Window Icon
        if AppConfig.APP_ICON_ICO.exists():
            try:
                self.root.iconbitmap(str(AppConfig.APP_ICON_ICO))
            except Exception:
                pass

        # Apply Royal Theme
        apply_royal_theme(self.root)

        # Initialize backend with this user's private database
        init_db(user.db_url)
        self.repo = ContactRepository(db_url=user.db_url)
        self.contact_service = ContactService(self.repo)
        self.search_service = SearchService(self.repo)
        self.duplicate_service = DuplicateService(self.repo)
        self.analytics_service = AnalyticsService(self.repo, self.duplicate_service)
        self.import_service = ImportService(self.repo)
        self.export_service = ExportService()
        self.backup_service = BackupService()
        self.ai_service = AIAssistantService(
            self.contact_service,
            self.search_service,
            self.analytics_service,
            self.duplicate_service,
            self.backup_service
        )

        # Active view state
        self.active_view_key = "dashboard"
        self.views: Dict[str, tk.Widget] = {}
        self.nav_buttons: Dict[str, tk.Button] = {}

        self._build_layout()
        self.show_view("dashboard")

    def _build_layout(self):
        # 1. Main Horizontal Shell: Sidebar + Content Area
        self.shell = tk.Frame(self.root, bg=COLORS["bg_main"])
        self.shell.pack(fill="both", expand=True)

        # 2. Royal Sidebar (Left)
        self.sidebar = tk.Frame(self.shell, bg=COLORS["bg_sidebar"], width=260, padx=12, pady=16)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Section
        brand_f = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        brand_f.pack(fill="x", pady=(0, 6), padx=6)

        tk.Label(
            brand_f,
            text="👑  Contact Manager Pro",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["gold_bright"],
            font=FONTS["title_medium"]
        ).pack(anchor="w")

        tk.Label(
            brand_f,
            text="Executive CRM & Data Platform",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_muted"],
            font=FONTS["micro"]
        ).pack(anchor="w", pady=(2, 0))

        # Current user badge
        user_badge = tk.Frame(self.sidebar, bg=COLORS["bg_input"], padx=10, pady=5, relief="solid", borderwidth=1)
        user_badge.pack(fill="x", padx=4, pady=(6, 4))
        tk.Label(user_badge, text="👤  Logged in as", bg=COLORS["bg_input"], fg=COLORS["text_muted"], font=FONTS["micro"]).pack(anchor="w")
        tk.Label(user_badge, text=self.user.display_name, bg=COLORS["bg_input"], fg=COLORS["gold_bright"], font=FONTS["body_bold"]).pack(anchor="w")

        # Divider
        tk.Frame(self.sidebar, bg=COLORS["divider"], height=1).pack(fill="x", pady=(8, 12))

        # Navigation Links Frame
        self.nav_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        self.nav_frame.pack(fill="x", expand=True, anchor="n")

        nav_items = [
            ("dashboard", LABELS["NAV_DASHBOARD"]),
            ("contacts", LABELS["NAV_CONTACTS"]),
            ("favorites", LABELS["NAV_FAVORITES"]),
            ("groups", LABELS["NAV_GROUPS"]),
            ("analytics", LABELS["NAV_ANALYTICS"]),
            ("duplicates", LABELS["NAV_DUPLICATES"]),
            ("import", LABELS["NAV_IMPORT"]),
            ("export", LABELS["NAV_EXPORT"]),
            ("backup", LABELS["NAV_BACKUP"]),
            ("settings", LABELS["NAV_SETTINGS"]),
        ]

        for key, text in nav_items:
            btn = tk.Button(
                self.nav_frame,
                text=f"  {text}",
                bg=COLORS["bg_sidebar"],
                fg=COLORS["text_white"],
                font=FONTS["body"],
                anchor="w",
                relief="flat",
                padx=12,
                pady=7,
                cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill="x", pady=2)
            add_hover_effect(btn, COLORS["bg_card"], COLORS["bg_sidebar"], hover_fg=COLORS["gold_bright"], normal_fg=COLORS["text_white"])
            self.nav_buttons[key] = btn

        # Sidebar Bottom Section
        bottom_nav = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        bottom_nav.pack(side="bottom", fill="x", pady=(10, 0))

        tk.Frame(bottom_nav, bg=COLORS["divider"], height=1).pack(fill="x", pady=(0, 10))

        # Dedicated AI Assistant Launch Button
        self.btn_ai_launcher = tk.Button(
            bottom_nav,
            text=f"  {LABELS['NAV_ASSISTANT']}",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["body_bold"],
            anchor="w",
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda: self.show_view("assistant")
        )
        self.btn_ai_launcher.pack(fill="x", pady=(0, 6))
        add_hover_effect(self.btn_ai_launcher, COLORS["bg_card_hover"], COLORS["bg_card"])
        self.nav_buttons["assistant"] = self.btn_ai_launcher

        # Logout Button
        btn_logout = tk.Button(
            bottom_nav,
            text="🚪  Logout",
            bg=COLORS["danger"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            anchor="w",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._logout
        )
        btn_logout.pack(fill="x", pady=(0, 8))
        add_hover_effect(btn_logout, "#b91c1c", COLORS["danger"])

        tk.Label(
            bottom_nav,
            text=f"v{AppConfig.APP_VERSION} • 100% Offline Ready",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_dim"],
            font=FONTS["micro"]
        ).pack(anchor="w", padx=6)

        # 3. Main Viewport & Top Header Area (Right)
        self.main_content = tk.Frame(self.shell, bg=COLORS["bg_main"])
        self.main_content.pack(side="right", fill="both", expand=True)

        # Top Universal Bar
        top_bar = tk.Frame(self.main_content, bg=COLORS["bg_card"], height=52, padx=25, relief="solid", borderwidth=1)
        top_bar.pack(fill="x")

        self.lbl_top_count = tk.Label(
            top_bar,
            text="👥  Loading Contacts...",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["body_bold"]
        )
        self.lbl_top_count.pack(side="left", pady=12)

        btn_top_add = tk.Button(
            top_bar,
            text=LABELS["ACTION_ADD"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._open_quick_add
        )
        btn_top_add.pack(side="right", pady=10, padx=(10, 0))
        add_hover_effect(btn_top_add, "#047857", COLORS["success"])

        btn_top_ai = tk.Button(
            top_bar,
            text="🤖 Ask ContactAI",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=lambda: self.show_view("assistant")
        )
        btn_top_ai.pack(side="right", pady=10)
        add_hover_effect(btn_top_ai, COLORS["sapphire_hover"], COLORS["sapphire"])

        # Viewport Frame
        self.view_container = tk.Frame(self.main_content, bg=COLORS["bg_main"])
        self.view_container.pack(fill="both", expand=True)

    def show_view(self, view_key: str):
        """Switch active view with highlight and fresh data."""
        self.active_view_key = view_key

        # Update Navigation Button Highlights
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(bg=COLORS["sapphire"], fg=COLORS["text_white"], font=FONTS["body_bold"])
            else:
                default_bg = COLORS["bg_card"] if k == "assistant" else COLORS["bg_sidebar"]
                default_fg = COLORS["gold_bright"] if k == "assistant" else COLORS["text_white"]
                btn.configure(bg=default_bg, fg=default_fg, font=FONTS["body"])

        # Remove existing view from container
        for widget in self.view_container.winfo_children():
            widget.pack_forget()

        # Instantiate view
        if view_key == "dashboard":
            view = DashboardView(
                self.view_container,
                self.contact_service,
                self.analytics_service,
                self.duplicate_service,
                nav_callback=self.show_view
            )
        elif view_key == "contacts":
            view = ContactsView(
                self.view_container,
                self.contact_service,
                self.search_service,
                favorites_only=False
            )
        elif view_key == "favorites":
            view = ContactsView(
                self.view_container,
                self.contact_service,
                self.search_service,
                favorites_only=True
            )
        elif view_key == "groups":
            view = GroupsView(
                self.view_container,
                self.contact_service,
                nav_callback=self.show_view
            )
        elif view_key == "analytics":
            view = AnalyticsView(
                self.view_container,
                self.analytics_service,
                self.duplicate_service
            )
        elif view_key == "duplicates":
            view = DuplicateView(
                self.view_container,
                self.duplicate_service,
                self.contact_service,
                on_merged_callback=self._on_data_modified
            )
        elif view_key == "import":
            view = ImportView(
                self.view_container,
                self.import_service,
                on_imported_callback=self._on_data_modified
            )
        elif view_key == "export":
            view = ExportView(
                self.view_container,
                self.contact_service
            )
        elif view_key == "backup":
            view = BackupView(
                self.view_container,
                self.backup_service,
                self.contact_service,
                on_restore_callback=self._on_data_modified
            )
        elif view_key == "settings":
            view = SettingsView(
                self.view_container,
                self.user,
                on_logout=self.on_logout
            )
        elif view_key == "assistant":
            view = AIAssistantView(
                self.view_container,
                self.ai_service,
                on_action_done=self._on_data_modified
            )
        else:
            view = tk.Label(
                self.view_container,
                text=f"View '{view_key}' not found",
                bg=COLORS["bg_main"],
                fg="white"
            )

        view.pack(fill="both", expand=True)
        self.update_top_stats()

    def update_top_stats(self):
        """Update top bar contact counter."""
        metrics = self.contact_service.get_dashboard_metrics()
        active = metrics.get("total_active", 0)
        favs = metrics.get("total_favorites", 0)
        self.lbl_top_count.configure(
            text=f"👥  {active} Active Contacts  •  ⭐ {favs} Favorites  •  🛡️ {metrics.get('quality_score', 100)}% Data Quality"
        )

    def _open_quick_add(self):
        """Open Add Contact modal from header."""
        ContactFormDialog(self.root, self.contact_service, on_saved=lambda _: self._on_data_modified())

    def _on_data_modified(self):
        """Refresh current view and top stats when contacts are added/modified/restored."""
        self.update_top_stats()
        self.show_view(self.active_view_key)

    def _logout(self):
        """Log the current user out and return to the login screen."""
        confirm = messagebox.askyesno(
            "Logout",
            f"Are you sure you want to logout, {self.user.display_name}?\n\nYour data is safely saved.",
            icon="question"
        )
        if not confirm:
            return
        self.root.destroy()
        if self.on_logout:
            self.on_logout()

    def run(self):
        """Start Tkinter main event loop."""
        self.root.mainloop()
