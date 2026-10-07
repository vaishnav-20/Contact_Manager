"""
Multi-format Contact Export Service.
Exports contacts into CSV, Excel (.xlsx), JSON, and vCard (.vcf) files, supporting both
entire database backups and targeted filtered search subsets.
"""
import os
import csv
import json
from pathlib import Path
from typing import List, Optional
import pandas as pd

from models.contact import Contact
from config.settings import AppConfig
from utils.logger import get_logger

logger = get_logger("ExportService")


class ExportService:
    """Service handling multi-format contact exporting."""

    @staticmethod
    def export_contacts(
        contacts: List[Contact],
        output_filepath: str | Path,
        file_format: Optional[str] = None
    ) -> Path:
        """
        Export contacts to target filepath.
        Format is inferred from file extension unless explicitly provided.
        """
        path = Path(output_filepath)
        os.makedirs(path.parent, exist_ok=True)
        
        fmt = (file_format or path.suffix.replace(".", "")).lower()

        if fmt == "csv":
            ExportService._export_csv(contacts, path)
        elif fmt in ["xlsx", "excel"]:
            ExportService._export_excel(contacts, path)
        elif fmt == "json":
            ExportService._export_json(contacts, path)
        elif fmt in ["vcf", "vcard"]:
            ExportService._export_vcard(contacts, path)
        else:
            raise ValueError(f"Unsupported export format '{fmt}'. Choose from: csv, xlsx, json, vcf.")

        logger.info(f"Successfully exported {len(contacts)} contacts to {path}")
        return path

    @staticmethod
    def _export_csv(contacts: List[Contact], path: Path) -> None:
        """Export contacts to CSV."""
        rows = [c.to_dict() for c in contacts]
        if not rows:
            # Write empty header
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                f.write("first_name,last_name,phone,email,company\n")
            return

        # Flatten groups and tags lists to comma-separated strings
        for r in rows:
            r["groups"] = ", ".join(r.get("groups", []))
            r["tags"] = ", ".join(r.get("tags", []))

        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, encoding="utf-8-sig")

    @staticmethod
    def _export_excel(contacts: List[Contact], path: Path) -> None:
        """Export contacts to Excel spreadsheet (.xlsx)."""
        rows = [c.to_dict() for c in contacts]
        for r in rows:
            r["groups"] = ", ".join(r.get("groups", []))
            r["tags"] = ", ".join(r.get("tags", []))

        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["first_name", "last_name", "phone", "email", "company"])
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Contacts")

    @staticmethod
    def _export_json(contacts: List[Contact], path: Path) -> None:
        """Export contacts to JSON."""
        data = [c.to_dict() for c in contacts]
        with open(path, mode="w", encoding="utf-8") as f:
            json.dump({"contacts": data, "count": len(data)}, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _export_vcard(contacts: List[Contact], path: Path) -> None:
        """Export contacts to vCard 3.0."""
        cards = []
        for c in contacts:
            lines = [
                "BEGIN:VCARD",
                "VERSION:3.0",
                f"N:{c.last_name};{c.first_name};;;",
                f"FN:{c.full_name}",
            ]
            if c.company:
                lines.append(f"ORG:{c.company};{c.department}")
            if c.job_title:
                lines.append(f"TITLE:{c.job_title}")
            if c.phone:
                lines.append(f"TEL;TYPE=CELL,VOICE:{c.phone}")
            if c.alternate_phone:
                lines.append(f"TEL;TYPE=WORK,VOICE:{c.alternate_phone}")
            if c.email:
                lines.append(f"EMAIL;TYPE=PREF,INTERNET:{c.email}")
            if c.alternate_email:
                lines.append(f"EMAIL;TYPE=WORK,INTERNET:{c.alternate_email}")
            if c.website:
                lines.append(f"URL:{c.website}")
            if c.address_line or c.city or c.country:
                lines.append(f"ADR;TYPE=HOME:;;{c.address_line};{c.city};{c.state};{c.postal_code};{c.country}")
            if c.notes:
                clean_note = c.notes.replace("\n", "\\n")
                lines.append(f"NOTE:{clean_note}")
            lines.append("END:VCARD")
            cards.append("\n".join(lines))

        with open(path, mode="w", encoding="utf-8") as f:
            f.write("\n\n".join(cards))
