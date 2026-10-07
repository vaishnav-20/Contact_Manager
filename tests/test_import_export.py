"""
Round-trip tests for ImportService and ExportService across CSV, Excel, JSON, and vCard.
"""
import os
import tempfile
from pathlib import Path
import pytest

from database.connection import init_db
from database.repository import ContactRepository
from services.import_service import ImportService
from services.export_service import ExportService
from models.contact import Contact


@pytest.fixture
def test_contacts():
    return [
        Contact(first_name="Arun", last_name="Kumar", phone="+91 9876543210", email="arun@microsoft.com", company="Microsoft", city="Chennai"),
        Contact(first_name="Priya", last_name="Sharma", phone="+91 9876543211", email="priya@tcs.com", company="TCS", city="Mumbai"),
    ]


def test_csv_export_and_import(test_contacts):
    """Test CSV round-trip export and ingestion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_contacts.csv"
        ExportService.export_contacts(test_contacts, csv_path, file_format="csv")
        assert csv_path.exists()

        # Ingest back
        repo = ContactRepository("sqlite:///:memory:")
        init_db("sqlite:///:memory:")
        import_svc = ImportService(repo)

        records, headers = import_svc.parse_file(csv_path)
        assert len(records) == 2
        mappings = import_svc.detect_column_mapping(headers)
        summary = import_svc.import_records(records, mappings, skip_duplicates=False)
        assert summary["imported_count"] == 2


def test_json_export_and_import(test_contacts):
    """Test JSON round-trip export and ingestion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "test_contacts.json"
        ExportService.export_contacts(test_contacts, json_path, file_format="json")
        assert json_path.exists()

        repo = ContactRepository("sqlite:///:memory:")
        init_db("sqlite:///:memory:")
        import_svc = ImportService(repo)

        records, headers = import_svc.parse_file(json_path)
        assert len(records) == 2
        mappings = import_svc.detect_column_mapping(headers)
        summary = import_svc.import_records(records, mappings, skip_duplicates=False)
        assert summary["imported_count"] == 2


def test_vcard_export_and_import(test_contacts):
    """Test vCard round-trip export and parsing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vcf_path = Path(tmpdir) / "test_contacts.vcf"
        ExportService.export_contacts(test_contacts, vcf_path, file_format="vcf")
        assert vcf_path.exists()

        repo = ContactRepository("sqlite:///:memory:")
        init_db("sqlite:///:memory:")
        import_svc = ImportService(repo)

        records, _ = import_svc.parse_file(vcf_path)
        assert len(records) == 2
        assert records[0]["first_name"] == "Arun"
