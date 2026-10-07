"""
Duplicate Detection and Intelligent Contact Merge Engine.
Combines deterministic rule matching with fuzzy string similarity scoring and automated reconciliation.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from database.repository import ContactRepository
from models.contact import Contact
from utils.logger import get_logger

logger = get_logger("DuplicateService")


@dataclass
class DuplicateMatch:
    """Represents a flagged duplicate pair."""
    primary: Contact
    secondary: Contact
    similarity_score: float          # 0.0 to 1.0
    similarity_percentage: int       # 0 to 100
    reasons: List[str]               # Specific factors triggering match


class DuplicateService:
    """Service detecting duplicates and executing intelligent contact merges."""

    def __init__(self, repo: ContactRepository = None):
        self.repo = repo or ContactRepository()

    @staticmethod
    def calculate_name_similarity(name1: str, name2: str) -> float:
        """Compute fuzzy similarity ratio between two contact names."""
        n1 = name1.strip().lower()
        n2 = name2.strip().lower()
        if not n1 or not n2:
            return 0.0
        if n1 == n2:
            return 1.0
            
        # Check initial match e.g. "Arun Kumar" vs "Arun K"
        parts1 = n1.split()
        parts2 = n2.split()
        if parts1 and parts2 and parts1[0] == parts2[0]:
            # Same first name
            if len(parts1) > 1 and len(parts2) > 1:
                last1, last2 = parts1[-1], parts2[-1]
                if last1[0] == last2[0] and (len(last1) == 1 or len(last2) == 1):
                    return 0.90  # High confidence initial match
                    
        return SequenceMatcher(None, n1, n2).ratio()

    def compare_contacts(self, c1: Contact, c2: Contact) -> Tuple[float, List[str]]:
        """
        Compare two contacts and return (similarity_score, list_of_reasons).
        """
        reasons = []
        score = 0.0
        
        # 1. Exact Email Match (High confidence)
        if c1.email and c2.email and c1.email.strip().lower() == c2.email.strip().lower():
            reasons.append("Identical email address")
            score += 0.50

        # 2. Exact Phone Match (High confidence)
        digits1 = "".join(ch for ch in (c1.phone or "") if ch.isdigit())
        digits2 = "".join(ch for ch in (c2.phone or "") if ch.isdigit())
        if digits1 and digits2 and (digits1 == digits2 or digits1.endswith(digits2) or digits2.endswith(digits1)):
            if len(digits1) >= 7 and len(digits2) >= 7:
                reasons.append("Identical normalized phone number")
                score += 0.50

        # 3. Name Similarity
        name_sim = self.calculate_name_similarity(c1.full_name, c2.full_name)
        if name_sim >= 0.85:
            reasons.append(f"High name similarity ({int(name_sim * 100)}%)")
            score += name_sim * 0.40
        elif name_sim >= 0.70:
            reasons.append(f"Moderate name similarity ({int(name_sim * 100)}%)")
            score += name_sim * 0.25

        # 4. Company Match
        if c1.company and c2.company and c1.company.strip().lower() == c2.company.strip().lower():
            reasons.append(f"Same company ({c1.company})")
            score += 0.15

        # Cap score at 1.0
        final_score = min(1.0, score)
        return final_score, reasons

    def find_all_duplicates(self, threshold: float = 0.75) -> List[DuplicateMatch]:
        """
        Scan all active contacts in the database for potential duplicates above threshold.
        """
        contacts, _ = self.repo.get_all_contacts(include_deleted=False)
        duplicates: List[DuplicateMatch] = []
        visited_pairs = set()

        for i in range(len(contacts)):
            for j in range(i + 1, len(contacts)):
                c1 = contacts[i]
                c2 = contacts[j]
                pair_key = (min(c1.id, c2.id), max(c1.id, c2.id))
                if pair_key in visited_pairs:
                    continue
                visited_pairs.add(pair_key)

                score, reasons = self.compare_contacts(c1, c2)
                if score >= threshold and len(reasons) > 0:
                    duplicates.append(
                        DuplicateMatch(
                            primary=c1,
                            secondary=c2,
                            similarity_score=score,
                            similarity_percentage=int(score * 100),
                            reasons=reasons
                        )
                    )

        # Sort highest similarity first
        duplicates.sort(key=lambda d: d.similarity_score, reverse=True)
        logger.info(f"Duplicate scan identified {len(duplicates)} candidate pairs (threshold={threshold}).")
        return duplicates

    def merge_contacts(
        self,
        survivor_id: int,
        duplicate_id: int,
        field_choices: Optional[Dict[str, Any]] = None
    ) -> Optional[Contact]:
        """
        Intelligently merge duplicate contact into survivor contact.
        - Keeps latest/non-empty values or respects field_choices.
        - Combines unique groups and tags.
        - Concatenates notes if distinct.
        - Soft-deletes the duplicate record.
        """
        survivor = self.repo.get_contact_by_id(survivor_id)
        duplicate = self.repo.get_contact_by_id(duplicate_id)
        
        if not survivor or not duplicate:
            raise ValueError(f"One or both contact IDs ({survivor_id}, {duplicate_id}) do not exist.")

        # Apply field choices or default to filling empty fields from duplicate
        if field_choices:
            for field, val in field_choices.items():
                if hasattr(survivor, field):
                    setattr(survivor, field, val)
        else:
            # Automatic intelligent filling
            auto_fields = [
                "last_name", "phone", "alternate_phone", "email", "alternate_email",
                "website", "company", "job_title", "department", "address_line",
                "city", "state", "country", "postal_code", "date_of_birth", "gender"
            ]
            for f in auto_fields:
                cur_val = getattr(survivor, f)
                dup_val = getattr(duplicate, f)
                if (not cur_val or not str(cur_val).strip()) and dup_val and str(dup_val).strip():
                    setattr(survivor, f, dup_val)

        # Merge groups and tags
        combined_groups = list(dict.fromkeys(survivor.groups + duplicate.groups))
        combined_tags = list(dict.fromkeys(survivor.tags + duplicate.tags))
        survivor.groups = combined_groups
        survivor.tags = combined_tags

        # Combine notes
        if duplicate.notes and duplicate.notes.strip():
            if duplicate.notes not in survivor.notes:
                survivor.notes = f"{survivor.notes}\n[Merged Notes]: {duplicate.notes}".strip()

        # Update survivor
        updated_survivor = self.repo.update_contact(survivor)

        # Soft delete duplicate
        self.repo.soft_delete_contact(duplicate_id)
        
        # Log merge audit
        self.repo.log_audit(
            action="MERGE",
            contact_id=survivor_id,
            details=f"Merged duplicate contact ID {duplicate_id} ('{duplicate.full_name}') into ID {survivor_id} ('{survivor.full_name}')"
        )
        
        logger.info(f"Successfully merged contact {duplicate_id} into {survivor_id}.")
        return updated_survivor
