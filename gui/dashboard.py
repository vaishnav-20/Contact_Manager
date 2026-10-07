"""
Executive Cockpit & Summarized Home Page (DashboardView).
Features high-impact Qlik/PowerBI-grade KPI tiles with tallying counters, embedded Matplotlib charts,
automated business insight banners, and quick action launch buttons.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from services.contact_service import ContactService
from services.analytics_service import AnalyticsService
from services.duplicate_service import DuplicateService
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import animate_counter, add_hover_effect
from gui.contact_form import ContactFormDialog


class DashboardView(tk.Frame):
    """Summarized Executive Cockpit View."""

    def __init__(
        self,
        parent: tk.Widget,
        contact_service: ContactService,
        analytics_service: AnalyticsService,
        duplicate_service: DuplicateService,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.contact_service = contact_service
        self.analytics_service = analytics_service
        self.duplicate_service = duplicate_service
        self.nav_callback = nav_callback

        self._init_ui()

    def _init_ui(self):
        # Top Header Bar
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        title_frame = tk.Frame(header, bg=COLORS["bg_main"])
        title_frame.pack(side="left")

        tk.Label(
            title_frame,
            text="🏠  Executive Analytics & Summary Cockpit",
            bg=COLORS["bg_main"],
            fg=COLORS["text_white"],
            font=FONTS["title_large"]
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Live overview of your contact ecosystem, data health score, and network intelligence.",
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"]
        ).pack(anchor="w", pady=(2, 0))

        # Action Ribbon (Prominent labeled buttons)
        ribbon = tk.Frame(header, bg=COLORS["bg_main"])
        ribbon.pack(side="right")

        btn_add = tk.Button(
            ribbon,
            text=LABELS["ACTION_ADD"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._open_add_form
        )
        btn_add.pack(side="left", padx=5)
        add_hover_effect(btn_add, "#047857", COLORS["success"])

        btn_import = tk.Button(
            ribbon,
            text=LABELS["NAV_IMPORT"],
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=lambda: self.nav_callback("import")
        )
        btn_import.pack(side="left", padx=5)
        add_hover_effect(btn_import, COLORS["sapphire_hover"], COLORS["sapphire"])

        btn_refresh = tk.Button(
            ribbon,
            text=LABELS["ACTION_REFRESH"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["body"],
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.refresh_data
        )
        btn_refresh.pack(side="left", padx=5)

        # Scrollable Body Container
        canvas_container = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas_container.yview)
        self.scroll_content = tk.Frame(canvas_container, bg=COLORS["bg_main"], padx=25, pady=10)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all"))
        )
        window_id = canvas_container.create_window((0, 0), window=self.scroll_content, anchor="nw")
        canvas_container.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)
        
        # Responsive resize of inner frame width
        def on_canvas_configure(event):
            canvas_container.itemconfig(window_id, width=event.width)
        canvas_container.bind("<Configure>", on_canvas_configure)

        canvas_container.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. KPI Cards Row
        self.kpi_container = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        self.kpi_container.pack(fill="x", pady=(0, 18))
        self.kpi_container.columnconfigure((0, 1, 2, 3, 4), weight=1)

        # 2. Middle Row: Embedded Charts
        self.charts_container = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        self.charts_container.pack(fill="x", pady=(0, 18))
        self.charts_container.columnconfigure(0, weight=1)
        self.charts_container.columnconfigure(1, weight=1)

        # 3. Bottom Row: Insight Engine & Recent Contacts
        self.bottom_container = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        self.bottom_container.pack(fill="both", expand=True, pady=(0, 20))
        self.bottom_container.columnconfigure(0, weight=3)
        self.bottom_container.columnconfigure(1, weight=2)

        self.refresh_data()

    def refresh_data(self):
        """Fetch fresh metrics, update KPI cards, re-render charts, and insights."""
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

            # Animate counter roll
            suffix = "%" if "Quality" in title else ""
            animate_counter(val_label, val, duration_ms=450, suffix=suffix)

            sub_lbl = tk.Label(card, text=subtitle, bg=COLORS["bg_card"], fg=COLORS["text_dim"], font=FONTS["micro"])
            sub_lbl.pack(anchor="w")
            sub_lbl.bind("<Button-1>", lambda e, cmd=click_cmd: cmd())

            add_hover_effect(card, COLORS["bg_card_hover"], COLORS["bg_card"])

        # 2. Render Charts
        self._render_charts()

        # 3. Render Bottom Insight Engine & Recent Contacts
        self._render_bottom_section()

    def _render_charts(self):
        """Render high-contrast Matplotlib visualizations embedded in Tkinter."""
        for widget in self.charts_container.winfo_children():
            widget.destroy()

        # Frame Left: Donut Chart (Groups)
        frame_donut = tk.Frame(self.charts_container, bg=COLORS["bg_card"], relief="solid", borderwidth=1, padx=12, pady=12)
        frame_donut.grid(row=0, column=0, padx=6, sticky="nsew")

        tk.Label(
            frame_donut,
            text="📁  Contact Distribution by Group",
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["title_small"]
        ).pack(anchor="w", padx=5, pady=(0, 5))

        # Matplotlib Donut Chart
        groups_data = self.analytics_service.get_contacts_by_group()
        if not groups_data:
            groups_data = [("General", 1)]

        labels = [g[0] for g in groups_data[:5]]
        counts = [g[1] for g in groups_data[:5]]
        chart_colors = ["#d4af37", "#2563eb", "#059669", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4"]

        fig1 = Figure(figsize=(4.8, 3.2), dpi=95, facecolor=COLORS["bg_card"])
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(COLORS["bg_card"])

        wedges, texts, autotexts = ax1.pie(
            counts,
            labels=labels,
            autopct="%1.0f%%",
            startangle=140,
            pctdistance=0.75,
            colors=chart_colors[:len(counts)],
            textprops={"color": COLORS["text_white"], "fontsize": 8},
            wedgeprops={"width": 0.42, "edgecolor": COLORS["bg_card"], "linewidth": 2}
        )
        for at in autotexts:
            at.set_color(COLORS["bg_main"])
            at.set_fontweight("bold")
            at.set_fontsize(8)

        total_contacts = sum(counts)
        ax1.text(0, 0, f"{total_contacts}\nContacts", ha="center", va="center", color=COLORS["gold_bright"], fontweight="bold", fontsize=10)

        canvas1 = FigureCanvasTkAgg(fig1, master=frame_donut)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        # Frame Right: Top Locations Bar Chart
        frame_bar = tk.Frame(self.charts_container, bg=COLORS["bg_card"], relief="solid", borderwidth=1, padx=12, pady=12)
        frame_bar.grid(row=0, column=1, padx=6, sticky="nsew")

        tk.Label(
            frame_bar,
            text="📍  Top Geographic Hubs (Cities)",
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["title_small"]
        ).pack(anchor="w", padx=5, pady=(0, 5))

        locations_data = self.analytics_service.get_contacts_by_location()
        if not locations_data:
            locations_data = [("Not Specified", 1)]

        cities = [l[0] for l in reversed(locations_data[:5])]
        city_counts = [l[1] for l in reversed(locations_data[:5])]

        fig2 = Figure(figsize=(4.8, 3.2), dpi=95, facecolor=COLORS["bg_card"])
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor(COLORS["bg_card"])

        y_pos = range(len(cities))
        bars = ax2.barh(y_pos, city_counts, color=COLORS["gold"], height=0.55, edgecolor=COLORS["gold_bright"], linewidth=1)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(cities, color=COLORS["text_white"], fontsize=9)
        ax2.tick_params(axis="x", colors=COLORS["text_muted"], labelsize=8)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["bottom"].set_color(COLORS["border"])
        ax2.spines["left"].set_color(COLORS["border"])
        ax2.grid(axis="x", color=COLORS["divider"], linestyle="--", linewidth=0.5)

        # Label numbers on ends of bars
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"{int(width)}",
                     va="center", ha="left", color=COLORS["text_white"], fontsize=8, fontweight="bold")

        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_bar)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)

    def _render_bottom_section(self):
        """Render Insight Engine card and Recent Contacts list."""
        for widget in self.bottom_container.winfo_children():
            widget.destroy()

        # Left: Automated Insight Engine Panel
        insights_card = tk.Frame(self.bottom_container, bg=COLORS["bg_card"], relief="solid", borderwidth=1, padx=18, pady=16)
        insights_card.grid(row=0, column=0, padx=6, sticky="nsew")

        tk.Label(
            insights_card,
            text="💡  Automated AI Business Intelligence",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["title_small"]
        ).pack(anchor="w", pady=(0, 10))

        insights = self.analytics_service.generate_automated_insights()
        for ins in insights:
            row_f = tk.Frame(insights_card, bg=COLORS["bg_card"])
            row_f.pack(fill="x", pady=3)
            tk.Label(
                row_f,
                text=ins,
                bg=COLORS["bg_card"],
                fg=COLORS["text_white"],
                font=FONTS["body"],
                wraplength=480,
                justify="left"
            ).pack(anchor="w")

        # Right: Recent Contacts Mini Table
        recent_card = tk.Frame(self.bottom_container, bg=COLORS["bg_card"], relief="solid", borderwidth=1, padx=16, pady=16)
        recent_card.grid(row=0, column=1, padx=6, sticky="nsew")

        header_f = tk.Frame(recent_card, bg=COLORS["bg_card"])
        header_f.pack(fill="x", pady=(0, 8))
        tk.Label(
            header_f,
            text="🕒  Recent Additions",
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["title_small"]
        ).pack(side="left")

        btn_view_all = tk.Button(
            header_f,
            text="View All ➔",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["body_small"],
            relief="flat",
            cursor="hand2",
            command=lambda: self.nav_callback("contacts")
        )
        btn_view_all.pack(side="right")

        recent_contacts, _ = self.contact_service.list_contacts(limit=5, sort_by="created_at", sort_order="desc")
        if not recent_contacts:
            tk.Label(
                recent_card,
                text="No recent contacts yet.",
                bg=COLORS["bg_card"],
                fg=COLORS["text_muted"],
                font=FONTS["body"]
            ).pack(anchor="w", pady=10)
        else:
            for rc in recent_contacts:
                item_f = tk.Frame(recent_card, bg=COLORS["bg_input"], padx=10, pady=8, relief="solid", borderwidth=1)
                item_f.pack(fill="x", pady=3)

                fav_icon = "⭐ " if rc.is_favorite else ""
                name_lbl = tk.Label(
                    item_f,
                    text=f"{fav_icon}{rc.full_name}",
                    bg=COLORS["bg_input"],
                    fg=COLORS["text_white"],
                    font=FONTS["body_bold"]
                )
                name_lbl.pack(side="left")

                meta_txt = f"{rc.company or 'Personal'} • {rc.formatted_phone or rc.email or 'No info'}"
                tk.Label(
                    item_f,
                    text=meta_txt,
                    bg=COLORS["bg_input"],
                    fg=COLORS["text_muted"],
                    font=FONTS["micro"]
                ).pack(side="right")

    def _open_add_form(self):
        """Open Add Contact modal form."""
        ContactFormDialog(self.winfo_toplevel(), self.contact_service, on_saved=lambda _: self.refresh_data())
