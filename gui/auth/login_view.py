"""
Login & Sign-Up View (LoginView).
Full-screen Royal-themed authentication gate shown before the main app.
Supports: Sign In with existing account / Sign Up to create a new account.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from pathlib import Path

from config.settings import AppConfig
from gui.theme import COLORS, FONTS
from gui.animations import add_hover_effect
from services.auth_service import AuthService, UserAccount


class LoginView:
    """
    Full-screen authentication window.
    On successful login/registration, calls on_success(UserAccount).
    """

    def __init__(self, on_success: Callable[[UserAccount], None]):
        self.on_success = on_success
        self.auth_service = AuthService()

        self.root = tk.Tk()
        self.root.title(f"{AppConfig.APP_NAME} — Login")
        self.root.geometry("520x680")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg_main"])

        # Center window
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 520) // 2
        y = (sh - 680) // 2
        self.root.geometry(f"520x680+{x}+{y}")

        # Set icon
        if AppConfig.APP_ICON_ICO.exists():
            try:
                self.root.iconbitmap(str(AppConfig.APP_ICON_ICO))
            except Exception:
                pass

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build the full login/signup interface."""
        # Outer container with royal border glow
        outer = tk.Frame(self.root, bg=COLORS["gold"], padx=2, pady=2)
        outer.place(relx=0.05, rely=0.04, relwidth=0.90, relheight=0.92)

        inner = tk.Frame(outer, bg=COLORS["bg_card"], padx=30, pady=20)
        inner.pack(fill="both", expand=True)

        # ── Brand Header ──────────────────────────────────────────────
        brand_f = tk.Frame(inner, bg=COLORS["bg_card"])
        brand_f.pack(fill="x", pady=(10, 20))

        tk.Label(
            brand_f,
            text="👑",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=("Segoe UI Emoji", 36)
        ).pack()

        tk.Label(
            brand_f,
            text=AppConfig.APP_NAME,
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["title_large"]
        ).pack()

        tk.Label(
            brand_f,
            text="Enterprise CRM & Intelligence Platform",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"]
        ).pack(pady=(2, 0))

        # ── Divider ───────────────────────────────────────────────────
        tk.Frame(inner, bg=COLORS["gold"], height=1).pack(fill="x", pady=(0, 18))

        # ── Tab Switcher ──────────────────────────────────────────────
        tab_row = tk.Frame(inner, bg=COLORS["bg_main"], relief="solid", borderwidth=1)
        tab_row.pack(fill="x", pady=(0, 20))

        self.mode_var = tk.StringVar(value="login")

        self.btn_tab_login = tk.Button(
            tab_row,
            text="🔐  Sign In",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_mode("login")
        )
        self.btn_tab_login.pack(side="left", fill="x", expand=True)

        self.btn_tab_signup = tk.Button(
            tab_row,
            text="✨  Sign Up",
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
            font=FONTS["body"],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: self._switch_mode("signup")
        )
        self.btn_tab_signup.pack(side="left", fill="x", expand=True)

        # ── Form Container ────────────────────────────────────────────
        self.form_container = tk.Frame(inner, bg=COLORS["bg_card"])
        self.form_container.pack(fill="both", expand=True)

        # Build both forms; show only one at a time
        self._build_login_form()
        self._build_signup_form()

        self._switch_mode("login")

        # ── Footer ────────────────────────────────────────────────────
        tk.Label(
            inner,
            text=f"v{AppConfig.APP_VERSION}  •  100% Offline  •  Royal Enterprise Edition",
            bg=COLORS["bg_card"],
            fg=COLORS["text_dim"],
            font=FONTS["micro"]
        ).pack(pady=(14, 0))

    def _build_login_form(self):
        """Build the Sign In form panel."""
        self.login_frame = tk.Frame(self.form_container, bg=COLORS["bg_card"])

        self._field_label(self.login_frame, "👤  Username")
        self.login_username = self._entry(self.login_frame)

        self._field_label(self.login_frame, "🔒  Password")
        self.login_password = self._entry(self.login_frame, show="●")

        # Status label
        self.login_status = tk.Label(
            self.login_frame,
            text="",
            bg=COLORS["bg_card"],
            fg=COLORS["danger"],
            font=FONTS["body_small"],
            wraplength=380
        )
        self.login_status.pack(pady=(8, 4))

        btn_login = tk.Button(
            self.login_frame,
            text="🔐  Sign In to Contact Manager Pro",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            command=self._do_login
        )
        btn_login.pack(fill="x", pady=(6, 0))
        add_hover_effect(btn_login, COLORS["sapphire_hover"], COLORS["sapphire"])

        # Enter key binding
        self.login_password.bind("<Return>", lambda e: self._do_login())
        self.login_username.bind("<Return>", lambda e: self.login_password.focus())

    def _build_signup_form(self):
        """Build the Sign Up form panel."""
        self.signup_frame = tk.Frame(self.form_container, bg=COLORS["bg_card"])

        self._field_label(self.signup_frame, "👤  Username  (3–30 chars, letters/digits/_/-)")
        self.signup_username = self._entry(self.signup_frame)

        self._field_label(self.signup_frame, "📛  Display Name  (shown in the app)")
        self.signup_display = self._entry(self.signup_frame)

        self._field_label(self.signup_frame, "🔒  Password  (min 6 characters)")
        self.signup_password = self._entry(self.signup_frame, show="●")

        self._field_label(self.signup_frame, "🔒  Confirm Password")
        self.signup_confirm = self._entry(self.signup_frame, show="●")

        # Status label
        self.signup_status = tk.Label(
            self.signup_frame,
            text="",
            bg=COLORS["bg_card"],
            fg=COLORS["danger"],
            font=FONTS["body_small"],
            wraplength=380
        )
        self.signup_status.pack(pady=(6, 4))

        btn_signup = tk.Button(
            self.signup_frame,
            text="✨  Create Account & Get Started",
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            command=self._do_signup
        )
        btn_signup.pack(fill="x", pady=(6, 0))
        add_hover_effect(btn_signup, "#047857", COLORS["success"])

        self.signup_confirm.bind("<Return>", lambda e: self._do_signup())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _field_label(self, parent: tk.Widget, text: str):
        tk.Label(
            parent,
            text=text,
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"],
            anchor="w"
        ).pack(fill="x", pady=(8, 2))

    def _entry(self, parent: tk.Widget, show: str = "") -> tk.Entry:
        e = tk.Entry(
            parent,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["gold_bright"],
            relief="solid",
            borderwidth=1,
            font=FONTS["body"],
            show=show
        )
        e.pack(fill="x", ipady=6)
        return e

    def _switch_mode(self, mode: str):
        """Toggle between login and signup panels."""
        self.mode_var.set(mode)
        if mode == "login":
            self.signup_frame.pack_forget()
            self.login_frame.pack(fill="both", expand=True)
            self.btn_tab_login.configure(bg=COLORS["sapphire"], fg=COLORS["text_white"], font=FONTS["body_bold"])
            self.btn_tab_signup.configure(bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body"])
            self.login_username.focus()
        else:
            self.login_frame.pack_forget()
            self.signup_frame.pack(fill="both", expand=True)
            self.btn_tab_login.configure(bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body"])
            self.btn_tab_signup.configure(bg=COLORS["success"], fg=COLORS["text_white"], font=FONTS["body_bold"])
            self.signup_username.focus()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _do_login(self):
        """Handle Sign In button."""
        self.login_status.configure(text="⏳ Authenticating...", fg=COLORS["text_muted"])
        self.root.update_idletasks()

        username = self.login_username.get()
        password = self.login_password.get()

        user, err = self.auth_service.login(username, password)
        if err:
            self.login_status.configure(text=f"❌  {err}", fg=COLORS["danger"])
            return

        self.login_status.configure(text=f"✅  Welcome back, {user.display_name}!", fg=COLORS["success"])
        self.root.update_idletasks()
        self.root.after(300, lambda: self._on_authenticated(user))

    def _do_signup(self):
        """Handle Sign Up button."""
        self.signup_status.configure(text="⏳ Creating account...", fg=COLORS["text_muted"])
        self.root.update_idletasks()

        username = self.signup_username.get()
        display_name = self.signup_display.get()
        password = self.signup_password.get()
        confirm = self.signup_confirm.get()

        user, err = self.auth_service.register(username, display_name, password, confirm)
        if err:
            self.signup_status.configure(text=f"❌  {err}", fg=COLORS["danger"])
            return

        self.signup_status.configure(text=f"✅  Account created! Welcome, {user.display_name}!", fg=COLORS["success"])
        self.root.update_idletasks()
        self.root.after(400, lambda: self._on_authenticated(user))

    def _on_authenticated(self, user: UserAccount):
        """Destroy login window and hand off to the main app."""
        self.root.destroy()
        self.on_success(user)

    def run(self):
        """Start the Tkinter event loop for the login window."""
        self.root.mainloop()
