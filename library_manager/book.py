# library_manager/book.py
"""
Book class for Library Inventory Manager.

Attributes:
    title (str), author (str), isbn (str), status (str) -> "available" or "issued"
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    status: str = "available"  # "available" or "issued"

    def __post_init__(self):
        # normalize status
        if self.status not in ("available", "issued"):
            self.status = "available"

    def issue(self) -> bool:
        """Mark book as issued. Return True if successful, False if already issued."""
        if self.status == "issued":
            return False
        self.status = "issued"
        return True

    def return_book(self) -> bool:
        """Mark book as available. Return True if successful, False if already available."""
        if self.status == "available":
            return False
        self.status = "available"
        return True

    def is_available(self) -> bool:
        """Return True if the book is available."""
        return self.status == "available"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON persistence."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Book":
        """Create Book from dictionary (as read from JSON)."""
        return cls(
            title=data.get("title", ""),
            author=data.get("author", ""),
            isbn=str(data.get("isbn", "")),
            status=data.get("status", "available"),
        )

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - {self.status}"
