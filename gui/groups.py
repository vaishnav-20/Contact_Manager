"""
Groups & Tags Manager Page (GroupsView).
Allows users to create, color-code, and manage categories and tags, and inspect contacts within each group.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional

from services.contact_service import ContactService
from models.group import Group
from models.tag import Tag
from gui.theme import COLORS, FONTS, LABELS


class GroupsView(tk.Frame):
    """Groups and Tags Organization Management View."""

    def __init__(self, parent: tk.Widget, contact_service: ContactService, nav_callback: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.contact_service = contact_service
        self.nav_callback = nav_callback
        self.selected_group_name = None

        self._init_ui()
        self.load_data()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="📁  Groups & Tags Management", bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text="Organize contacts into high-level categories and custom keywords.", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # Main Split Container
        split_f = tk.Frame(self, bg=COLORS["bg_main"], padx=25)
        split_f.pack(fill="both", expand=True, pady=(0, 15))
        split_f.columnconfigure(0, weight=1)
        split_f.columnconfigure(1, weight=1)

        # 1. Groups Section (Left)
        groups_box = tk.Frame(split_f, bg=COLORS["bg_card"], padx=18, pady=15, relief="solid", borderwidth=1)
        groups_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        gh_frame = tk.Frame(groups_box, bg=COLORS["bg_card"])
        gh_frame.pack(fill="x", pady=(0, 10))
        tk.Label(gh_frame, text="📁  Contact Groups", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(side="left")

        btn_add_group = tk.Button(
            gh_frame,
            text="➕ New Group",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_small"],
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._create_new_group
        )
        btn_add_group.pack(side="right")

        # Groups Listbox
        self.groups_listbox = tk.Listbox(
            groups_box,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            selectbackground=COLORS["sapphire"],
            selectforeground=COLORS["text_white"],
            font=FONTS["body"],
            relief="solid",
            borderwidth=1,
            height=12
        )
        self.groups_listbox.pack(fill="both", expand=True, pady=(0, 10))
        self.groups_listbox.bind("<<ListboxSelect>>", self._on_group_selected)

        btn_del_group = tk.Button(
            groups_box,
            text="🗑️ Delete Selected Group",
            bg=COLORS["bg_card"],
            fg=COLORS["danger"],
            font=FONTS["body_small"],
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._delete_selected_group
        )
        btn_del_group.pack(anchor="w")

        # 2. Tags Section (Right)
        tags_box = tk.Frame(split_f, bg=COLORS["bg_card"], padx=18, pady=15, relief="solid", borderwidth=1)
        tags_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        th_frame = tk.Frame(tags_box, bg=COLORS["bg_card"])
        th_frame.pack(fill="x", pady=(0, 10))
        tk.Label(th_frame, text="🏷️  Keywords & Tags", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(side="left")

        btn_add_tag = tk.Button(
            th_frame,
            text="➕ New Tag",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_small"],
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._create_new_tag
        )
        btn_add_tag.pack(side="right")

        # Tags Listbox
        self.tags_listbox = tk.Listbox(
            tags_box,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            selectbackground=COLORS["sapphire"],
            selectforeground=COLORS["text_white"],
            font=FONTS["body"],
            relief="solid",
            borderwidth=1,
            height=12
        )
        self.tags_listbox.pack(fill="both", expand=True, pady=(0, 10))

        btn_del_tag = tk.Button(
            tags_box,
            text="🗑️ Delete Selected Tag",
            bg=COLORS["bg_card"],
            fg=COLORS["danger"],
            font=FONTS["body_small"],
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._delete_selected_tag
        )
        btn_del_tag.pack(anchor="w")

        # 3. Bottom Preview of Contacts in Selected Group
        preview_box = tk.Frame(self, bg=COLORS["bg_card"], padx=20, pady=12, relief="solid", borderwidth=1)
        preview_box.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        self.lbl_preview_title = tk.Label(
            preview_box,
            text="👥  Contacts in Group",
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            font=FONTS["title_small"]
        )
        self.lbl_preview_title.pack(anchor="w", pady=(0, 8))

        cols = ("id", "name", "company", "phone", "email")
        self.tree_preview = ttk.Treeview(preview_box, columns=cols, show="headings", height=6)
        self.tree_preview.heading("id", text="ID")
        self.tree_preview.heading("name", text="Name")
        self.tree_preview.heading("company", text="Company")
        self.tree_preview.heading("phone", text="Phone")
        self.tree_preview.heading("email", text="Email")

        self.tree_preview.column("id", width=50, anchor="center")
        self.tree_preview.column("name", width=160)
        self.tree_preview.column("company", width=140)
        self.tree_preview.column("phone", width=130)
        self.tree_preview.column("email", width=180)

        self.tree_preview.pack(fill="both", expand=True)

    def load_data(self):
        """Fetch and populate groups, tags, and initial contacts."""
        # Load Groups
        self.groups = self.contact_service.get_all_groups()
        self.groups_listbox.delete(0, "end")
        for g in self.groups:
            self.groups_listbox.insert("end", f"  {g.icon}  {g.name}  —  {g.description or 'No description'}")

        # Load Tags
        self.tags = self.contact_service.get_all_tags()
        self.tags_listbox.delete(0, "end")
        for t in self.tags:
            self.tags_listbox.insert("end", f"  🏷️  {t.name}")

        if self.groups:
            self.groups_listbox.select_set(0)
            self._on_group_selected()

    def _on_group_selected(self, event=None):
        """Update contacts preview when user clicks a group."""
        sel = self.groups_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        selected_group = self.groups[idx]
        self.selected_group_name = selected_group.name
        self.lbl_preview_title.configure(text=f"👥  Contacts in '{selected_group.icon} {selected_group.name}':")

        contacts, _ = self.contact_service.list_contacts(group_name=selected_group.name, limit=50)
        for item in self.tree_preview.get_children():
            self.tree_preview.delete(item)

        for c in contacts:
            self.tree_preview.insert(
                "",
                "end",
                values=(c.id, c.full_name, c.company or "—", c.formatted_phone or "—", c.email or "—")
            )

    def _create_new_group(self):
        """Prompt user for group name and save."""
        name = simpledialog.askstring("➕ New Group", "Enter group name (e.g. Investors, Mentors):", parent=self)
        if name and name.strip():
            self.contact_service.create_group(name=name.strip())
            self.load_data()

    def _create_new_tag(self):
        """Prompt user for tag name and save."""
        name = simpledialog.askstring("➕ New Tag", "Enter tag name (e.g. Lead, VIP):", parent=self)
        if name and name.strip():
            self.contact_service.create_tag(name=name.strip())
            self.load_data()

    def _delete_selected_group(self):
        """Delete chosen group."""
        sel = self.groups_listbox.curselection()
        if not sel:
            return
        g = self.groups[sel[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete group '{g.name}'? (Contacts will not be deleted)"):
            self.contact_service.delete_group(g.id)
            self.load_data()

    def _delete_selected_tag(self):
        """Delete chosen tag."""
        sel = self.tags_listbox.curselection()
        if not sel:
            return
        t = self.tags[sel[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete tag '{t.name}'?"):
            self.contact_service.delete_tag(t.id)
            self.load_data()
