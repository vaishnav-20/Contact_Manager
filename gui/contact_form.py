"""
Dedicated Contact Add / Edit Modal Dialog.
Organizes 25+ contact fields into clean categorized tabs with real-time validation and error highlights.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, List

from models.contact import Contact
from services.contact_service import ContactService
from gui.theme import COLORS, FONTS, LABELS


class ContactFormDialog(tk.Toplevel):
    """Add / Edit Contact Modal Dialog."""

    def __init__(
        self,
        parent: tk.Widget,
        contact_service: ContactService,
        contact: Optional[Contact] = None,
        on_saved: Optional[Callable[[Contact], None]] = None
    ):
        super().__init__(parent)
        self.contact_service = contact_service
        self.contact = contact
        self.on_saved = on_saved
        self.is_edit_mode = contact is not None

        title_text = f"✏️  Edit Contact: {contact.full_name}" if self.is_edit_mode else "➕  Add New Contact"
        self.title(title_text)
        self.geometry("680x720")
        self.minsize(620, 640)
        self.configure(bg=COLORS["bg_main"])
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (680 // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (720 // 2)
            self.geometry(f"+{max(10, x)}+{max(10, y)}")
        except Exception:
            pass

        self._init_ui()

    def _init_ui(self):
        # Header banner
        header = tk.Frame(self, bg=COLORS["bg_sidebar"], height=60, padx=20, pady=12)
        header.pack(fill="x")
        
        icon = "✏️" if self.is_edit_mode else "➕"
        heading_text = f"{icon}  {'Edit Contact Details' if self.is_edit_mode else 'Create New Contact'}"
        tk.Label(
            header,
            text=heading_text,
            bg=COLORS["bg_sidebar"],
            fg=COLORS["gold_bright"],
            font=FONTS["title_medium"]
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Fill in contact details below. First name is required.",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"]
        ).pack(anchor="w")

        # Error notification banner (hidden by default)
        self.error_frame = tk.Frame(self, bg=COLORS["danger_bg"], padx=15, pady=8)
        self.error_label = tk.Label(
            self.error_frame,
            text="",
            bg=COLORS["danger_bg"],
            fg="#fecaca",
            font=FONTS["body_bold"],
            wraplength=600,
            justify="left"
        )
        self.error_label.pack(fill="x")

        # Tabbed Notebook
        content_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=20, pady=10)
        content_frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.tab_personal = tk.Frame(self.notebook, bg=COLORS["bg_card"], padx=20, pady=15)
        self.tab_contact = tk.Frame(self.notebook, bg=COLORS["bg_card"], padx=20, pady=15)
        self.tab_pro = tk.Frame(self.notebook, bg=COLORS["bg_card"], padx=20, pady=15)
        self.tab_address = tk.Frame(self.notebook, bg=COLORS["bg_card"], padx=20, pady=15)
        self.tab_org = tk.Frame(self.notebook, bg=COLORS["bg_card"], padx=20, pady=15)
        self.tab_notes = tk.Frame(self.notebook, bg=COLORS["bg_card"], padx=20, pady=15)

        self.notebook.add(self.tab_personal, text="👤 Personal")
        self.notebook.add(self.tab_contact, text="📞 Contact Info")
        self.notebook.add(self.tab_pro, text="💼 Professional")
        self.notebook.add(self.tab_address, text="📍 Address")
        self.notebook.add(self.tab_org, text="🏷️ Organization")
        self.notebook.add(self.tab_notes, text="📝 Notes")

        # Build Fields
        self._build_personal_tab()
        self._build_contact_tab()
        self._build_pro_tab()
        self._build_address_tab()
        self._build_org_tab()
        self._build_notes_tab()

        # Bottom Action Buttons Bar
        actions_bar = tk.Frame(self, bg=COLORS["bg_sidebar"], height=60, padx=20, pady=12)
        actions_bar.pack(fill="x", side="bottom")

        # Save Button (Emerald)
        btn_save = tk.Button(
            actions_bar,
            text=LABELS["ACTION_SAVE"],
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            activebackground="#047857",
            activeforeground=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._save_contact
        )
        btn_save.pack(side="right", padx=(10, 0))

        # Cancel Button
        btn_cancel = tk.Button(
            actions_bar,
            text=LABELS["ACTION_CANCEL"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_white"],
            activebackground=COLORS["bg_card_hover"],
            activeforeground=COLORS["text_white"],
            font=FONTS["body"],
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side="right")

    def _create_entry(self, parent: tk.Widget, label_text: str, row: int, default_val: str = "", required: bool = False) -> tk.Entry:
        """Helper to create labeled input row."""
        lbl = tk.Label(
            parent,
            text=f"{label_text} *" if required else label_text,
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"] if required else COLORS["text_muted"],
            font=FONTS["body_bold"] if required else FONTS["body"],
            anchor="w"
        )
        lbl.grid(row=row*2, column=0, sticky="w", pady=(8, 2))

        entry = tk.Entry(
            parent,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["gold"],
            relief="solid",
            borderwidth=1,
            highlightcolor=COLORS["gold"],
            highlightbackground=COLORS["border"],
            font=FONTS["body"]
        )
        entry.insert(0, default_val or "")
        entry.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 6))
        parent.columnconfigure(0, weight=1)
        return entry

    def _build_personal_tab(self):
        c = self.contact or Contact()
        self.entry_first_name = self._create_entry(self.tab_personal, "First Name", 0, c.first_name, required=True)
        self.entry_last_name = self._create_entry(self.tab_personal, "Last Name", 1, c.last_name)
        self.entry_display_name = self._create_entry(self.tab_personal, "Display Name (Optional)", 2, c.display_name)
        self.entry_dob = self._create_entry(self.tab_personal, "Date of Birth (YYYY-MM-DD)", 3, c.date_of_birth or "")

        # Gender Dropdown
        tk.Label(self.tab_personal, text="Gender", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["body"]).grid(row=8, column=0, sticky="w", pady=(8, 2))
        self.combo_gender = ttk.Combobox(self.tab_personal, values=["Male", "Female", "Other", "Prefer not to say"], state="readonly")
        if c.gender:
            self.combo_gender.set(c.gender)
        self.combo_gender.grid(row=9, column=0, sticky="ew", pady=(0, 6))

    def _build_contact_tab(self):
        c = self.contact or Contact()
        self.entry_phone = self._create_entry(self.tab_contact, "Primary Phone Number", 0, c.phone)
        self.entry_alt_phone = self._create_entry(self.tab_contact, "Alternate Phone Number", 1, c.alternate_phone or "")
        self.entry_email = self._create_entry(self.tab_contact, "Primary Email Address", 2, c.email)
        self.entry_alt_email = self._create_entry(self.tab_contact, "Alternate Email Address", 3, c.alternate_email or "")
        self.entry_website = self._create_entry(self.tab_contact, "Website URL", 4, c.website or "")

    def _build_pro_tab(self):
        c = self.contact or Contact()
        self.entry_company = self._create_entry(self.tab_pro, "Company / Organization", 0, c.company)
        self.entry_job_title = self._create_entry(self.tab_pro, "Job Title / Role", 1, c.job_title)
        self.entry_dept = self._create_entry(self.tab_pro, "Department", 2, c.department)

    def _build_address_tab(self):
        c = self.contact or Contact()
        self.entry_address = self._create_entry(self.tab_address, "Address Line", 0, c.address_line)
        self.entry_city = self._create_entry(self.tab_address, "City", 1, c.city)
        self.entry_state = self._create_entry(self.tab_address, "State / Province", 2, c.state)
        self.entry_country = self._create_entry(self.tab_address, "Country", 3, c.country)
        self.entry_postal = self._create_entry(self.tab_address, "Postal / ZIP Code", 4, c.postal_code)

    def _build_org_tab(self):
        c = self.contact or Contact()
        
        # Favorite Checkbox
        self.var_favorite = tk.BooleanVar(value=c.is_favorite)
        chk_fav = tk.Checkbutton(
            self.tab_org,
            text="⭐  Mark as VIP Priority Favorite",
            variable=self.var_favorite,
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            selectcolor=COLORS["bg_input"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["gold_bright"],
            font=FONTS["body_bold"]
        )
        chk_fav.pack(anchor="w", pady=(5, 15))

        # Groups Checklist
        tk.Label(self.tab_org, text="📁 Assign to Groups:", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_bold"]).pack(anchor="w", pady=(5, 4))
        
        groups_frame = tk.Frame(self.tab_org, bg=COLORS["bg_input"], padx=10, pady=8, relief="solid", borderwidth=1)
        groups_frame.pack(fill="x", pady=(0, 15))

        all_groups = self.contact_service.get_all_groups()
        self.group_vars: Dict[str, tk.BooleanVar] = {}
        
        # Grid layout for groups checkboxes
        for i, g in enumerate(all_groups):
            var = tk.BooleanVar(value=g.name in c.groups)
            self.group_vars[g.name] = var
            chk = tk.Checkbutton(
                groups_frame,
                text=f"{g.icon} {g.name}",
                variable=var,
                bg=COLORS["bg_input"],
                fg=COLORS["text_white"],
                selectcolor=COLORS["bg_main"],
                activebackground=COLORS["bg_input"],
                activeforeground=COLORS["gold"],
                font=FONTS["body"]
            )
            chk.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=4)

        # Tags entry
        tk.Label(self.tab_org, text="🏷️ Tags (comma-separated keywords):", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_bold"]).pack(anchor="w", pady=(5, 2))
        self.entry_tags = tk.Entry(
            self.tab_org,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["gold"],
            relief="solid",
            borderwidth=1,
            font=FONTS["body"]
        )
        self.entry_tags.insert(0, ", ".join(c.tags))
        self.entry_tags.pack(fill="x", pady=(0, 10))

    def _build_notes_tab(self):
        c = self.contact or Contact()
        tk.Label(self.tab_notes, text="Personal Notes / Conversation Log:", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_bold"]).pack(anchor="w", pady=(5, 4))
        
        self.txt_notes = tk.Text(
            self.tab_notes,
            bg=COLORS["bg_input"],
            fg=COLORS["text_white"],
            insertbackground=COLORS["gold"],
            relief="solid",
            borderwidth=1,
            font=FONTS["body"],
            wrap="word",
            height=14
        )
        self.txt_notes.insert("1.0", c.notes or "")
        self.txt_notes.pack(fill="both", expand=True)

    def _save_contact(self):
        """Extract data, validate, and invoke contact service."""
        # 1. Harvest inputs
        first_name = self.entry_first_name.get().strip()
        last_name = self.entry_last_name.get().strip()
        display_name = self.entry_display_name.get().strip()
        dob = self.entry_dob.get().strip() or None
        gender = self.combo_gender.get() or None

        phone = self.entry_phone.get().strip()
        alt_phone = self.entry_alt_phone.get().strip() or None
        email = self.entry_email.get().strip()
        alt_email = self.entry_alt_email.get().strip() or None
        website = self.entry_website.get().strip() or None

        company = self.entry_company.get().strip()
        job_title = self.entry_job_title.get().strip()
        dept = self.entry_dept.get().strip()

        addr = self.entry_address.get().strip()
        city = self.entry_city.get().strip()
        state = self.entry_state.get().strip()
        country = self.entry_country.get().strip()
        postal = self.entry_postal.get().strip()

        is_fav = self.var_favorite.get()
        selected_groups = [name for name, var in self.group_vars.items() if var.get()]
        raw_tags = self.entry_tags.get().strip()
        tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

        notes = self.txt_notes.get("1.0", "end-1c").strip()

        contact_obj = self.contact or Contact()
        contact_obj.first_name = first_name
        contact_obj.last_name = last_name
        contact_obj.display_name = display_name
        contact_obj.date_of_birth = dob
        contact_obj.gender = gender
        contact_obj.phone = phone
        contact_obj.alternate_phone = alt_phone
        contact_obj.email = email
        contact_obj.alternate_email = alt_email
        contact_obj.website = website
        contact_obj.company = company
        contact_obj.job_title = job_title
        contact_obj.department = dept
        contact_obj.address_line = addr
        contact_obj.city = city
        contact_obj.state = state
        contact_obj.country = country
        contact_obj.postal_code = postal
        contact_obj.groups = selected_groups
        contact_obj.tags = tags
        contact_obj.is_favorite = is_fav
        contact_obj.notes = notes

        # 2. Persist through Service
        if self.is_edit_mode:
            saved, errors = self.contact_service.update_contact(contact_obj)
        else:
            saved, errors = self.contact_service.create_contact(contact_obj)

        if errors:
            self.error_frame.pack(fill="x", before=self.notebook, pady=(0, 10))
            self.error_label.configure(text="⚠️ Validation Issues:\n" + "\n".join(f"• {v}" for v in errors.values()))
            return

        # Success callback and close
        if self.on_saved and saved:
            self.on_saved(saved)
            
        self.destroy()
