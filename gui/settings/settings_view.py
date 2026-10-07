"""
System Settings and User Profile View (SettingsView).
"""
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
import os

from services.auth_service import UserAccount
from config.settings import AppConfig
from gui.theme import COLORS, FONTS
from gui.animations import add_hover_effect

class SettingsView(tk.Frame):
    """System configuration, About, and User Profile controls."""

    def __init__(self, parent: tk.Widget, user: UserAccount, on_logout: Optional[Callable[[], None]] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.user = user
        self.on_logout = on_logout

        self._init_ui()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="⚙️  Settings & Profile", bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text="Manage your account session and application configuration.", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # Main Layout
        main_f = tk.Frame(self, bg=COLORS["bg_main"], padx=25)
        main_f.pack(fill="both", expand=True, pady=(0, 20))
        
        # Grid layout for side-by-side cards
        main_f.columnconfigure(0, weight=1)
        main_f.columnconfigure(1, weight=1)

        # LEFT COLUMN: User Account settings
        col_left = tk.Frame(main_f, bg=COLORS["bg_main"])
        col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        user_box = tk.Frame(col_left, bg=COLORS["bg_card"], padx=20, pady=18, relief="solid", borderwidth=1)
        user_box.pack(fill="x")

        tk.Label(user_box, text="👤  User Profile", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 6))
        
        tk.Label(user_box, text=f"Logged in as: {self.user.display_name} (@{self.user.username})", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_bold"]).pack(anchor="w", pady=(0, 6))
        tk.Label(user_box, text=f"Database: {os.path.basename(self.user.db_url)}", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["micro"]).pack(anchor="w", pady=(0, 12))

        btn_logout = tk.Button(
            user_box,
            text="🚪  Log Out",
            bg=COLORS["danger"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._handle_logout
        )
        btn_logout.pack(anchor="w", pady=(0, 8))
        add_hover_effect(btn_logout, "#991b1b", COLORS["danger"])

        btn_switch = tk.Button(
            user_box,
            text="🔄  Log In / Create New Account",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._handle_logout
        )
        btn_switch.pack(anchor="w")
        add_hover_effect(btn_switch, COLORS["sapphire_hover"], COLORS["sapphire"])

        # RIGHT COLUMN: System Info
        col_right = tk.Frame(main_f, bg=COLORS["bg_main"])
        col_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        sys_box = tk.Frame(col_right, bg=COLORS["bg_card"], padx=20, pady=18, relief="solid", borderwidth=1)
        sys_box.pack(fill="x")

        tk.Label(sys_box, text="ℹ️  System Information", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 10))

        sys_data = [
            ("Version", AppConfig.APP_VERSION),
            ("Build", "Standalone Windows (PyInstaller)"),
            ("Environment", "Offline Mode Enabled"),
            ("Data Directory", AppConfig.USER_DATA_DIR),
            ("Logs Directory", AppConfig.LOGS_DIR)
        ]

        for k, v in sys_data:
            row = tk.Frame(sys_box, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=k + ":", bg=COLORS["bg_card"], fg=COLORS["text_dim"], font=FONTS["body_small"], width=18, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body"]).pack(side="left")

    def _handle_logout(self):
        """Prompt before logging out."""
        if messagebox.askyesno("Log Out", "Are you sure you want to log out of your session?"):
            if self.on_logout:
                self.on_logout()
