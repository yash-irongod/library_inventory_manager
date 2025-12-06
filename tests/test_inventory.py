# tests/test_inventory.py
import os
import tempfile
import json
import pytest

from library_manager import Book, LibraryInventory

def test_add_and_persist(tmp_path):
    storage = tmp_path / "test_catalog.json"
    inv = LibraryInventory(storage)
    assert inv.to_dict_list() == []

    b1 = Book(title="Test Book", author="Author", isbn="ISBN123")
    inv.add_book(b1)
    inv.save()

    # load into new instance
    inv2 = LibraryInventory(storage)
    assert len(inv2.books) == 1
    assert inv2.books[0].title == "Test Book"

def test_issue_and_return(tmp_path):
    storage = tmp_path / "test_catalog.json"
    inv = LibraryInventory(storage)
    b = Book(title="Issue Book", author="Auth", isbn="I-1")
    inv.add_book(b)
    inv.save()

    assert inv.issue_book_by_isbn("I-1") is True
    assert inv.find_by_isbn("I-1").status == "issued"

    assert inv.return_book_by_isbn("I-1") is True
    assert inv.find_by_isbn("I-1").status == "available"

    # non-existing ISBN
    assert inv.issue_book_by_isbn("nope") is False