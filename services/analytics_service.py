"""
Analytics and Automated Insight Engine for Contact Manager Pro.
Calculates KPI statistics, groups, location distributions, addition trends,
and generates intelligent natural-language observations.
"""
from typing import Dict, Any, List, Tuple
from collections import Counter
from datetime import datetime, timezone, timedelta
import pandas as pd

from database.repository import ContactRepository
from services.duplicate_service import DuplicateService
from models.contact import Contact
from utils.logger import get_logger

logger = get_logger("AnalyticsService")


class AnalyticsService:
    """Service providing data engineering aggregations and automated business insights."""

    def __init__(self, repo: ContactRepository = None, dup_service: DuplicateService = None):
        self.repo = repo or ContactRepository()
        self.dup_service = dup_service or DuplicateService(self.repo)

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Fetch high-level KPI metrics."""
        metrics = self.repo.get_dashboard_metrics()
        duplicates = self.dup_service.find_all_duplicates()
        metrics["duplicate_alerts"] = len(duplicates)
        return metrics

    def get_contacts_by_group(self) -> List[Tuple[str, int]]:
        """Return contacts count per group sorted by count descending."""
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        group_counts: Counter = Counter()
        for c in contacts:
            for g in c.groups:
                group_counts[g] += 1
                
        # If any contacts have no group, count as "Ungrouped"
        ungrouped = sum(1 for c in contacts if not c.groups)
        if ungrouped > 0:
            group_counts["Ungrouped"] = ungrouped
            
        return group_counts.most_common(10)

    def get_contacts_by_location(self) -> List[Tuple[str, int]]:
        """Return top cities/locations count sorted descending."""
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        cities = [c.city.strip() for c in contacts if c.city and c.city.strip()]
        if not cities:
            return [("Not Specified", len(contacts))]
        return Counter(cities).most_common(8)

    def get_contacts_by_company(self) -> List[Tuple[str, int]]:
        """Return top employers/companies."""
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        companies = [c.company.strip() for c in contacts if c.company and c.company.strip()]
        return Counter(companies).most_common(8)

    def get_monthly_growth_trend(self) -> List[Tuple[str, int]]:
        """Return contact addition count aggregated by month."""
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        if not contacts:
            return []

        # Convert to pandas series
        dates = []
        for c in contacts:
            if c.created_at:
                dates.append(c.created_at.strftime("%b %Y"))
            else:
                dates.append(datetime.now().strftime("%b %Y"))

        counter = Counter(dates)
        # Return chronological or top counts
        return list(counter.items())[-12:]

    def generate_automated_insights(self) -> List[str]:
        """
        Insight Engine: Generates smart, human-readable bullet observations
        characterizing database health, top segments, and anomalies.
        """
        contacts, total = self.repo.get_all_contacts(include_deleted=False)
        if total == 0:
            return ["Your contact database is currently empty. Click '➕ Add Contact' or '📥 Import' to get started."]

        insights: List[str] = []
        
        # 1. Total & Quality Overview
        metrics = self.repo.get_dashboard_metrics()
        quality_score = metrics.get("quality_score", 0)
        insights.append(f"📊 Your database contains {total} active contacts with an overall Data Quality Score of {quality_score}%.")

        # 2. Email & Phone Coverage
        has_email = sum(1 for c in contacts if c.email and c.email.strip())
        email_pct = int((has_email / total) * 100) if total > 0 else 0
        insights.append(f"✉️ {email_pct}% ({has_email}/{total}) of your contacts have a verified email address.")

        missing_phone = metrics.get("missing_phone", 0)
        if missing_phone > 0:
            insights.append(f"⚠️ {missing_phone} contacts are currently missing primary phone numbers.")

        # 3. Top Location
        locs = self.get_contacts_by_location()
        if locs and locs[0][0] != "Not Specified":
            top_city, city_count = locs[0]
            city_pct = int((city_count / total) * 100)
            insights.append(f"🏙️ {top_city} is your top geographic hub with {city_count} contacts ({city_pct}% of total).")

        # 4. Top Employer / Industry
        companies = self.get_contacts_by_company()
        if companies:
            top_company, comp_count = companies[0]
            insights.append(f"💼 {top_company} is the most represented company in your network ({comp_count} contacts).")

        # 5. Favorites
        favs = metrics.get("total_favorites", 0)
        fav_pct = int((favs / total) * 100) if total > 0 else 0
        insights.append(f"⭐ {favs} VIP priority contacts marked as Favorites ({fav_pct}%).")

        # 6. Duplicate Risk Alert
        dups = self.dup_service.find_all_duplicates()
        if dups:
            insights.append(f"🔍 {len(dups)} potential duplicate profile pairs detected. Check the Duplicate Review page to merge them.")
        else:
            insights.append("✅ No duplicate records detected in your database. High integrity maintained!")

        return insights
