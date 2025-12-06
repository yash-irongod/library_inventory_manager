# library_manager/__init__.py
"""Library Inventory package."""
from .book import Book
from .inventory import LibraryInventory

__all__ = ["Book", "LibraryInventory"]