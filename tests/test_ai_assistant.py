"""
Unit tests for ContactAI Assistant offline NLP engine and intent dispatcher.
"""
import pytest
from database.connection import init_db
from database.repository import ContactRepository
from services.contact_service import ContactService
from services.search_service import SearchService
from services.analytics_service import AnalyticsService
from services.duplicate_service import DuplicateService
from services.ai_assistant_service import AIAssistantService
from models.contact import Contact


@pytest.fixture
def ai_env():
    """Setup test fixture for assistant."""
    import uuid
    test_db_url = f"sqlite:///file:mem_{uuid.uuid4().hex}?mode=memory&cache=shared&uri=true"
    init_db(test_db_url)
    repo = ContactRepository(test_db_url)
    contact_svc = ContactService(repo)
    search_svc = SearchService(repo)
    dup_svc = DuplicateService(repo)
    analytics_svc = AnalyticsService(repo, dup_svc)

    repo.add_contact(Contact(first_name="Arun", last_name="Kumar", phone="+91 9876543210", email="arun@microsoft.com", company="Microsoft", city="Chennai"))
    repo.add_contact(Contact(first_name="Priya", last_name="Sharma", phone="+91 9876543211", email="priya@tcs.com", company="TCS", city="Mumbai"))

    assistant = AIAssistantService(contact_svc, search_svc, analytics_svc, dup_svc)
    return repo, assistant


def test_ai_help_intent(ai_env):
    """Test help and command list query."""
    _, assistant = ai_env
    res = assistant.process_query("What can you do?")
    assert "ContactAI Assistant Capabilities" in res
    assert "Quick Contact Addition" in res


def test_ai_analytics_intent(ai_env):
    """Test natural language analytics request."""
    _, assistant = ai_env
    res = assistant.process_query("Give me an analysis of my database")
    assert "Executive Contact Analytics" in res
    assert "Total Active Contacts:" in res


def test_ai_search_intent(ai_env):
    """Test natural language search."""
    _, assistant = ai_env
    res = assistant.process_query("Search for Microsoft")
    assert "Arun Kumar" in res


def test_ai_add_contact_intent(ai_env):
    """Test natural language contact insertion."""
    repo, assistant = ai_env
    res = assistant.process_query("Add contact Sundar Pichai, 9876543299, sundar@google.com, Google, Mountain View")
    assert "Contact Successfully Added" in res
    assert "Sundar Pichai" in res

    # Verify contact is in DB
    contacts, total = repo.search_contacts("Sundar")
    assert total == 1
    assert contacts[0].company == "Google"


def test_ai_duplicates_intent(ai_env):
    """Test duplicate check trigger."""
    _, assistant = ai_env
    res = assistant.process_query("Check for duplicates")
    assert "No duplicate records detected" in res or "Identified" in res
