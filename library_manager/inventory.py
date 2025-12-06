# library_manager/inventory.py
"""
LibraryInventory: manages a collection of Book objects with JSON persistence.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import List, Optional
from json import JSONDecodeError

from .book import Book

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LibraryInventory:
    def __init__(self, storage_path: Path | str = "catalog.json"):
        self.storage_path = Path(storage_path)
        self.books: List[Book] = []
        # ensure directory exists for storage
        try:
            if self.storage_path.parent and not self.storage_path.parent.exists():
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error("Could not create storage directory: %s", e)
        # load existing catalog if present
        self.load()

    # -------------------------
    # CRUD + search operations
    # -------------------------
    def add_book(self, book: Book) -> None:
        """Add a Book object if ISBN doesn't exist already."""
        if self.find_by_isbn(book.isbn):
            logger.info("Book with ISBN %s already exists. Skipping add.", book.isbn)
            return
        self.books.append(book)
        logger.info("Added book: %s", book)

    def find_by_isbn(self, isbn: str) -> Optional[Book]:
        """Return Book matching ISBN or None."""
        isbn = str(isbn).strip()
        for b in self.books:
            if b.isbn == isbn:
                return b
        return None

    def search_by_title(self, query: str) -> List[Book]:
        """Return list of books that contain query in title (case-insensitive)."""
        q = query.lower().strip()
        return [b for b in self.books if q in b.title.lower()]

    def search_by_author(self, query: str) -> List[Book]:
        """Return list of books that contain query in author (case-insensitive)."""
        q = query.lower().strip()
        return [b for b in self.books if q in b.author.lower()]

    def display_all(self) -> List[str]:
        """Return list of string representations for display."""
        return [str(b) for b in self.books]

    # -------------------------
    # Issue / return operations
    # -------------------------
    def issue_book_by_isbn(self, isbn: str) -> bool:
        """Attempt to issue a book by ISBN. Returns True if successful."""
        book = self.find_by_isbn(isbn)
        if not book:
            logger.error("Issue failed: ISBN %s not found", isbn)
            return False
        if not book.issue():
            logger.info("Issue failed: Book %s already issued", isbn)
            return False
        logger.info("Book issued: %s", isbn)
        self.save()
        return True

    def return_book_by_isbn(self, isbn: str) -> bool:
        """Attempt to return a book by ISBN. Returns True if successful."""
        book = self.find_by_isbn(isbn)
        if not book:
            logger.error("Return failed: ISBN %s not found", isbn)
            return False
        if not book.return_book():
            logger.info("Return failed: Book %s already available", isbn)
            return False
        logger.info("Book returned: %s", isbn)
        self.save()
        return True

    # -------------------------
    # Persistence
    # -------------------------
    def save(self) -> None:
        """Save current catalog to JSON. Uses try/except for robustness."""
        try:
            data = [b.to_dict() for b in self.books]
            with self.storage_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Catalog saved to %s", self.storage_path)
        except Exception as e:
            logger.exception("Failed to save catalog: %s", e)

    def load(self) -> None:
        """Load catalog from JSON file. Handles missing/corrupted files gracefully."""
        if not self.storage_path.exists():
            logger.info("Catalog file %s not found. Starting with empty catalog.", self.storage_path)
            self.books = []
            return
        try:
            with self.storage_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, list):
                logger.error("Catalog JSON is malformed (expected list). Starting empty.")
                self.books = []
                return
            self.books = [Book.from_dict(item) for item in raw]
            logger.info("Loaded %d books from %s", len(self.books), self.storage_path)
        except JSONDecodeError:
            logger.error("Catalog file %s is corrupted or not valid JSON. Backing up and starting fresh.", self.storage_path)
            # move corrupted file aside
            try:
                backup = self.storage_path.with_suffix(".corrupt.json")
                self.storage_path.rename(backup)
                logger.info("Corrupted catalog moved to %s", backup)
            except Exception as e:
                logger.exception("Failed to backup corrupted file: %s", e)
            self.books = []
        except Exception as e:
            logger.exception("Unexpected error loading catalog: %s", e)
            self.books = []

    # -------------------------
    # Utilities
    # -------------------------
    def to_dict_list(self):
        """Return list-of-dicts representation (useful for tests)."""
        return [b.to_dict() for b in self.books]