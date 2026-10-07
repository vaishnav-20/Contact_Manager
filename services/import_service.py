"""
Smart Import Pipeline for Contact Manager Pro.
Supports CSV, Excel (.xlsx), JSON, and vCard (.vcf) formats with schema detection,
fuzzy column header synonyms mapping, normalization, and validation.
"""
import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher
import pandas as pd

from database.repository import ContactRepository
from models.contact import Contact
from services.validation_service import ValidationService
from utils.logger import get_logger

logger = get_logger("ImportService")

# Known synonyms for smart header mapping
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "first_name": ["first_name", "firstname", "first", "given_name", "fname", "forename"],
    "last_name": ["last_name", "lastname", "last", "surname", "family_name", "lname"],
    "display_name": ["display_name", "fullname", "full_name", "contact_name", "name"],
    "phone": ["phone", "mobile", "mobile_number", "cell", "cell_phone", "contact_no", "telephone", "phone_number", "tel"],
    "alternate_phone": ["alt_phone", "alternate_phone", "home_phone", "secondary_phone", "work_phone"],
    "email": ["email", "e_mail", "mail", "email_address", "electronic_mail"],
    "alternate_email": ["alt_email", "alternate_email", "secondary_email", "work_email"],
    "company": ["company", "organization", "organisation", "employer", "workplace", "business", "company_name"],
    "job_title": ["job_title", "title", "designation", "position", "role", "occupation"],
    "department": ["department", "dept", "division", "team"],
    "address_line": ["address", "address_line", "street", "street_address", "address_1"],
    "city": ["city", "town", "locality", "city_name"],
    "state": ["state", "province", "region"],
    "country": ["country", "nation"],
    "postal_code": ["postal_code", "zip", "zip_code", "pincode", "pin_code", "postcode"],
    "notes": ["notes", "note", "comments", "description", "remarks", "about"],
    "groups": ["groups", "group", "category", "categories"],
    "tags": ["tags", "tag", "labels", "keywords"],
    "is_favorite": ["favorite", "is_favorite", "starred", "vip"],
    "date_of_birth": ["dob", "date_of_birth", "birthday", "birth_date"],
    "gender": ["gender", "sex"],
    "website": ["website", "web", "url", "homepage", "blog"]
}


class ImportService:
    """Service handling multi-format contact ingestion with smart schema mapping."""

    def __init__(self, repo: ContactRepository = None):
        self.repo = repo or ContactRepository()

    @staticmethod
    def detect_column_mapping(headers: List[str]) -> Dict[str, Optional[str]]:
        """
        Map discovered file headers to standard Contact fields.
        Returns:
            Dict[file_header, contact_field]
        """
        mapping: Dict[str, Optional[str]] = {}
        cleaned_headers = [h.strip().lower().replace(" ", "_").replace("-", "_") for h in headers]

        for orig_header, clean in zip(headers, cleaned_headers):
            matched_field = None
            best_sim = 0.0

            # 1. Exact synonym check
            for standard_field, syn_list in COLUMN_SYNONYMS.items():
                if clean in syn_list:
                    matched_field = standard_field
                    break

            # 2. Fuzzy synonym check if no exact match
            if not matched_field:
                for standard_field, syn_list in COLUMN_SYNONYMS.items():
                    for syn in syn_list:
                        sim = SequenceMatcher(None, clean, syn).ratio()
                        if sim > 0.85 and sim > best_sim:
                            best_sim = sim
                            matched_field = standard_field

            mapping[orig_header] = matched_field

        return mapping

    def parse_file(self, filepath: str | Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Read file and return raw records list and header list.
        Supports .csv, .xlsx, .xls, .json, .vcf.
        """
        path = Path(filepath)
        ext = path.suffix.lower()

        if ext == ".csv":
            return self._parse_csv(path)
        elif ext in [".xlsx", ".xls"]:
            return self._parse_excel(path)
        elif ext == ".json":
            return self._parse_json(path)
        elif ext in [".vcf", ".vcard"]:
            return self._parse_vcard(path)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Supported: CSV, Excel, JSON, vCard.")

    def _parse_csv(self, path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse CSV file with encoding fallbacks."""
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
        for enc in encodings:
            try:
                with open(path, mode="r", encoding=enc, newline="") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []
                    records = list(reader)
                    return records, list(headers)
            except UnicodeDecodeError:
                continue
        raise ValueError("Failed to decode CSV with common encodings.")

    def _parse_excel(self, path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse Excel spreadsheet."""
        df = pd.read_excel(path, dtype=str)
        df = df.fillna("")
        headers = [str(col) for col in df.columns]
        records = df.to_dict(orient="records")
        return records, headers

    def _parse_json(self, path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse JSON array of contacts."""
        with open(path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            
        if isinstance(data, dict):
            # Handle {"contacts": [...]}
            for key in ["contacts", "data", "items"]:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                data = [data]

        if not isinstance(data, list):
            raise ValueError("JSON must contain an array of contact objects.")

        headers = list({k for rec in data if isinstance(rec, dict) for k in rec.keys()})
        return data, headers

    def _parse_vcard(self, path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Parse vCard 2.1 / 3.0 / 4.0 file."""
        records = []
        with open(path, mode="r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        cards = content.split("BEGIN:VCARD")
        for card in cards:
            if "END:VCARD" not in card:
                continue
            rec = {}
            for line in card.splitlines():
                line = line.strip()
                if not line or line.startswith("VERSION") or line.startswith("END:"):
                    continue
                if ":" in line:
                    key_part, val = line.split(":", 1)
                    prop = key_part.split(";")[0].upper()
                    if prop == "FN":
                        rec["display_name"] = val
                    elif prop == "N":
                        parts = val.split(";")
                        if len(parts) > 0:
                            rec["last_name"] = parts[0]
                        if len(parts) > 1:
                            rec["first_name"] = parts[1]
                    elif prop == "TEL":
                        if "phone" not in rec:
                            rec["phone"] = val
                        else:
                            rec["alternate_phone"] = val
                    elif prop == "EMAIL":
                        if "email" not in rec:
                            rec["email"] = val
                        else:
                            rec["alternate_email"] = val
                    elif prop == "ORG":
                        rec["company"] = val.replace(";", " ").strip()
                    elif prop == "TITLE":
                        rec["job_title"] = val
                    elif prop == "NOTE":
                        rec["notes"] = val
            if rec:
                records.append(rec)

        headers = ["first_name", "last_name", "display_name", "phone", "alternate_phone", "email", "alternate_email", "company", "job_title", "notes"]
        return records, headers

    def import_records(
        self,
        records: List[Dict[str, Any]],
        column_mapping: Dict[str, str],
        skip_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Execute batch import applying column mapping, normalization, and validation.
        Returns:
            summary: {
                "total_rows": int,
                "imported_count": int,
                "skipped_duplicate_count": int,
                "invalid_count": int,
                "errors": List[str]
            }
        """
        imported_count = 0
        skipped_dup = 0
        invalid_count = 0
        error_logs: List[str] = []

        for idx, row in enumerate(records, start=1):
            contact_data: Dict[str, Any] = {}
            for file_header, mapped_field in column_mapping.items():
                if mapped_field and file_header in row:
                    val = row[file_header]
                    contact_data[mapped_field] = str(val).strip() if val is not None else ""

            # Handle Name splitting if only full name / display name provided
            if not contact_data.get("first_name") and contact_data.get("display_name"):
                name_parts = contact_data["display_name"].split(maxsplit=1)
                contact_data["first_name"] = name_parts[0]
                if len(name_parts) > 1:
                    contact_data["last_name"] = name_parts[1]

            contact = Contact.from_dict(contact_data)
            contact.normalize()

            # Validation
            is_valid, errs = ValidationService.validate_contact(contact)
            if not is_valid:
                invalid_count += 1
                error_logs.append(f"Row {idx} rejected: {', '.join(errs.values())}")
                continue

            # Duplicate check
            if skip_duplicates:
                existing_email = None
                existing_phone = None
                if contact.email:
                    existing_email, _ = self.repo.search_contacts(contact.email)
                    existing_email = [c for c in existing_email if c.email.lower() == contact.email.lower()]
                if contact.phone:
                    existing_phone, _ = self.repo.search_contacts(contact.phone)
                    clean_p = "".join(ch for ch in contact.phone if ch.isdigit())
                    existing_phone = [c for c in existing_phone if "".join(ch for ch in c.phone if ch.isdigit()) == clean_p]
                
                if (existing_email and len(existing_email) > 0) or (existing_phone and len(existing_phone) > 0):
                    skipped_dup += 1
                    continue

            # Persist
            try:
                self.repo.add_contact(contact)
                imported_count += 1
            except Exception as e:
                invalid_count += 1
                error_logs.append(f"Row {idx} database insert error: {e}")

        summary = {
            "total_rows": len(records),
            "imported_count": imported_count,
            "skipped_duplicate_count": skipped_dup,
            "invalid_count": invalid_count,
            "errors": error_logs
        }
        logger.info(f"Import finished: {summary['imported_count']} imported, {summary['skipped_duplicate_count']} dups skipped, {summary['invalid_count']} invalid.")
        return summary
