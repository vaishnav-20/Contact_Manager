"""
Unit tests for SearchService and faceted filtering.
"""
import pytest
from database.connection import init_db
from database.repository import ContactRepository
from services.search_service import SearchService
from models.contact import Contact


@pytest.fixture
def search_env():
    """Setup in-memory DB and search service fixture."""
    import uuid
    test_db_url = f"sqlite:///file:mem_{uuid.uuid4().hex}?mode=memory&cache=shared&uri=true"
    init_db(test_db_url)
    repo = ContactRepository(test_db_url)
    svc = SearchService(repo)

    # Seed diverse sample records
    repo.add_contact(Contact(first_name="Arun", last_name="Kumar", company="Microsoft", city="Chennai", tags=["Python"]))
    repo.add_contact(Contact(first_name="Priya", last_name="Sharma", company="TCS", city="Mumbai", tags=["Management"]))
    repo.add_contact(Contact(first_name="Rahul", last_name="Sundaram", company="Infosys", city="Bangalore", tags=["Python", "Cloud"]))
    repo.add_contact(Contact(first_name="Deepak", last_name="Verma", company="Microsoft", city="Delhi", notes="Azure team"))

    return repo, svc


def test_quick_search_by_name(search_env):
    """Test searching by contact name."""
    _, svc = search_env
    results, total = svc.quick_search("Arun")
    assert total == 1
    assert results[0].first_name == "Arun"


def test_quick_search_by_company(search_env):
    """Test searching by company keyword."""
    _, svc = search_env
    results, total = svc.quick_search("Microsoft")
    assert total == 2


def test_quick_search_by_city(search_env):
    """Test searching by city."""
    _, svc = search_env
    results, total = svc.quick_search("Bangalore")
    assert total == 1
    assert results[0].first_name == "Rahul"


def test_advanced_search(search_env):
    """Test multi-field targeted search."""
    _, svc = search_env
    results, total = svc.advanced_search(company="Microsoft", city="Delhi")
    assert total == 1
    assert results[0].first_name == "Deepak"
