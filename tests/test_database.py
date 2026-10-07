"""
Integration tests for Database Repository, SQLite models, and transactions.
"""
import pytest
from database.connection import init_db
from database.repository import ContactRepository
from models.contact import Contact
from models.group import Group
from models.tag import Tag


@pytest.fixture
def repo():
    """In-memory SQLite test fixture with unique isolated database."""
    import uuid
    test_db_url = f"sqlite:///file:mem_{uuid.uuid4().hex}?mode=memory&cache=shared&uri=true"
    init_db(test_db_url)
    return ContactRepository(test_db_url)


def test_add_and_get_contact(repo):
    """Test contact persistence and retrieval."""
    c = Contact(
        first_name="Sundar",
        last_name="Pichai",
        phone="+91 9876543210",
        email="sundar@google.com",
        company="Google",
        city="Mountain View",
        groups=["Work", "Important"],
        tags=["VIP", "Executive"]
    )
    saved = repo.add_contact(c)
    assert saved.id is not None
    assert saved.first_name == "Sundar"
    assert "Work" in saved.groups
    assert "VIP" in saved.tags

    fetched = repo.get_contact_by_id(saved.id)
    assert fetched is not None
    assert fetched.email == "sundar@google.com"


def test_update_contact(repo):
    """Test modifying contact fields."""
    c = Contact(first_name="Arun", last_name="Kumar", company="Microsoft")
    saved = repo.add_contact(c)

    saved.company = "Microsoft Corporation"
    saved.city = "Hyderabad"
    updated = repo.update_contact(saved)

    assert updated.company == "Microsoft Corporation"
    assert updated.city == "Hyderabad"


def test_soft_delete_and_restore(repo):
    """Test soft delete flag and restore logic."""
    c = Contact(first_name="Temp", last_name="User", phone="9876543210")
    saved = repo.add_contact(c)

    # Soft delete
    assert repo.soft_delete_contact(saved.id) is True
    assert repo.get_contact_by_id(saved.id, include_deleted=False) is None
    assert repo.get_contact_by_id(saved.id, include_deleted=True) is not None

    # Restore
    assert repo.restore_contact(saved.id) is True
    restored = repo.get_contact_by_id(saved.id, include_deleted=False)
    assert restored is not None
    assert restored.is_deleted is False


def test_toggle_favorite(repo):
    """Test toggling contact favorite status."""
    c = Contact(first_name="VIP", last_name="Contact", is_favorite=False)
    saved = repo.add_contact(c)
    assert saved.is_favorite is False

    new_state = repo.toggle_favorite(saved.id)
    assert new_state is True

    new_state = repo.toggle_favorite(saved.id)
    assert new_state is False


def test_dashboard_metrics(repo):
    """Test KPI aggregation."""
    repo.add_contact(Contact(first_name="A", phone="123", email="a@test.com", is_favorite=True))
    repo.add_contact(Contact(first_name="B", phone="456", email="", is_favorite=False))

    metrics = repo.get_dashboard_metrics()
    assert metrics["total_active"] == 2
    assert metrics["total_favorites"] == 1
    assert metrics["missing_email"] == 1
