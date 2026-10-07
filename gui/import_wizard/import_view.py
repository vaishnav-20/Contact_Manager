"""
Multi-format Contact Ingestion Wizard (ImportView).
Supports CSV, Excel (.xlsx), JSON, and vCard files with schema detection,
fuzzy column mapping preview, duplicate filtering, and batch commit.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from services.import_service import ImportService
from services.contact_service import ContactService
from gui.theme import COLORS, FONTS, LABELS
from gui.animations import add_hover_effect


class ImportView(tk.Frame):
    """Four-step Contact Import Wizard."""

    def __init__(self, parent: tk.Widget, import_service: ImportService, on_imported_callback: Optional[Callable[[], None]] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.import_service = import_service
        self.on_imported_callback = on_imported_callback

        self.selected_file_path: Optional[Path] = None
        self.raw_records: List[Dict[str, Any]] = []
        self.file_headers: List[str] = []
        self.mapping_combos: Dict[str, ttk.Combobox] = {}

        self._init_ui()

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], padx=25, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="📥  Data Import Pipeline & Schema Mapping", bg=COLORS["bg_main"], fg=COLORS["text_white"], font=FONTS["title_large"]).pack(anchor="w")
        tk.Label(header, text="Batch import contacts from CSV, Excel (.xlsx), JSON, or vCard (.vcf) files.", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["body_small"]).pack(anchor="w", pady=(2, 0))

        # Main Card Frame
        self.card = tk.Frame(self, bg=COLORS["bg_card"], padx=25, pady=20, relief="solid", borderwidth=1)
        self.card.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # Step 1: File Selection Strip
        s1 = tk.Frame(self.card, bg=COLORS["bg_card"])
        s1.pack(fill="x", pady=(0, 15))

        tk.Label(s1, text="Step 1: Choose Source File (CSV, Excel, JSON, vCard)", bg=COLORS["bg_card"], fg=COLORS["gold_bright"], font=FONTS["title_small"]).pack(anchor="w", pady=(0, 8))

        browse_row = tk.Frame(s1, bg=COLORS["bg_card"])
        browse_row.pack(fill="x")

        self.lbl_filename = tk.Label(
            browse_row,
            text="No file selected yet. Supported formats: .csv, .xlsx, .json, .vcf",
            bg=COLORS["bg_input"],
            fg=COLORS["text_muted"],
            font=FONTS["body"],
            padx=12,
            pady=8,
            relief="solid",
            borderwidth=1
        )
        self.lbl_filename.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = tk.Button(
            browse_row,
            text="📂  Browse File...",
            bg=COLORS["sapphire"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._browse_file
        )
        btn_browse.pack(side="right")
        add_hover_effect(btn_browse, COLORS["sapphire_hover"], COLORS["sapphire"])

        # Step 2: Column Mapping Frame
        self.step2_frame = tk.Frame(self.card, bg=COLORS["bg_card"])
        self.step2_frame.pack(fill="both", expand=True, pady=(10, 0))

    def _browse_file(self):
        """Open file dialog and parse selected file."""
        file_path = filedialog.askopenfilename(
            title="Select Contacts File to Import",
            filetypes=[
                ("All Supported Files", "*.csv;*.xlsx;*.xls;*.json;*.vcf"),
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx;*.xls"),
                ("JSON Files", "*.json"),
                ("vCard Files", "*.vcf;*.vcard")
            ]
        )
        if not file_path:
            return

        self.selected_file_path = Path(file_path)
        self.lbl_filename.configure(text=f"Selected: {self.selected_file_path.name} ({self.selected_file_path.stat().st_size} bytes)", fg=COLORS["text_white"])

        try:
            records, headers = self.import_service.parse_file(self.selected_file_path)
            self.raw_records = records
            self.file_headers = headers
            self._render_column_mapping_step()
        except Exception as e:
            messagebox.showerror("File Parsing Error", f"Could not parse selected file:\n{e}")

    def _render_column_mapping_step(self):
        """Build column mapping UI using smart mapping."""
        for widget in self.step2_frame.winfo_children():
            widget.destroy()

        # Step 2 Header
        tk.Label(
            self.step2_frame,
            text=f"Step 2: Verify Smart Column Mapping ({len(self.raw_records)} records detected)",
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            font=FONTS["title_small"]
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            self.step2_frame,
            text="Our AI schema engine matched your file columns below. Adjust if necessary:",
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            font=FONTS["body_small"]
        ).pack(anchor="w", pady=(0, 10))

        # Detect Mappings
        auto_mappings = self.import_service.detect_column_mapping(self.file_headers)

        # Mapping Grid inside scrollable frame
        map_canvas = tk.Canvas(self.step2_frame, bg=COLORS["bg_card"], highlightthickness=0, height=200)
        map_scroll = ttk.Scrollbar(self.step2_frame, orient="vertical", command=map_canvas.yview)
        inner_map = tk.Frame(map_canvas, bg=COLORS["bg_card"])

        inner_map.bind("<Configure>", lambda e: map_canvas.configure(scrollregion=map_canvas.bbox("all")))
        map_canvas.create_window((0, 0), window=inner_map, anchor="nw")
        map_canvas.configure(yscrollcommand=map_scroll.set)

        map_canvas.pack(fill="x", pady=(0, 15))
        map_scroll.pack(side="right", fill="y")

        standard_fields = [
            "(Ignore Column)",
            "first_name", "last_name", "display_name", "phone", "alternate_phone",
            "email", "alternate_email", "company", "job_title", "department",
            "address_line", "city", "state", "country", "postal_code",
            "notes", "groups", "tags", "date_of_birth", "website"
        ]

        self.mapping_combos.clear()
        for i, header in enumerate(self.file_headers):
            row_f = tk.Frame(inner_map, bg=COLORS["bg_card"])
            row_f.pack(fill="x", pady=2)

            tk.Label(row_f, text=f"File Header: '{header}'", bg=COLORS["bg_card"], fg=COLORS["text_white"], font=FONTS["body_bold"], width=28, anchor="w").pack(side="left")
            tk.Label(row_f, text="➔  Maps To:", bg=COLORS["bg_card"], fg=COLORS["gold"], font=FONTS["body_small"], width=12).pack(side="left")

            combo = ttk.Combobox(row_f, values=standard_fields, state="readonly", width=22)
            detected = auto_mappings.get(header)
            combo.set(detected if detected and detected in standard_fields else "(Ignore Column)")
            combo.pack(side="left")

            self.mapping_combos[header] = combo

        # Step 3: Options & Execution
        s3 = tk.Frame(self.step2_frame, bg=COLORS["bg_card"])
        s3.pack(fill="x", pady=(10, 0))

        self.var_skip_duplicates = tk.BooleanVar(value=True)
        chk_skip = tk.Checkbutton(
            s3,
            text="🛡️  Automatically skip records matching existing Phone numbers or Emails",
            variable=self.var_skip_duplicates,
            bg=COLORS["bg_card"],
            fg=COLORS["gold_bright"],
            selectcolor=COLORS["bg_input"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["gold_bright"],
            font=FONTS["body_bold"]
        )
        chk_skip.pack(anchor="w", pady=(0, 15))

        btn_import = tk.Button(
            s3,
            text=f"📥  Start Batch Import ({len(self.raw_records)} Records)",
            bg=COLORS["success"],
            fg=COLORS["text_white"],
            font=FONTS["body_bold"],
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._execute_import
        )
        btn_import.pack(anchor="w")
        add_hover_effect(btn_import, "#047857", COLORS["success"])

    def _execute_import(self):
        """Execute the batch import using configured mappings."""
        final_mapping = {}
        for header, combo in self.mapping_combos.items():
            val = combo.get()
            final_mapping[header] = None if val == "(Ignore Column)" else val

        try:
            summary = self.import_service.import_records(
                records=self.raw_records,
                column_mapping=final_mapping,
                skip_duplicates=self.var_skip_duplicates.get()
            )

            msg = (
                f"🎉 Batch Ingestion Finished!\n\n"
                f"• Total Rows Processed: {summary['total_rows']}\n"
                f"• Successfully Imported: {summary['imported_count']}\n"
                f"• Duplicates Skipped: {summary['skipped_duplicate_count']}\n"
                f"• Invalid Rows: {summary['invalid_count']}"
            )
            messagebox.showinfo("Import Complete", msg)

            if self.on_imported_callback:
                self.on_imported_callback()

        except Exception as e:
            messagebox.showerror("Import Failed", f"An error occurred during import:\n{e}")
