# cli/main.py
"""
Simple CLI front-end for the Library Inventory Manager.
Run: python -m cli.main
"""

import logging
from pathlib import Path
from typing import Optional

from library_manager import Book, LibraryInventory

# Configure root logger for the CLI (console)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def prompt_non_empty(prompt_text: str) -> str:
    while True:
        s = input(prompt_text).strip()
        if s:
            return s
        print("Input cannot be empty. Please try again.")


def add_book_flow(inventory: LibraryInventory) -> None:
    title = prompt_non_empty("Title: ")
    author = prompt_non_empty("Author: ")
    isbn = prompt_non_empty("ISBN: ")
    book = Book(title=title, author=author, isbn=isbn)
    inventory.add_book(book)
    inventory.save()
    print("Book added.")


def issue_book_flow(inventory: LibraryInventory) -> None:
    isbn = prompt_non_empty("Enter ISBN to issue: ")
    if inventory.issue_book_by_isbn(isbn):
        print("Book issued.")
    else:
        print("Could not issue book. Check ISBN or availability.")


def return_book_flow(inventory: LibraryInventory) -> None:
    isbn = prompt_non_empty("Enter ISBN to return: ")
    if inventory.return_book_by_isbn(isbn):
        print("Book returned.")
    else:
        print("Could not return book. Check ISBN or status.")


def view_all_flow(inventory: LibraryInventory) -> None:
    lines = inventory.display_all()
    if not lines:
        print("No books in catalog.")
    else:
        print("\nCatalog:")
        print("-" * 60)
        for line in lines:
            print(line)
        print("-" * 60)


def search_flow(inventory: LibraryInventory) -> None:
    print("Search by: 1) Title  2) Author  3) ISBN")
    choice = input("Choice (1/2/3): ").strip()
    if choice == "1":
        q = prompt_non_empty("Title query: ")
        results = inventory.search_by_title(q)
    elif choice == "2":
        q = prompt_non_empty("Author query: ")
        results = inventory.search_by_author(q)
    elif choice == "3":
        q = prompt_non_empty("ISBN: ")
        book = inventory.find_by_isbn(q)
        results = [book] if book else []
    else:
        print("Invalid choice.")
        return

    if not results:
        print("No results found.")
        return
    print(f"Found {len(results)} result(s):")
    for b in results:
        print(b)


def main():
    # default storage in project root
    storage = Path("catalog.json")
    inventory = LibraryInventory(storage)
    print("Welcome to Library Inventory Manager (CLI)")
    while True:
        print("\nMenu:")
        print("  1) Add Book")
        print("  2) Issue Book")
        print("  3) Return Book")
        print("  4) View All Books")
        print("  5) Search")
        print("  6) Exit")
        choice = input("Select option (1-6): ").strip()
        try:
            if choice == "1":
                add_book_flow(inventory)
            elif choice == "2":
                issue_book_flow(inventory)
            elif choice == "3":
                return_book_flow(inventory)
            elif choice == "4":
                view_all_flow(inventory)
            elif choice == "5":
                search_flow(inventory)
            elif choice == "6":
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Enter 1-6.")
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break
        except Exception as e:
            logger.exception("An unexpected error occurred: %s", e)
            print("An error occurred. Check logs for details.")


if __name__ == "__main__":
    main()