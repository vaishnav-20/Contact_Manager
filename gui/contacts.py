"""
Contacts Directory Page (ContactsView).
Comprehensive grid view with instant full-text search, advanced filter drawer,
explicitly labeled action buttons (with icons & wordings), sorting, and pagination.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List, Dict, Any

from models.contact import Contact
from services.contact_service import ContactService
from services.search_service import SearchService
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import add_hover_effect
from gui.contact_form import ContactFormDialog


class ContactsView(tk.Frame):
    """Full-featured Contacts Directory View."""

    def __init__(
        self,
        parent: tk.Widget,
        contact_service: ContactService,
        search_service: SearchService,
        favorites_only: bool = False
    ):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.contact_service = contact_service
        self.search_service = search_service
        self.favorites_only = favorites_only

        # Pagination state
        self.page = 1
        self.page_size = 15
        self.total_count = 0
        self.sort_by = "name"
        self.sort_order = "asc"
        self.active_search_query = ""
        self.filter_group = None
        self.filter_city = None

        self._init_ui()
        self.load_contacts()

    def _init_ui(self):
        # 1. Top Header Bar
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=12)
        header.pack(fill="x")

        title_text = "⭐  VIP Favorite Contacts" if self.favorites_only else "👥  Contacts Directory"
        sub_text = "High-priority starred contacts" if self.favorites_only else "Manage, search, sort, and organize all contacts."

        tk.Label(header, text=title_text, bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text=sub_text, bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # 2. Search & Toolbar Strip
        toolbar = tk.Frame(self, bg=COLORS["bg_card"], padx=20, pady=10, relief="solid", borderwidth=1)
        toolbar.pack(fill="x", padx=25, pady=(0, 10))

        # Search Bar
        search_f = tk.Frame(toolbar, bg=COLORS["bg_input"], padx=8, pady=4, relief="solid", borderwidth=1)
        search_f.pack(side="left", fill="x", expand=True, padx=(0, 15))

        tk.Label(search_f, text="🔍", bg=COLORS["bg_input"], fg=COLORS["gold"]).pack(side="left", padx=(0, 5))
        self.search_entry = tk.Entry(
            search_f,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["gold"],
            font=FONTS["body"],
            relief="flat"
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        btn_clear_search = tk.Button(
            search_f,
            text="✕",
            bg=COLORS["bg_input"],
            fg=COLORS["text_muted"],
            activebackground=COLORS["bg_input"],
            activeforeground=COLORS["text_white"],
            font=FONTS["body_small"],
            relief="flat",
            cursor="hand2",
            command=self._clear_search
        )
        btn_clear_search.pack(side="right")

        # Action Buttons (Icon + Clear Wordings)
        btn_add = tk.Button(
            toolbar,
            text=LABELS["ACTION_ADD"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._open_add_dialog
        )
        btn_add.pack(side="left", padx=4)
        add_hover_effect(btn_add, "#047857", COLORS["success"])

        btn_edit = tk.Button(
            toolbar,
            text=LABELS["ACTION_EDIT"],
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._edit_selected
        )
        btn_edit.pack(side="left", padx=4)
        add_hover_effect(btn_edit, COLORS["sapphire_hover"], COLORS["sapphire"])

        btn_del = tk.Button(
            toolbar,
            text=LABELS["ACTION_DELETE"],
            bg=COLORS["danger"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._delete_selected
        )
        btn_del.pack(side="left", padx=4)
        add_hover_effect(btn_del, "#b91c1c", COLORS["danger"])

        btn_fav = tk.Button(
            toolbar,
            text=LABELS["ACTION_FAVORITE"],
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["body_bold"],
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._toggle_favorite_selected
        )
        btn_fav.pack(side="left", padx=4)

        btn_refresh = tk.Button(
            toolbar,
            text=LABELS["ACTION_REFRESH"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["body"],
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.load_contacts
        )
        btn_refresh.pack(side="left", padx=4)

        # 3. Main Data Grid (Treeview Table)
        grid_container = tk.Frame(self, bg=COLORS["bg_main"], padx=25)
        grid_container.pack(fill="both", expand=True)

        columns = ("id", "fav", "name", "company", "job_title", "phone", "email", "city", "groups")
        self.tree = ttk.Treeview(grid_container, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID", command=lambda: self._set_sort("id"))
        self.tree.heading("fav", text="⭐", command=lambda: self._set_sort("fav"))
        self.tree.heading("name", text="Full Name", command=lambda: self._set_sort("name"))
        self.tree.heading("company", text="Company", command=lambda: self._set_sort("company"))
        self.tree.heading("job_title", text="Job Title")
        self.tree.heading("phone", text="Phone Number")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("city", text="City / Hub", command=lambda: self._set_sort("city"))
        self.tree.heading("groups", text="Groups")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fav", width=45, anchor="center")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("company", width=140, anchor="w")
        self.tree.column("job_title", width=130, anchor="w")
        self.tree.column("phone", width=125, anchor="w")
        self.tree.column("email", width=180, anchor="w")
        self.tree.column("city", width=100, anchor="w")
        self.tree.column("groups", width=130, anchor="w")

        # Scrollbar for tree
        v_scroll = ttk.Scrollbar(grid_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Double click to edit
        self.tree.bind("<Double-1>", lambda e: self._edit_selected())

        # 4. Pagination Footer Bar
        footer = tk.Frame(self, bg=COLORS["bg_sidebar"], padx=25, pady=8)
        footer.pack(fill="x", side="bottom")

        self.lbl_page_info = tk.Label(footer, text="Showing 0 of 0 contacts", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"], font=FONTS["body_small"])
        self.lbl_page_info.pack(side="left")

        btn_next = tk.Button(footer, text="Next ▶", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_small"], relief="flat", padx=10, pady=3, cursor="hand2", command=self._next_page)
        btn_next.pack(side="right", padx=(5, 0))

        self.lbl_page_num = tk.Label(footer, text="Page 1", bg=COLORS["bg_sidebar"], fg=COLORS["gold_bright"], font=FONTS["body_bold"])
        self.lbl_page_num.pack(side="right", padx=8)

        btn_prev = tk.Button(footer, text="◀ Prev", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_small"], relief="flat", padx=10, pady=3, cursor="hand2", command=self._prev_page)
        btn_prev.pack(side="right", padx=(0, 5))

    def load_contacts(self):
        """Fetch and populate contacts according to active search, filters, and page."""
        offset = (self.page - 1) * self.page_size
        
        if self.active_search_query:
            contacts, total = self.search_service.quick_search(
                self.active_search_query,
                favorites_only=self.favorites_only,
                limit=self.page_size,
                offset=offset
            )
        else:
            contacts, total = self.contact_service.list_contacts(
                favorites_only=self.favorites_only,
                group_name=self.filter_group,
                limit=self.page_size,
                offset=offset,
                sort_by=self.sort_by,
                sort_order=self.sort_order
            )

        self.total_count = total

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert rows
        for c in contacts:
            fav_char = "★" if c.is_favorite else "☆"
            self.tree.insert(
                "",
                "end",
                iid=str(c.id),
                values=(
                    c.id,
                    fav_char,
                    c.full_name,
                    c.company or "—",
                    c.job_title or "—",
                    c.formatted_phone or "—",
                    c.email or "—",
                    c.city or "—",
                    c.groups_str or "—"
                )
            )

        # Update pagination footer
        max_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        start_idx = offset + 1 if total > 0 else 0
        end_idx = min(offset + self.page_size, total)
        self.lbl_page_info.configure(text=f"Showing {start_idx}–{end_idx} of {total} contacts")
        self.lbl_page_num.configure(text=f"Page {self.page} of {max_page}")

    def _on_search_change(self, event=None):
        """Handle dynamic search input."""
        self.active_search_query = self.search_entry.get().strip()
        self.page = 1
        self.load_contacts()

    def _clear_search(self):
        """Clear search query."""
        self.search_entry.delete(0, "end")
        self.active_search_query = ""
        self.page = 1
        self.load_contacts()

    def _set_sort(self, col: str):
        """Toggle column sort order."""
        if self.sort_by == col:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_by = col
            self.sort_order = "asc"
        self.load_contacts()

    def _next_page(self):
        max_page = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        if self.page < max_page:
            self.page += 1
            self.load_contacts()

    def _prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.load_contacts()

    def _get_selected_id(self) -> Optional[int]:
        """Get ID of currently selected row."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Contact", "Please select a contact from the list first.")
            return None
        return int(selected[0])

    def _open_add_dialog(self):
        """Launch Add Contact modal."""
        ContactFormDialog(self.winfo_toplevel(), self.contact_service, on_saved=lambda _: self.load_contacts())

    def _edit_selected(self):
        """Launch Edit Contact modal for selected row."""
        cid = self._get_selected_id()
        if cid is None:
            return
        contact = self.contact_service.get_contact(cid)
        if contact:
            ContactFormDialog(self.winfo_toplevel(), self.contact_service, contact=contact, on_saved=lambda _: self.load_contacts())

    def _delete_selected(self):
        """Delete selected contact with user confirmation."""
        cid = self._get_selected_id()
        if cid is None:
            return
        contact = self.contact_service.get_contact(cid)
        if not contact:
            return

        confirm = messagebox.askyesno(
            "🗑️ Confirm Deletion",
            f"Are you sure you want to delete:\n\n{contact.full_name}\n{contact.company}\n{contact.phone or contact.email}?\n\nThis will safely soft-delete the contact.",
            icon="warning"
        )
        if confirm:
            self.contact_service.delete_contact(cid)
            self.load_contacts()
            messagebox.showinfo("Deleted", f"Contact '{contact.full_name}' was deleted successfully.")

    def _toggle_favorite_selected(self):
        """Toggle favorite state of selected contact."""
        cid = self._get_selected_id()
        if cid is None:
            return
        new_state = self.contact_service.toggle_favorite(cid)
        self.load_contacts()
