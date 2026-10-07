"""
Group domain model.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Group:
    """Represents a categorized group for contacts (e.g., Work, Family, Friends, Clients)."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    color: str = "#2563eb"
    icon: str = "📁"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Group":
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            color=data.get("color", "#2563eb"),
            icon=data.get("icon", "📁")
        )
