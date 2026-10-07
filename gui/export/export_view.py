"""
Export Modal / View (ExportView).
Allows users to export contact datasets to CSV, Excel, JSON, or vCard.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Optional

from services.export_service import ExportService
from services.contact_service import ContactService
from models.contact import Contact
from config.settings import AppConfig
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import add_hover_effect


class ExportView(tk.Frame):
    """Export Contacts View."""

    def __init__(self, parent: tk.Widget, contact_service: ContactService):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.contact_service = contact_service

        self._init_ui()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="📤  Export Contacts & Data Backups", bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text="Export all contacts or filtered datasets into CSV, Excel (.xlsx), JSON, or vCard (.vcf) formats.", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # Main Card
        card = tk.Frame(self, bg=COLORS["bg_card"], padx=25, pady=20, relief="solid", borderwidth=1)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # 1. Format Selection
        tk.Label(card, text="1. Select Export Format:", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 8))

        self.format_var = tk.StringVar(value="csv")
        formats = [
            ("csv", "📄  CSV (Comma-Separated Values) — Standard spreadsheet interchange"),
            ("xlsx", "📊  Excel Spreadsheet (.xlsx) — Formatted workbook with columns"),
            ("json", "📦  JSON (JavaScript Object Notation) — Full developer data schema"),
            ("vcf", "👤  vCard (.vcf) — Native address book format for phones & Outlook")
        ]

        for fmt_val, desc in formats:
            rb = tk.Radiobutton(
                card,
                text=desc,
                value=fmt_val,
                variable=self.format_var,
                bg=COLORS["bg_card"],
                fg=COLORS["text_white"],
                selectcolor=COLORS["bg_input"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["gold_bright"],
                font=FONTS["body"]
            )
            rb.pack(anchor="w", pady=3)

        # 2. Scope Selection
        tk.Label(card, text="\n2. Select Export Scope:", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(10, 8))

        self.scope_var = tk.StringVar(value="all")
        scopes = [
            ("all", "👥  Export All Active Database Contacts"),
            ("favorites", "⭐  Export Favorites Only (VIP Priority Contacts)")
        ]
        for scope_val, desc in scopes:
            rb = tk.Radiobutton(
                card,
                text=desc,
                value=scope_val,
                variable=self.scope_var,
                bg=COLORS["bg_card"],
                fg=COLORS["text_white"],
                selectcolor=COLORS["bg_input"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["gold_bright"],
                font=FONTS["body"]
            )
            rb.pack(anchor="w", pady=3)

        # 3. Action Buttons
        actions_f = tk.Frame(card, bg=COLORS["bg_card"])
        actions_f.pack(anchor="w", pady=(25, 0))

        btn_export = tk.Button(
            actions_f,
            text="📤  Choose Destination & Export File",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._execute_export
        )
        btn_export.pack(side="left")
        add_hover_effect(btn_export, COLORS["sapphire_hover"], COLORS["sapphire"])

    def _execute_export(self):
        """Prompt user for save path and write file."""
        fmt = self.format_var.get()
        scope = self.scope_var.get()

        if scope == "favorites":
            contacts, total = self.contact_service.list_contacts(favorites_only=True)
        else:
            contacts, total = self.contact_service.list_contacts(include_deleted=False)

        if total == 0:
            messagebox.showwarning("No Contacts", "There are no contacts available to export.")
            return

        ext_map = {"csv": ".csv", "xlsx": ".xlsx", "json": ".json", "vcf": ".vcf"}
        target_ext = ext_map[fmt]

        dest_file = filedialog.asksaveasfilename(
            title="Save Exported Contacts",
            initialdir=str(AppConfig.EXPORTS_DIR),
            initialfile=f"contacts_export_{fmt}{target_ext}",
            defaultextension=target_ext,
            filetypes=[(f"{fmt.upper()} File", f"*{target_ext}")]
        )
        if not dest_file:
            return

        try:
            out_path = ExportService.export_contacts(contacts, dest_file, file_format=fmt)
            messagebox.showinfo(
                "Export Successful",
                f"🎉 Successfully exported {len(contacts)} contacts!\n\nFile saved at:\n{out_path}"
            )
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export contacts:\n{e}")
