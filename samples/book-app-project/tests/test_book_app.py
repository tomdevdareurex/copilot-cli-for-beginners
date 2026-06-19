import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import builtins
import pytest
import books
from books import BookCollection
import book_app


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def feed_input(monkeypatch, responses):
    """Make input() return each item from responses in order."""
    answers = iter(responses)
    monkeypatch.setattr(builtins, "input", lambda *args: next(answers))


def test_handle_add_success(monkeypatch, capsys):
    feed_input(monkeypatch, ["Dune", "Frank Herbert", "1965"])
    collection = BookCollection()
    book_app.handle_add(collection)
    out = capsys.readouterr().out
    assert "Book added successfully" in out
    assert collection.find_book_by_title("Dune") is not None


def test_handle_add_requires_title_and_author(monkeypatch, capsys):
    feed_input(monkeypatch, ["", "Someone"])
    collection = BookCollection()
    book_app.handle_add(collection)
    out = capsys.readouterr().out
    assert "Title and author are required" in out
    assert collection.list_books() == []


def test_handle_add_invalid_year(monkeypatch, capsys):
    feed_input(monkeypatch, ["Dune", "Frank Herbert", "not-a-year"])
    collection = BookCollection()
    book_app.handle_add(collection)
    out = capsys.readouterr().out
    assert "Year must be a whole number" in out
    assert collection.find_book_by_title("Dune") is None


def test_handle_add_blank_year_defaults_to_zero(monkeypatch):
    feed_input(monkeypatch, ["Dune", "Frank Herbert", ""])
    collection = BookCollection()
    book_app.handle_add(collection)
    book = collection.find_book_by_title("Dune")
    assert book is not None
    assert book.year == 0


def test_handle_remove_existing(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    feed_input(monkeypatch, ["The Hobbit"])
    book_app.handle_remove(collection)
    out = capsys.readouterr().out
    assert 'Removed "The Hobbit"' in out
    assert collection.find_book_by_title("The Hobbit") is None


def test_handle_remove_missing(monkeypatch, capsys):
    collection = BookCollection()
    feed_input(monkeypatch, ["Nonexistent"])
    book_app.handle_remove(collection)
    out = capsys.readouterr().out
    assert "No book titled" in out


def test_handle_read_existing(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    feed_input(monkeypatch, ["Dune"])
    book_app.handle_read(collection)
    out = capsys.readouterr().out
    assert 'Marked "Dune" as read' in out
    assert collection.find_book_by_title("Dune").read is True


def test_handle_read_missing(monkeypatch, capsys):
    collection = BookCollection()
    feed_input(monkeypatch, ["Nope"])
    book_app.handle_read(collection)
    out = capsys.readouterr().out
    assert "No book titled" in out


def test_main_unknown_command(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["book_app.py", "bogus"])
    book_app.main()
    out = capsys.readouterr().out
    assert "Unknown command" in out


def test_handle_list_empty(capsys):
    collection = BookCollection()
    book_app.handle_list(collection)
    out = capsys.readouterr().out
    assert "No books in your collection" in out


def test_handle_list_with_books(capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    book_app.handle_list(collection)
    out = capsys.readouterr().out
    assert "Dune" in out
    assert "The Hobbit" in out


def test_handle_find_matching_author(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.add_book("Dune Messiah", "Frank Herbert", 1969)
    feed_input(monkeypatch, ["Frank Herbert"])
    book_app.handle_find(collection)
    out = capsys.readouterr().out
    assert "Dune" in out
    assert "Dune Messiah" in out


def test_handle_find_case_insensitive(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    feed_input(monkeypatch, ["frank herbert"])
    book_app.handle_find(collection)
    out = capsys.readouterr().out
    assert "Dune" in out


def test_handle_find_no_match(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    feed_input(monkeypatch, ["Unknown Author"])
    book_app.handle_find(collection)
    out = capsys.readouterr().out
    assert "No books" in out


def test_handle_remove_is_case_insensitive(monkeypatch, capsys):
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    feed_input(monkeypatch, ["the hobbit"])
    book_app.handle_remove(collection)
    out = capsys.readouterr().out
    assert 'Removed "the hobbit"' in out
    assert collection.find_book_by_title("The Hobbit") is None


def test_show_help_lists_commands(capsys):
    book_app.show_help()
    out = capsys.readouterr().out
    for command in ("list", "add", "remove", "find", "read", "help"):
        assert command in out


def test_main_no_arguments_shows_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["book_app.py"])
    book_app.main()
    out = capsys.readouterr().out
    assert "Book Collection Helper" in out


def test_main_help_command(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["book_app.py", "help"])
    book_app.main()
    out = capsys.readouterr().out
    assert "Book Collection Helper" in out


def test_main_command_is_case_insensitive(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["book_app.py", "LIST"])
    book_app.main()
    out = capsys.readouterr().out
    assert "No books in your collection" in out


def test_main_dispatches_to_handler(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["book_app.py", "list"])
    book_app.main()
    out = capsys.readouterr().out
    assert "No books in your collection" in out


def test_main_handles_cancellation(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["book_app.py", "add"])

    def raise_eof(*args):
        raise EOFError

    monkeypatch.setattr(builtins, "input", raise_eof)
    book_app.main()
    out = capsys.readouterr().out
    assert "Cancelled" in out
