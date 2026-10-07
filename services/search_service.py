"""
Search Service for Contact Manager Pro.
Implements instant full-text search, multi-field faceted filtering, and search highlighting.
"""
from typing import List, Tuple, Dict, Any, Optional
from database.repository import ContactRepository
from models.contact import Contact
from utils.logger import get_logger

logger = get_logger("SearchService")


class SearchService:
    """Service dedicated to search queries and faceted filters."""

    def __init__(self, repo: ContactRepository = None):
        self.repo = repo or ContactRepository()

    def quick_search(
        self,
        query: str,
        include_deleted: bool = False,
        favorites_only: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Tuple[List[Contact], int]:
        """Perform unified instant search across all textual contact fields."""
        logger.info(f"Executing quick search query: '{query}'")
        return self.repo.search_contacts(
            search_query=query,
            include_deleted=include_deleted,
            favorites_only=favorites_only,
            limit=limit,
            offset=offset
        )

    def advanced_search(
        self,
        name: Optional[str] = None,
        company: Optional[str] = None,
        city: Optional[str] = None,
        group_name: Optional[str] = None,
        tag_name: Optional[str] = None,
        favorites_only: bool = False,
        include_deleted: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Tuple[List[Contact], int]:
        """Perform targeted multi-criteria filtering."""
        logger.info(f"Executing advanced search: name={name}, company={company}, city={city}, group={group_name}")
        return self.repo.advanced_search(
            name=name,
            company=company,
            city=city,
            group_name=group_name,
            tag_name=tag_name,
            favorites_only=favorites_only,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )
