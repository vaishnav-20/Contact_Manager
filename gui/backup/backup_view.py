"""
Database Backup Management View (BackupView).
Provides atomic database backup/restore controls.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path
from typing import Optional, Callable

from services.backup_service import BackupService
from services.contact_service import ContactService
from config.settings import AppConfig
from gui.theme import COLORS, FONTS
from gui.animations import add_hover_effect


class BackupView(tk.Frame):
    """Backup and Disaster Recovery View."""

    def __init__(self, parent: tk.Widget, backup_service: BackupService, contact_service: ContactService, on_restore_callback: Optional[Callable[[], None]] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.backup_service = backup_service
        self.contact_service = contact_service
        self.on_restore_callback = on_restore_callback

        self._init_ui()
        self.load_backups()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="💾  Database Backup & Recovery", bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text="Create instant atomic SQLite snapshots and restore your personal data if needed.", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # Main Frame
        main_f = tk.Frame(self, bg=COLORS["bg_main"], padx=25)
        main_f.pack(fill="both", expand=True, pady=(0, 20))
        
        backup_box = tk.Frame(main_f, bg=COLORS["bg_card"], padx=20, pady=18, relief="solid", borderwidth=1)
        backup_box.pack(fill="both", expand=True)

        tk.Label(backup_box, text="💾  Disaster Recovery Manager", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 6))
        tk.Label(backup_box, text="Create instant atomic SQLite snapshots without interrupting active use.", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(0, 12))

        btn_create_backup = tk.Button(
            backup_box,
            text="💾  Create Snapshot Now",
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._create_backup
        )
        btn_create_backup.pack(anchor="w", pady=(0, 12))
        add_hover_effect(btn_create_backup, "#047857", COLORS["success"])

        tk.Label(backup_box, text="Historical Backup Restore Points:", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_bold"]).pack(anchor="w", pady=(10, 4))

        # Backups Treeview
        cols = ("filename", "size", "created_at")
        self.tree_backups = ttk.Treeview(backup_box, columns=cols, show="headings", height=12, selectmode="browse")
        self.tree_backups.heading("filename", text="Backup Snapshot")
        self.tree_backups.heading("size", text="Size")
        self.tree_backups.heading("created_at", text="Created On")

        self.tree_backups.column("filename", width=250)
        self.tree_backups.column("size", width=100, anchor="center")
        self.tree_backups.column("created_at", width=180)
        
        scroll = ttk.Scrollbar(backup_box, orient="vertical", command=self.tree_backups.yview)
        self.tree_backups.configure(yscrollcommand=scroll.set)
        
        tree_frame = tk.Frame(backup_box, bg=COLORS["bg_card"])
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.tree_backups.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        btn_restore = tk.Button(
            backup_box,
            text="🔄  Restore Selected Snapshot",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._restore_backup
        )
        btn_restore.pack(anchor="w")
        add_hover_effect(btn_restore, COLORS["sapphire_hover"], COLORS["sapphire"])

    def load_backups(self):
        """Fetch and populate historical backups list."""
        for item in self.tree_backups.get_children():
            self.tree_backups.delete(item)

        backups = self.backup_service.list_backups()
        for b in backups:
            self.tree_backups.insert(
                "",
                "end",
                iid=b["filepath"],
                values=(
                    b["filename"],
                    f"{b['size_kb']} KB",
                    b["created_at"].strftime("%Y-%m-%d %H:%M")
                )
            )

    def _create_backup(self):
        """Create new snapshot."""
        try:
            dest = self.backup_service.create_backup("manual")
            messagebox.showinfo("Backup Created", f"🎉 Snapshot created successfully:\n\n{dest.name}")
            self.load_backups()
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Could not create backup: {e}")

    def _restore_backup(self):
        """Restore chosen snapshot."""
        sel = self.tree_backups.selection()
        if not sel:
            messagebox.showwarning("Select Backup", "Please select a backup from the list to restore.")
            return

        backup_file = sel[0]
        confirm = messagebox.askyesno(
            "⚠️ Confirm Restore",
            f"Are you sure you want to restore:\n\n{Path(backup_file).name}?\n\nThis will replace your current active database.",
            icon="warning"
        )
        if not confirm:
            return

        try:
            self.backup_service.restore_backup(backup_file)
            messagebox.showinfo("Restored", "🎉 Database restored successfully from backup snapshot.")
            if self.on_restore_callback:
                self.on_restore_callback()
        except Exception as e:
            messagebox.showerror("Restore Failed", f"Could not restore database:\n{e}")
