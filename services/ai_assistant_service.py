"""
ContactAI Assistant Engine.
Hybrid Offline/Online Natural Language Processing (NLP) Assistant capable of executing
CRUD operations, advanced search, data quality analysis, duplicate resolution, and voice transcription.
Operates 100% offline out-of-the-box without external API keys, ensuring seamless post-deployment execution.
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from database.repository import ContactRepository
from services.contact_service import ContactService
from services.search_service import SearchService
from services.analytics_service import AnalyticsService
from services.duplicate_service import DuplicateService
from services.backup_service import BackupService
from models.contact import Contact
from utils.validators import Validator
from utils.logger import get_logger

logger = get_logger("AIAssistant")


class AIAssistantService:
    """Intelligent conversational assistant for Contact Manager Pro."""

    def __init__(
        self,
        contact_service: ContactService = None,
        search_service: SearchService = None,
        analytics_service: AnalyticsService = None,
        duplicate_service: DuplicateService = None,
        backup_service: BackupService = None
    ):
        self.contact_service = contact_service or ContactService(ContactRepository())
        self.repo = self.contact_service.repo
        self.search_service = search_service or SearchService(self.repo)
        self.analytics_service = analytics_service or AnalyticsService(self.repo)
        self.duplicate_service = duplicate_service or DuplicateService(self.repo)
        self.backup_service = backup_service or BackupService()

    def process_query(self, user_text: str) -> str:
        """
        Main query handler. Identifies intent, extracts entities, executes action,
        and returns human-readable formatted text response.
        """
        if not user_text or not user_text.strip():
            return "🤖 Hello! I am your **ContactAI Assistant**. How can I assist you with your contacts today?"

        raw = user_text.strip()
        lower = raw.lower()

        # 1. Greetings & Help
        if any(w in lower for w in ["help", "what can you do", "features", "commands"]):
            return self._handle_help()
        if lower in ["hi", "hello", "hey", "greetings", "good morning", "good evening"]:
            return (
                "👋 **Greetings! I am ContactAI, your offline CRM assistant.**\n\n"
                "Here are a few things I can do for you:\n"
                "• *'Add contact Rajesh Kumar, 9876543299, rajesh@gmail.com, Zoho, Chennai'*\n"
                "• *'Search for Google' or 'Find contacts in Bangalore'*\n"
                "• *'Analyze my contacts'* (executive summary & KPIs)\n"
                "• *'Check for duplicates'*\n"
                "• *'Show my favorite contacts'*\n"
                "• *'Who is missing email or phone?'*\n"
                "• *'Backup database'* or *'Export contacts'*"
            )

        # 2. Add Contact Intent
        if lower.startswith("add ") or lower.startswith("create ") or "add contact" in lower or "new contact" in lower:
            return self._handle_add_contact(raw)

        # 3. Analytics & Summary Intent
        if any(w in lower for w in ["analysis", "analyze", "summary", "stats", "overview", "insights", "metrics", "health"]):
            return self._handle_analytics()

        # 4. Incomplete / Missing Data Query
        if any(w in lower for w in ["missing email", "without email", "no email"]):
            return self._handle_missing_email()
        if any(w in lower for w in ["missing phone", "without phone", "no phone"]):
            return self._handle_missing_phone()
        if any(w in lower for w in ["incomplete", "quality score"]):
            return self._handle_data_quality()

        # 5. Duplicate Detection Query
        if any(w in lower for w in ["duplicate", "duplicates", "repeated"]):
            return self._handle_duplicates()

        # 6. Favorites Query
        if any(w in lower for w in ["favorite", "favorites", "vip", "starred"]):
            return self._handle_favorites()

        # 7. Backup Intent
        if any(w in lower for w in ["backup", "snapshot"]):
            return self._handle_backup()

        # 8. Search Intent
        if lower.startswith("search ") or lower.startswith("find ") or "look for" in lower or "who works at" in lower:
            return self._handle_search(raw)

        # 9. Fallback Search / Match
        # If user typed a company name or person's name directly, search for it
        return self._handle_fallback_search(raw)

    def _handle_help(self) -> str:
        """Return assistant capabilities."""
        return (
            "🤖 **ContactAI Assistant Capabilities:**\n\n"
            "**1. Quick Contact Addition**\n"
            "   `Add contact [Name], [Phone], [Email], [Company], [City]`\n"
            "   *Example:* `Add Ankit Sharma, 9876543200, ankit@tech.com, Amazon, Hyderabad`\n\n"
            "**2. Smart Search & Retrieval**\n"
            "   `Find contacts in Chennai` | `Search for Microsoft` | `Who works at TCS?`\n\n"
            "**3. Data Analytics & Insights**\n"
            "   `Analyze my database` | `Show top companies` | `Show top locations`\n\n"
            "**4. Data Quality & Cleaning**\n"
            "   `Who is missing an email?` | `Check for duplicate contacts`\n\n"
            "**5. Database Utilities**\n"
            "   `Show favorites` | `Backup database`"
        )

    def _handle_add_contact(self, query: str) -> str:
        """Parse natural language command and insert contact."""
        # Strip command prefix
        clean = re.sub(r"^(add|create)\s+(new\s+)?(contact\s+)?", "", query, flags=re.IGNORECASE).strip()
        
        # Split by comma or semicolon
        tokens = [t.strip() for t in re.split(r"[,;]", clean) if t.strip()]
        
        name = ""
        phone = ""
        email = ""
        company = ""
        city = ""

        # Pattern-based entity extraction
        remaining_tokens = []
        for token in tokens:
            # Check if token is email
            if "@" in token and "." in token:
                email = token
            # Check if token is phone number (7-15 digits with optional +)
            elif re.search(r"^\+?[0-9\s\-]{7,15}$", token):
                phone = token
            else:
                remaining_tokens.append(token)

        # Assign remaining tokens in order: [Name, Company, City]
        if remaining_tokens:
            name = remaining_tokens[0]
        if len(remaining_tokens) > 1:
            company = remaining_tokens[1]
        if len(remaining_tokens) > 2:
            city = remaining_tokens[2]

        if not name:
            return (
                "⚠️ **Could not identify the contact name.**\n\n"
                "Please format as: `Add contact [Name], [Phone], [Email], [Company]`\n"
                "Example: `Add contact Sundar Pichai, 9876543210, sundar@google.com, Google`"
            )

        # Split Name into first and last
        parts = name.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        new_contact = Contact(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            company=company,
            city=city,
            notes="Added via ContactAI Assistant"
        )

        saved, errors = self.contact_service.create_contact(new_contact)
        if errors:
            return f"❌ **Validation Failed:**\n" + "\n".join(f"• {k}: {v}" for k, v in errors.items())

        return (
            f"✅ **Contact Successfully Added!**\n\n"
            f"• **ID:** `{saved.id}`\n"
            f"• **Name:** {saved.full_name}\n"
            f"• **Phone:** {saved.formatted_phone or '—'}\n"
            f"• **Email:** {saved.email or '—'}\n"
            f"• **Company:** {saved.company or '—'}\n"
            f"• **Location:** {saved.city or '—'}"
        )

    def _handle_analytics(self) -> str:
        """Generate comprehensive analytics report."""
        kpis = self.analytics_service.get_summary_kpis()
        insights = self.analytics_service.generate_automated_insights()
        groups = self.analytics_service.get_contacts_by_group()
        locations = self.analytics_service.get_contacts_by_location()

        resp = [
            "📊 **Executive Contact Analytics & Health Report**\n",
            f"• **Total Active Contacts:** `{kpis['total_active']}`",
            f"• **Favorites (VIP):** `{kpis['total_favorites']}`",
            f"• **Active Groups:** `{kpis['total_groups']}`",
            f"• **Data Completeness Score:** `{kpis['quality_score']}%`",
            f"• **Duplicate Risk Alerts:** `{kpis['duplicate_alerts']}`",
            "\n💡 **Automated Business Insights:**"
        ]
        for ins in insights:
            resp.append(f"• {ins}")

        if locations:
            top_locs = ", ".join(f"{loc} ({cnt})" for loc, cnt in locations[:3])
            resp.append(f"\n📍 **Top Hubs:** {top_locs}")

        if groups:
            top_groups = ", ".join(f"{grp} ({cnt})" for grp, cnt in groups[:3])
            resp.append(f"📁 **Top Groups:** {top_groups}")

        return "\n".join(resp)

    def _handle_missing_email(self) -> str:
        """Query contacts with missing email."""
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        missing = [c for c in contacts if not c.email or not c.email.strip()]
        if not missing:
            return "🎉 **All contacts have email addresses registered!**"

        lines = [f"⚠️ **Found {len(missing)} contact(s) missing email addresses:**\n"]
        for c in missing[:10]:
            lines.append(f"• **ID {c.id}:** {c.full_name} | Phone: {c.phone or 'None'} | {c.company or 'No Company'}")
        if len(missing) > 10:
            lines.append(f"*... and {len(missing) - 10} more.*")
        return "\n".join(lines)

    def _handle_missing_phone(self) -> str:
        """Query contacts with missing phone."""
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        missing = [c for c in contacts if not c.phone or not c.phone.strip()]
        if not missing:
            return "🎉 **All contacts have phone numbers registered!**"

        lines = [f"⚠️ **Found {len(missing)} contact(s) missing phone numbers:**\n"]
        for c in missing[:10]:
            lines.append(f"• **ID {c.id}:** {c.full_name} | Email: {c.email or 'None'} | {c.company or 'No Company'}")
        if len(missing) > 10:
            lines.append(f"*... and {len(missing) - 10} more.*")
        return "\n".join(lines)

    def _handle_data_quality(self) -> str:
        """Report on data completeness score."""
        metrics = self.repo.get_dashboard_metrics()
        score = metrics.get("quality_score", 0)
        return (
            f"🛡️ **Contact Data Quality Assessment**\n\n"
            f"• **Overall Score:** `{score}%`\n"
            f"• **Complete Profiles:** {metrics['complete_profiles']} / {metrics['total_active']}\n"
            f"• **Missing Phone:** {metrics['missing_phone']}\n"
            f"• **Missing Email:** {metrics['missing_email']}\n\n"
            f"💡 *Recommendation:* Fill in missing contact info to raise your quality score above 90%."
        )

    def _handle_duplicates(self) -> str:
        """Detect and list duplicate contact pairs."""
        dups = self.duplicate_service.find_all_duplicates()
        if not dups:
            return "✅ **No duplicate records detected.** Your database integrity is 100% clean!"

        lines = [f"🔍 **Identified {len(dups)} Potential Duplicate Pair(s):**\n"]
        for d in dups[:5]:
            lines.append(
                f"• **{d.similarity_percentage}% Match**: `{d.primary.full_name}` (ID {d.primary.id}) & "
                f"`{d.secondary.full_name}` (ID {d.secondary.id})\n"
                f"  *Reason:* {', '.join(d.reasons)}"
            )
        lines.append("\n👉 *Tip: Open the '🔀 Duplicates' tab in the navigation to review and merge them.*")
        return "\n".join(lines)

    def _handle_favorites(self) -> str:
        """List favorite VIP contacts."""
        favs, count = self.repo.get_all_contacts(favorites_only=True)
        if count == 0:
            return "⭐ **You currently have no contacts marked as Favorites.** Click the star icon on any contact to favorite them."

        lines = [f"⭐ **You have {count} Favorite Contact(s):**\n"]
        for c in favs[:10]:
            lines.append(f"• **{c.full_name}** | {c.company or 'No Company'} | 📞 {c.formatted_phone or '—'}")
        return "\n".join(lines)

    def _handle_backup(self) -> str:
        """Trigger database backup."""
        try:
            path = self.backup_service.create_backup("assistant")
            return f"💾 **Backup Created Successfully!**\n\n• **File:** `{path.name}`\n• **Location:** `{path}`"
        except Exception as e:
            return f"❌ **Backup Error:** {e}"

    def _handle_search(self, query: str) -> str:
        """Extract search query and return results."""
        # Strip prefixes like "find contacts in", "search for", etc.
        term = re.sub(r"^(search(\s+for)?|find(\s+contacts(\s+in)?)?|who works at)\s+", "", query, flags=re.IGNORECASE).strip()
        return self._execute_search_term(term)

    def _handle_fallback_search(self, term: str) -> str:
        """Fallback search across database."""
        results, count = self.search_service.quick_search(term, limit=5)
        if count > 0:
            lines = [f"🔍 **Found {count} contact(s) matching '{term}':**\n"]
            for c in results:
                lines.append(f"• **{c.full_name}** (ID {c.id}) | {c.company or 'No Company'} | 📞 {c.formatted_phone or '—'} | ✉️ {c.email or '—'}")
            return "\n".join(lines)
        
        return (
            f"🤔 I could not find any contacts matching **'{term}'**, nor recognize this as a known command.\n\n"
            "Try asking: *'Analyze my contacts'*, *'Check for duplicates'*, or *'Add contact [Name], [Phone]'*."
        )

    def _execute_search_term(self, term: str) -> str:
        """Execute search on a specific term."""
        results, count = self.search_service.quick_search(term, limit=6)
        if count == 0:
            return f"🔍 No contacts found matching **'{term}'**."

        lines = [f"🔍 **Found {count} contact(s) matching '{term}':**\n"]
        for c in results:
            lines.append(f"• **{c.full_name}** (ID {c.id}) | {c.company or 'No Company'} | 📞 {c.formatted_phone or '—'} | ✉️ {c.email or '—'}")
        return "\n".join(lines)

    def transcribe_voice(self) -> Tuple[bool, str]:
        """
        Transcribe voice input from microphone.
        Supports SpeechRecognition library if installed, or gracefully informs user.
        """
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio)
                return True, text
        except ImportError:
            return False, "Speech recognition library not installed. You can type your request directly in the chat box."
        except Exception as e:
            return False, f"Could not capture voice: {e}"
