"""
Executive Dashboard View (DashboardView).
High-level summary KPIs and Recent Contacts, updated for the streamlined layout.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from services.contact_service import ContactService
from services.analytics_service import AnalyticsService
from services.duplicate_service import DuplicateService
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import animate_counter, add_hover_effect

class DashboardView(tk.Frame):
    """Modern Executive Dashboard with KPIs and Contacts list."""

    def __init__(self, parent: tk.Widget, contact_service: ContactService, analytics_service: AnalyticsService, duplicate_service: DuplicateService, nav_callback: Callable[[str], None]):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.contact_service = contact_service
        self.analytics_service = analytics_service
        self.duplicate_service = duplicate_service
        self.nav_callback = nav_callback

        self._init_ui()

    def _init_ui(self):
        # Master Scrollable Canvas
        self.canvas = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scroll_content = tk.Frame(self.canvas, bg=COLORS["bg_main"], padx=25, pady=20)
        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        canvas_container = tk.Frame(self, bg=COLORS["bg_main"])
        canvas_container.pack(fill="both", expand=True)
        
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_win, width=event.width)
        canvas_container.bind("<Configure>", on_canvas_configure)

        canvas_container.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. KPI Cards Row
        self.kpi_container = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        self.kpi_container.pack(fill="x", pady=(0, 20))
        self.kpi_container.columnconfigure((0, 1, 2, 3, 4), weight=1)

        # 2. Bottom Row: Recent Contacts
        self.bottom_container = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        self.bottom_container.pack(fill="both", expand=True, pady=(0, 20))

        self.refresh_data()

    def refresh_data(self):
        """Fetch fresh metrics, update KPI cards, and populate recent contacts."""
        # 1. Update KPI Cards
        for widget in self.kpi_container.winfo_children():
            widget.destroy()

        metrics = self.analytics_service.get_summary_kpis()
        dups = self.duplicate_service.find_all_duplicates()
        metrics["duplicate_alerts"] = len(dups)

        cards_data = [
            ("👥 Total Contacts", metrics["total_active"], "Active in database", COLORS["gold_bright"], lambda: self.nav_callback("contacts")),
            ("⭐ VIP Favorites", metrics["total_favorites"], "Priority starred", COLORS["warning"], lambda: self.nav_callback("favorites")),
            ("📁 Groups & Tags", metrics["total_groups"], "Organizational sets", COLORS["info"], lambda: self.nav_callback("groups")),
            ("🛡️ Quality Score", metrics["quality_score"], "% complete records", COLORS["success"], lambda: self.nav_callback("analytics")),
            ("🔀 Duplicate Alerts", metrics["duplicate_alerts"], "Review & merge", COLORS["danger"] if metrics["duplicate_alerts"] > 0 else COLORS["success"], lambda: self.nav_callback("duplicates")),
        ]

        for idx, (title, val, subtitle, accent_color, click_cmd) in enumerate(cards_data):
            card = tk.Frame(self.kpi_container, bg=COLORS["bg_card"], relief="solid", borderwidth=1, padx=16, pady=14, cursor="hand2")
            card.grid(row=0, column=idx, padx=6, sticky="nsew")
            card.bind("<Button-1>", lambda e, cmd=click_cmd: cmd())

            tk.Label(card, text=title, bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["title_small"]).pack(anchor="w")

            val_label = tk.Label(card, text="0", bg=COLORS["bg_card"], fg=accent_color, font=FONTS["title_large"])
            val_label.pack(anchor="w", pady=(6, 2))
            val_label.bind("<Button-1>", lambda e, cmd=click_cmd: cmd())

            suffix = "%" if "Quality" in title else ""
            animate_counter(val_label, val, duration_ms=450, suffix=suffix)

            sub_lbl = tk.Label(card, text=subtitle, bg=COLORS["bg_card"], fg=COLORS["text_dim"], font=FONTS["micro"])
            sub_lbl.pack(anchor="w")
            sub_lbl.bind("<Button-1>", lambda e, cmd=click_cmd: cmd())

            add_hover_effect(card, COLORS["bg_card_hover"], COLORS["bg_card"])

        # 2. Render Recent Contacts
        for widget in self.bottom_container.winfo_children():
            widget.destroy()

        frame_recent = tk.Frame(self.bottom_container, bg=COLORS["bg_card"], relief="solid", borderwidth=1, padx=12, pady=12)
        frame_recent.pack(fill="both", expand=True, padx=6)

        header_f = tk.Frame(frame_recent, bg=COLORS["bg_card"])
        header_f.pack(fill="x", pady=(0, 10))

        tk.Label(
            header_f,
            text="🕒  Recently Added & Updated Contacts",
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["title_small"]
        ).pack(side="left")
        
        btn_view_all = tk.Button(
            header_f,
            text="View All Contacts ➜",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["micro"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.nav_callback("contacts")
        )
        btn_view_all.pack(side="right")
        add_hover_effect(btn_view_all, COLORS["bg_card_hover"], COLORS["bg_card"])

        # Treeview Configuration
        cols = ("id", "name", "company", "phone", "email")
        self.tree_recent = ttk.Treeview(frame_recent, columns=cols, show="headings", height=12)
        
        self.tree_recent.heading("id", text="ID")
        self.tree_recent.heading("name", text="Contact Name")
        self.tree_recent.heading("company", text="Company / Title")
        self.tree_recent.heading("phone", text="Phone Number")
        self.tree_recent.heading("email", text="Email Address")

        self.tree_recent.column("id", width=60, anchor="center")
        self.tree_recent.column("name", width=180, anchor="w")
        self.tree_recent.column("company", width=160, anchor="w")
        self.tree_recent.column("phone", width=140, anchor="w")
        self.tree_recent.column("email", width=180, anchor="w")

        # Scrollbar
        scroll = ttk.Scrollbar(frame_recent, orient="vertical", command=self.tree_recent.yview)
        self.tree_recent.configure(yscrollcommand=scroll.set)
        
        self.tree_recent.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Load recent contacts data
        contacts, _ = self.contact_service.list_contacts(limit=15)
        for c in contacts:
            fav = "⭐ " if c.is_favorite else ""
            self.tree_recent.insert("", "end", values=(
                f"{c.id:03d}",
                f"{fav}{c.full_name}",
                f"{c.company or '—'}",
                f"{c.formatted_phone or '—'}",
                f"{c.email or '—'}"
            ))
