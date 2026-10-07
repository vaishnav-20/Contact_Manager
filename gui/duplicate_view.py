"""
Duplicate Detection & Merge Resolution Page (DuplicateView).
Displays flagged duplicate candidates side-by-side with similarity percentages, match rationales,
and one-click intelligent merge reconciliation.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Optional, Tuple, Dict, Any

from services.duplicate_service import DuplicateService, DuplicateMatch
from services.contact_service import ContactService
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import add_hover_effect


class DuplicateView(tk.Frame):
    """Duplicate Resolution Dashboard View."""

    def __init__(
        self,
        parent: tk.Widget,
        duplicate_service: DuplicateService,
        contact_service: ContactService,
        on_merged_callback: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.duplicate_service = duplicate_service
        self.contact_service = contact_service
        self.on_merged_callback = on_merged_callback

        self._init_ui()
        self.scan_duplicates()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        left_h = tk.Frame(header, bg=COLORS["bg_main"])
        left_h.pack(side="left")

        tk.Label(
            left_h,
            text="🔀  Duplicate Detection & Merge Engine",
            bg=COLORS["bg_main"],
            fg=COLORS["text_white"],
            font=FONTS["title_large"]
        ).pack(anchor="w")

        tk.Label(
            left_h,
            text="Deterministic rules & fuzzy string matching identify redundant contact records.",
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"]
        ).pack(anchor="w", pady=(2, 0))

        btn_rescan = tk.Button(
            header,
            text="🔍  Re-scan Database",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.scan_duplicates
        )
        btn_rescan.pack(side="right")
        add_hover_effect(btn_rescan, COLORS["sapphire_hover"], COLORS["sapphire"])

        # Scrollable container for candidate cards
        canvas_f = tk.Canvas(self, bg=COLORS["bg_main"], highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas_f.yview)
        self.cards_frame = tk.Frame(canvas_f, bg=COLORS["bg_main"], padx=25, pady=10)

        self.cards_frame.bind(
            "<Configure>",
            lambda e: canvas_f.configure(scrollregion=canvas_f.bbox("all"))
        )
        win_id = canvas_f.create_window((0, 0), window=self.cards_frame, anchor="nw")
        canvas_f.configure(yscrollcommand=scroll.set)

        def on_configure(event):
            canvas_f.itemconfig(win_id, width=event.width)
        canvas_f.bind("<Configure>", on_configure)

        canvas_f.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def scan_duplicates(self):
        """Scan and render duplicate cards."""
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        duplicates = self.duplicate_service.find_all_duplicates(threshold=0.75)

        if not duplicates:
            # Clean State Banner
            banner = tk.Frame(self.cards_frame, bg=COLORS["bg_card"], padx=30, pady=40, relief="solid", borderwidth=1)
            banner.pack(fill="x", pady=20)

            tk.Label(banner, text="🎉", bg=COLORS["bg_card"], font=("Segoe UI", 36)).pack()
            tk.Label(banner, text="No Duplicate Contacts Found!", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_medium"]).pack(pady=(10, 4))
            tk.Label(banner, text="All contact names, phone numbers, and email addresses in your database appear distinct.", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body"]).pack()
            return

        # Summary Header
        sum_f = tk.Frame(self.cards_frame, bg=COLORS["bg_main"])
        sum_f.pack(fill="x", pady=(0, 15))
        tk.Label(
            sum_f,
            text=f"⚠️ Found {len(duplicates)} candidate duplicate pair(s). Compare details and merge redundant profiles below:",
            bg=COLORS["bg_main"],
            fg=COLORS["warning"],
            font=FONTS["body_bold"]
        ).pack(anchor="w")

        # Render each candidate pair
        for dup in duplicates:
            self._render_pair_card(dup)

    def _render_pair_card(self, dup: DuplicateMatch):
        """Render side-by-side comparison card."""
        card = tk.Frame(self.cards_frame, bg=COLORS["bg_card"], padx=20, pady=16, relief="solid", borderwidth=1)
        card.pack(fill="x", pady=8)

        # Card Top Header: Similarity Meter & Reasons
        top_f = tk.Frame(card, bg=COLORS["bg_card"])
        top_f.pack(fill="x", pady=(0, 10))

        score_color = COLORS["danger"] if dup.similarity_percentage >= 90 else COLORS["warning"]
        badge = tk.Label(
            top_f,
            text=f"  {dup.similarity_percentage}% MATCH  ",
            bg=score_color,
            fg=COLORS["text_white"],
            font=FONTS["badge"]
        )
        badge.pack(side="left", padx=(0, 10))

        reasons_txt = " • ".join(dup.reasons)
        tk.Label(top_f, text=f"Match Factors: {reasons_txt}", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(side="left")

        # Side by side profiles
        grid_f = tk.Frame(card, bg=COLORS["bg_card"])
        grid_f.pack(fill="x", pady=6)
        grid_f.columnconfigure(0, weight=1)
        grid_f.columnconfigure(1, weight=1)

        # Left: Contact A (Survivor candidate)
        self._render_contact_box(grid_f, "Contact A (Survivor)", dup.primary, col=0, is_primary=True)

        # Right: Contact B (Duplicate)
        self._render_contact_box(grid_f, "Contact B (Duplicate to merge)", dup.secondary, col=1, is_primary=False)

        # Action Buttons for Pair
        actions_f = tk.Frame(card, bg=COLORS["bg_card"])
        actions_f.pack(fill="x", pady=(12, 0))

        btn_merge = tk.Button(
            actions_f,
            text=f"🔀  Smart Merge: Keep {dup.primary.first_name} (ID {dup.primary.id}) & Consolidate",
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=lambda: self._execute_merge(dup.primary.id, dup.secondary.id)
        )
        btn_merge.pack(side="right")
        add_hover_effect(btn_merge, "#047857", COLORS["success"])

    def _render_contact_box(self, parent: tk.Widget, title: str, c, col: int, is_primary: bool):
        """Render single contact info block."""
        box = tk.Frame(parent, bg=COLORS["bg_input"], padx=14, pady=12, relief="solid", borderwidth=1)
        box.grid(row=0, column=col, padx=6, sticky="nsew")

        header_color = COLORS["gold_bright"] if is_primary else COLORS["text_muted"]
        tk.Label(box, text=f"{title} — ID {c.id}", bg=COLORS["bg_input"], fg=header_color, font=FONTS["body_bold"]).pack(anchor="w")

        tk.Label(box, text=c.full_name, bg=COLORS["bg_input"], fg=COLORS["text_white"], font=FONTS["title_small"]).pack(anchor="w", pady=(4, 6))

        info_rows = [
            ("Phone", c.formatted_phone or "None"),
            ("Email", c.email or "None"),
            ("Company", c.company or "None"),
            ("City", c.city or "None"),
            ("Groups", c.groups_str or "None"),
        ]
        for lbl, val in info_rows:
            row = tk.Frame(box, bg=COLORS["bg_input"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{lbl}:", bg=COLORS["bg_input"], fg=COLORS["text_dim"], font=FONTS["micro"], width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=COLORS["bg_input"], fg=COLORS["text_white"], font=FONTS["micro"]).pack(side="left")

    def _execute_merge(self, survivor_id: int, duplicate_id: int):
        """Execute merge through DuplicateService."""
        try:
            merged = self.duplicate_service.merge_contacts(survivor_id, duplicate_id)
            messagebox.showinfo("Merge Complete", f"Successfully merged contact ID {duplicate_id} into ID {survivor_id} ({merged.full_name}).")
            self.scan_duplicates()
            if self.on_merged_callback:
                self.on_merged_callback()
        except Exception as e:
            messagebox.showerror("Merge Error", f"Failed to merge contacts: {e}")
