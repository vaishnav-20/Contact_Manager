"""
Tag domain model.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Tag:
    """Represents a flexible keyword tag (e.g., Python, Developer, VIP, Lead)."""
    id: Optional[int] = None
    name: str = ""
    color: str = "#d4af37"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            color=data.get("color", "#d4af37")
        )
