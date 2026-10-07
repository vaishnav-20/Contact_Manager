"""
Database migrations and seed data generator.
Creates initial tables and seeds realistic contact entries, groups, tags, and deliberate duplicates.
"""
from datetime import datetime, timezone, timedelta
from database.connection import init_db
from database.repository import ContactRepository
from models.contact import Contact
from models.group import Group
from models.tag import Tag
from utils.logger import get_logger

logger = get_logger("Migrations")

DEFAULT_GROUPS = [
    ("Work", "Professional colleagues and teammates", "#2563eb", "💼"),
    ("Friends", "Close personal friends", "#10b981", "🧑‍🤝‍🧑"),
    ("Family", "Immediate and extended family members", "#ec4899", "👨‍👩‍👧‍👦"),
    ("Clients", "Key enterprise customers and accounts", "#f59e0b", "🤝"),
    ("Developers", "Tech community and engineering peers", "#8b5cf6", "💻"),
    ("College", "Alumni and university classmates", "#06b6d4", "🎓"),
    ("Important", "VIP priority contacts", "#d4af37", "⭐"),
]

DEFAULT_TAGS = [
    ("Python", "#3b82f6"),
    ("Developer", "#10b981"),
    ("Manager", "#f59e0b"),
    ("VIP", "#d4af37"),
    ("AI / ML", "#8b5cf6"),
    ("Cloud", "#06b6d4"),
    ("Design", "#ec4899"),
]

SAMPLE_CONTACTS = [
    {
        "first_name": "Arun",
        "last_name": "Kumar",
        "phone": "+91 9876543210",
        "email": "arun.kumar@microsoft.com",
        "company": "Microsoft",
        "job_title": "Principal Architect",
        "city": "Chennai",
        "country": "India",
        "groups": ["Work", "Developers", "Important"],
        "tags": ["Python", "Cloud", "VIP"],
        "is_favorite": True,
        "notes": "Lead for Azure cloud migration project.",
    },
    {
        "first_name": "Priya",
        "last_name": "Sharma",
        "phone": "+91 9876543211",
        "email": "priya.sharma@tcs.com",
        "company": "TCS",
        "job_title": "Senior Project Manager",
        "city": "Mumbai",
        "country": "India",
        "groups": ["Clients", "Work"],
        "tags": ["Manager", "VIP"],
        "is_favorite": False,
        "notes": "Met at APAC Banking Tech Conference.",
    },
    {
        "first_name": "Rahul",
        "last_name": "Sundaram",
        "phone": "+91 9876543212",
        "email": "rahul.s@infosys.com",
        "company": "Infosys",
        "job_title": "Lead Fullstack Engineer",
        "city": "Bangalore",
        "country": "India",
        "groups": ["Work", "Developers"],
        "tags": ["Python", "Developer"],
        "is_favorite": True,
        "notes": "Key contributor to open source tools.",
    },
    {
        "first_name": "Ananya",
        "last_name": "Iyer",
        "phone": "+91 9876543213",
        "email": "ananya.iyer@google.com",
        "company": "Google",
        "job_title": "AI Research Scientist",
        "city": "Bangalore",
        "country": "India",
        "groups": ["Work", "Important"],
        "tags": ["AI / ML", "Python", "VIP"],
        "is_favorite": True,
        "notes": "LLM optimization and autonomous agents speaker.",
    },
    {
        "first_name": "Karthik",
        "last_name": "Rajan",
        "phone": "+91 9876543214",
        "email": "karthik.rajan@zoho.com",
        "company": "Zoho",
        "job_title": "Product Designer",
        "city": "Chennai",
        "country": "India",
        "groups": ["Friends", "Developers"],
        "tags": ["Design"],
        "is_favorite": False,
        "notes": "Collaborating on UI design systems.",
    },
    {
        "first_name": "Sneha",
        "last_name": "Patel",
        "phone": "+91 9876543215",
        "email": "sneha.patel@amazon.com",
        "company": "Amazon",
        "job_title": "Solutions Architect",
        "city": "Hyderabad",
        "country": "India",
        "groups": ["Work", "College"],
        "tags": ["Cloud", "Developer"],
        "is_favorite": False,
        "notes": "Engineering batchmate from college.",
    },
    {
        "first_name": "Deepak",
        "last_name": "Verma",
        "phone": "+91 9876543216",
        "email": "deepak.verma@accenture.com",
        "company": "Accenture",
        "job_title": "Consulting Director",
        "city": "Delhi",
        "country": "India",
        "groups": ["Clients", "Important"],
        "tags": ["Manager", "VIP"],
        "is_favorite": True,
        "notes": "Enterprise digital transformation advisor.",
    },
    {
        "first_name": "Meera",
        "last_name": "Nair",
        "phone": "+91 9876543217",
        "email": "meera.nair@wipro.com",
        "company": "Wipro",
        "job_title": "DevOps Engineer",
        "city": "Kochi",
        "country": "India",
        "groups": ["Work", "Developers"],
        "tags": ["Cloud", "Python"],
        "is_favorite": False,
        "notes": "Kubernetes & CI/CD pipeline expert.",
    },
    # Deliberate near-duplicate for testing Deduplication Engine:
    {
        "first_name": "Arun",
        "last_name": "K",
        "phone": "+91 9876543210",
        "email": "arun.kumar@microsoft.com",
        "company": "Microsoft India",
        "job_title": "Architect",
        "city": "Chennai",
        "country": "India",
        "groups": ["Work"],
        "tags": ["Cloud"],
        "is_favorite": False,
        "notes": "Possible duplicate record of Arun Kumar.",
    },
    {
        "first_name": "Vikram",
        "last_name": "Reddy",
        "phone": "+91 9876543218",
        "email": "vikram.reddy@startup.io",
        "company": "NexGen Innovations",
        "job_title": "Co-founder & CTO",
        "city": "Hyderabad",
        "country": "India",
        "groups": ["Friends", "Developers", "Important"],
        "tags": ["VIP", "AI / ML"],
        "is_favorite": True,
        "notes": "Seed stage investor and tech co-founder.",
    },
    {
        "first_name": "Suresh",
        "last_name": "Menon",
        "phone": "",  # Deliberate missing phone to test Data Quality Score
        "email": "suresh.menon@freelance.org",
        "company": "Independent",
        "job_title": "Technical Writer",
        "city": "Chennai",
        "country": "India",
        "groups": ["Friends"],
        "tags": ["Python"],
        "is_favorite": False,
        "notes": "API docs reviewer.",
    },
    {
        "first_name": "Rohan",
        "last_name": "Gupta",
        "phone": "+91 9876543219",
        "email": "",  # Deliberate missing email to test Data Quality Score
        "company": "Fintech Global",
        "job_title": "Risk Analyst",
        "city": "Mumbai",
        "country": "India",
        "groups": ["Clients"],
        "tags": ["Finance"],
        "is_favorite": False,
        "notes": "Payment gateway integrations.",
    }
]


def seed_database(repo: ContactRepository = None) -> None:
    """Seed groups, tags, and realistic contacts into database."""
    if repo is None:
        repo = ContactRepository()
        
    init_db(repo.db_url)
    
    # Check if contacts already exist
    _, total = repo.get_all_contacts(include_deleted=True, limit=1)
    if total > 0:
        logger.info("Database already contains data; skipping seed.")
        return

    logger.info("Seeding database with default groups, tags, and contacts...")
    
    # 1. Create Groups
    for name, desc, color, icon in DEFAULT_GROUPS:
        repo.create_group(Group(name=name, description=desc, color=color, icon=icon))
        
    # 2. Create Tags
    for name, color in DEFAULT_TAGS:
        repo.create_tag(Tag(name=name, color=color))
        
    # 3. Create Contacts with staggered creation timestamps for analytics trend
    now = datetime.now(timezone.utc)
    for i, c_data in enumerate(SAMPLE_CONTACTS):
        staggered_time = now - timedelta(days=(len(SAMPLE_CONTACTS) - i) * 7)
        c = Contact.from_dict(c_data)
        c.normalize()
        c.created_at = staggered_time
        c.updated_at = staggered_time
        repo.add_contact(c)
        
    logger.info(f"Database successfully seeded with {len(SAMPLE_CONTACTS)} contacts.")
