"""
Unit tests for DuplicateService and Intelligent Merge Engine.
"""
import pytest
from database.connection import init_db
from database.repository import ContactRepository
from services.duplicate_service import DuplicateService
from models.contact import Contact


@pytest.fixture
def dup_env():
    """Setup in-memory DB and duplicate service fixture."""
    import uuid
    test_db_url = f"sqlite:///file:mem_{uuid.uuid4().hex}?mode=memory&cache=shared&uri=true"
    init_db(test_db_url)
    repo = ContactRepository(test_db_url)
    svc = DuplicateService(repo)
    return repo, svc


def test_name_similarity():
    """Test SequenceMatcher and prefix name matching."""
    sim1 = DuplicateService.calculate_name_similarity("Arun Kumar", "Arun Kumar")
    assert sim1 == 1.0

    # "Arun Kumar" vs "Arun K"
    sim2 = DuplicateService.calculate_name_similarity("Arun Kumar", "Arun K")
    assert sim2 >= 0.85


def test_duplicate_detection(dup_env):
    """Test flagging duplicate pairs."""
    repo, svc = dup_env
    # Add two near-identical records
    c1 = repo.add_contact(Contact(
        first_name="Arun",
        last_name="Kumar",
        phone="+91 9876543210",
        email="arun@microsoft.com",
        company="Microsoft"
    ))
    c2 = repo.add_contact(Contact(
        first_name="Arun",
        last_name="K",
        phone="+91 9876543210",
        email="arun@microsoft.com",
        company="Microsoft India"
    ))

    dups = svc.find_all_duplicates(threshold=0.75)
    assert len(dups) >= 1
    assert dups[0].similarity_percentage >= 85
    assert any("phone" in r.lower() or "email" in r.lower() for r in dups[0].reasons)


def test_merge_contacts(dup_env):
    """Test smart contact merging and reconciliation."""
    repo, svc = dup_env
    c1 = repo.add_contact(Contact(
        first_name="Arun",
        last_name="Kumar",
        phone="+91 9876543210",
        email="",  # Missing in survivor
        company="Microsoft",
        groups=["Work"]
    ))
    c2 = repo.add_contact(Contact(
        first_name="Arun",
        last_name="K",
        phone="+91 9876543210",
        email="arun.k@microsoft.com",  # Present in duplicate
        city="Chennai",                # Present in duplicate
        groups=["Developers"],
        notes="Secondary notes"
    ))

    merged = svc.merge_contacts(survivor_id=c1.id, duplicate_id=c2.id)
    assert merged.email == "arun.k@microsoft.com"
    assert merged.city == "Chennai"
    assert "Work" in merged.groups
    assert "Developers" in merged.groups
    assert "Secondary notes" in merged.notes

    # Duplicate should now be soft-deleted
    assert repo.get_contact_by_id(c2.id, include_deleted=False) is None
    assert repo.get_contact_by_id(c2.id, include_deleted=True).is_deleted is True
