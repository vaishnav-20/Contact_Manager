"""
Dedicated Deep-Dive Analytics Cockpit (AnalyticsView).
Features multi-chart Matplotlib canvas visualizations, health indicators, and natural-language insights.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from services.analytics_service import AnalyticsService
from services.duplicate_service import DuplicateService
from gui.theme import COLORS, FONTS, LABELS


class AnalyticsView(tk.Frame):
    """Full Analytics and Business Intelligence View."""

    def __init__(
        self,
        parent: tk.Widget,
        analytics_service: AnalyticsService,
        duplicate_service: DuplicateService
    ):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.analytics_service = analytics_service
        self.duplicate_service = duplicate_service

        self._init_ui()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="📊  Contact Analytics & Network Intelligence", bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text="Deep-dive demographic breakdowns, company distributions, and growth timelines.", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # Scrollable Canvas
        canvas_f = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas_f.yview)
        self.scroll_content = tk.Frame(canvas_f, bg=COLORS["bg_main"], padx=25, pady=10)

        self.scroll_content.bind("<Configure>", lambda e: canvas_f.configure(scrollregion=canvas_f.bbox("all")))
        win_id = canvas_f.create_window((0, 0), window=self.scroll_content, anchor="nw")
        canvas_f.configure(yscrollcommand=scroll.set)

        def on_configure(event):
            canvas_f.itemconfig(win_id, width=event.width)
        canvas_f.bind("<Configure>", on_configure)

        canvas_f.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.render_analytics()

    def render_analytics(self):
        """Render all analytical figures and cards."""
        for widget in self.scroll_content.winfo_children():
            widget.destroy()

        # Row 1: KPI Metrics & Insights Summary
        row1 = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        row1.pack(fill="x", pady=(0, 15))
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=2)

        # Health Card
        kpis = self.analytics_service.get_summary_kpis()
        health_card = tk.Frame(row1, bg=COLORS["bg_card"], padx=18, pady=16, relief="solid", borderwidth=1)
        health_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(health_card, text="🛡️ Data Integrity Metrics", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 8))

        stats = [
            ("Total Database Contacts", f"{kpis['total_active']}"),
            ("Overall Completeness Score", f"{kpis['quality_score']}%"),
            ("Missing Email Addresses", f"{kpis['missing_email']}"),
            ("Missing Phone Numbers", f"{kpis['missing_phone']}"),
            ("Duplicate Alerts", f"{kpis['duplicate_alerts']}"),
        ]
        for label, val in stats:
            rf = tk.Frame(health_card, bg=COLORS["bg_card"])
            rf.pack(fill="x", pady=3)
            tk.Label(rf, text=label, bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body"]).pack(side="left")
            tk.Label(rf, text=val, bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["body_bold"]).pack(side="right")

        # Insights Panel
        insights_panel = tk.Frame(row1, bg=COLORS["bg_card"], padx=18, pady=16, relief="solid", borderwidth=1)
        insights_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(insights_panel, text="💡 Dynamic Network Observations", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 8))
        for ins in self.analytics_service.generate_automated_insights():
            tk.Label(insights_panel, text=ins, bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body"], wraplength=480, justify="left").pack(anchor="w", pady=2)

        # Row 2: Grid of Charts
        charts_grid = tk.Frame(self.scroll_content, bg=COLORS["bg_main"])
        charts_grid.pack(fill="both", expand=True, pady=(0, 20))
        charts_grid.columnconfigure(0, weight=1)
        charts_grid.columnconfigure(1, weight=1)

        # Chart A: Top Companies
        frame_comp = tk.Frame(charts_grid, bg=COLORS["bg_card"], padx=12, pady=12, relief="solid", borderwidth=1)
        frame_comp.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        tk.Label(frame_comp, text="💼  Top Companies in Network", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["title_small"]).pack(anchor="w", padx=5)

        comp_data = self.analytics_service.get_contacts_by_company()
        if not comp_data:
            comp_data = [("General", 1)]

        fig_comp = Figure(figsize=(4.5, 3.2), dpi=95, facecolor=COLORS["bg_card"])
        ax_comp = fig_comp.add_subplot(111)
        ax_comp.set_facecolor(COLORS["bg_card"])

        comps = [c[0] for c in reversed(comp_data[:6])]
        c_counts = [c[1] for c in reversed(comp_data[:6])]
        y_pos = range(len(comps))
        ax_comp.barh(y_pos, c_counts, color=COLORS["sapphire"], height=0.55, edgecolor="#60a5fa", linewidth=1)
        ax_comp.set_yticks(y_pos)
        ax_comp.set_yticklabels(comps, color=COLORS["text_white"], fontsize=9)
        ax_comp.tick_params(axis="x", colors=COLORS["text_muted"], labelsize=8)
        ax_comp.spines["top"].set_visible(False)
        ax_comp.spines["right"].set_visible(False)
        ax_comp.spines["bottom"].set_color(COLORS["border"])
        ax_comp.spines["left"].set_color(COLORS["border"])

        fig_comp.tight_layout()
        canvas_comp = FigureCanvasTkAgg(fig_comp, master=frame_comp)
        canvas_comp.draw()
        canvas_comp.get_tk_widget().pack(fill="both", expand=True)

        # Chart B: Growth Timeline
        frame_trend = tk.Frame(charts_grid, bg=COLORS["bg_card"], padx=12, pady=12, relief="solid", borderwidth=1)
        frame_trend.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=8)
        tk.Label(frame_trend, text="📈  Contact Growth Timeline", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["title_small"]).pack(anchor="w", padx=5)

        trend_data = self.analytics_service.get_monthly_growth_trend()
        if not trend_data:
            trend_data = [("This Month", 1)]

        fig_trend = Figure(figsize=(4.5, 3.2), dpi=95, facecolor=COLORS["bg_card"])
        ax_trend = fig_trend.add_subplot(111)
        ax_trend.set_facecolor(COLORS["bg_card"])

        dates = [t[0] for t in trend_data]
        counts = [t[1] for t in trend_data]
        x_pos = range(len(dates))

        ax_trend.plot(x_pos, counts, marker="o", color=COLORS["gold_bright"], linewidth=2.5, markersize=6)
        ax_trend.fill_between(x_pos, counts, color=COLORS["gold"], alpha=0.25)
        ax_trend.set_xticks(x_pos)
        ax_trend.set_xticklabels(dates, color=COLORS["text_white"], fontsize=8, rotation=20)
        ax_trend.tick_params(axis="y", colors=COLORS["text_muted"], labelsize=8)
        ax_trend.spines["top"].set_visible(False)
        ax_trend.spines["right"].set_visible(False)
        ax_trend.spines["bottom"].set_color(COLORS["border"])
        ax_trend.spines["left"].set_color(COLORS["border"])
        ax_trend.grid(axis="y", color=COLORS["divider"], linestyle="--", linewidth=0.5)

        fig_trend.tight_layout()
        canvas_trend = FigureCanvasTkAgg(fig_trend, master=frame_trend)
        canvas_trend.draw()
        canvas_trend.get_tk_widget().pack(fill="both", expand=True)
