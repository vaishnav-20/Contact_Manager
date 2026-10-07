"""
Contact Manager Pro — Application Entry Point.

Flow:
  1. Show LoginView (multi-user auth gate)
  2. On successful login/signup → build ContactManagerApp with user-scoped database
  3. On logout → return to LoginView
  4. --cli flag skips GUI and runs the interactive console CLI
"""
import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import AppConfig
from database.connection import init_db
from database.migrations import seed_database
from database.repository import ContactRepository
from services.contact_service import ContactService
from services.search_service import SearchService
from services.analytics_service import AnalyticsService
from services.ai_assistant_service import AIAssistantService
from utils.logger import setup_logger, get_logger

logger = setup_logger()


def run_cli_mode():
    """Interactive Console CLI Mode (uses legacy shared contacts.db)."""
    repo = ContactRepository()
    contact_service = ContactService(repo)
    search_service = SearchService(repo)
    ai_service = AIAssistantService(contact_service, search_service)

    print("=" * 60)
    print(f"        {AppConfig.APP_NAME} v{AppConfig.APP_VERSION} (CLI Mode)")
    print("=" * 60)

    while True:
        print("\n1. View All Contacts")
        print("2. Search Contacts")
        print("3. Add New Contact")
        print("4. Toggle Favorite")
        print("5. Delete Contact")
        print("6. Executive Analytics Summary")
        print("7. Ask ContactAI Assistant")
        print("8. Exit")

        choice = input("\nEnter choice [1-8]: ").strip()

        if choice == "1":
            contacts, total = contact_service.list_contacts()
            print(f"\n--- Total Contacts: {total} ---")
            for c in contacts:
                fav = "★ " if c.is_favorite else "  "
                print(f"{fav}ID {c.id:2d} | {c.full_name:20s} | {c.company:16s} | {c.formatted_phone:16s} | {c.email}")

        elif choice == "2":
            q = input("Enter search keyword (name/company/phone/city): ").strip()
            results, total = search_service.quick_search(q)
            print(f"\nFound {total} match(es):")
            for c in results:
                print(f"• ID {c.id}: {c.full_name} ({c.company}) - Phone: {c.phone} | Email: {c.email}")

        elif choice == "3":
            from models.contact import Contact
            fname = input("First Name: ").strip()
            lname = input("Last Name: ").strip()
            phone = input("Phone: ").strip()
            email = input("Email: ").strip()
            company = input("Company: ").strip()
            c = Contact(first_name=fname, last_name=lname, phone=phone, email=email, company=company)
            saved, errs = contact_service.create_contact(c)
            if errs:
                print(f"Validation Error: {errs}")
            else:
                print(f"Contact created with ID {saved.id}!")

        elif choice == "4":
            cid = input("Enter Contact ID to toggle favorite: ").strip()
            if cid.isdigit():
                state = contact_service.toggle_favorite(int(cid))
                print(f"Favorite status is now: {state}")

        elif choice == "5":
            cid = input("Enter Contact ID to delete: ").strip()
            if cid.isdigit():
                contact_service.delete_contact(int(cid))
                print("Contact deleted successfully.")

        elif choice == "6":
            kpis = repo.get_dashboard_metrics()
            print(f"\n--- Executive KPIs ---")
            print(f"Total Contacts: {kpis['total_active']}")
            print(f"Favorites:      {kpis['total_favorites']}")
            print(f"Quality Score:  {kpis['quality_score']}%")
            print(f"Missing Email:  {kpis['missing_email']}")

        elif choice == "7":
            prompt = input("Ask ContactAI (e.g. 'Analyze my contacts' or 'Find Microsoft'): ").strip()
            ans = ai_service.process_query(prompt)
            print(f"\nContactAI Response:\n{ans}")

        elif choice == "8":
            print("Goodbye!")
            break


def launch_gui():
    """
    Launch the full GUI application with multi-user authentication.
    Shows LoginView first; on success builds ContactManagerApp with the
    authenticated user's private contact database.
    """
    from gui.auth.login_view import LoginView
    from gui.app import ContactManagerApp

    def start_app(user):
        """Called after successful login/registration."""
        # Initialise and seed this user's private contact database (first login)
        init_db(user.db_url)
        user_repo = ContactRepository(db_url=user.db_url)
        _, total = user_repo.get_all_contacts(include_deleted=True, limit=1)
        if total == 0:
            seed_database(user_repo)
            logger.info(f"Seeded new contact database for user: {user.username}")

        # Build main app; on logout → restart login screen
        app = ContactManagerApp(user=user, on_logout=launch_gui)
        app.run()

    login = LoginView(on_success=start_app)
    login.run()


def main():
    parser = argparse.ArgumentParser(description="Contact Manager Pro")
    parser.add_argument("--cli", action="store_true", help="Launch in command-line interface mode")
    parser.add_argument("--seed", action="store_true", help="Seed the legacy CLI database with sample contacts")
    args = parser.parse_args()

    # Ensure all required directories exist
    AppConfig.ensure_directories()

    if args.cli:
        # CLI mode uses the shared contacts.db (legacy)
        init_db()
        repo = ContactRepository()
        _, total = repo.get_all_contacts(include_deleted=True, limit=1)
        if total == 0 or args.seed:
            seed_database(repo)
        run_cli_mode()
    else:
        launch_gui()


if __name__ == "__main__":
    main()
