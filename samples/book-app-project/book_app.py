import sys

from books import BookCollection
from utils import print_books


def handle_list(collection):
    """Show every book in the collection."""
    print_books(collection.list_books())


def handle_add(collection):
    """Prompt for book details and add the book."""
    print("\nAdd a New Book\n")

    title = input("Title: ").strip()
    author = input("Author: ").strip()

    if not title or not author:
        print("\nError: Title and author are required.\n")
        return

    year_str = input("Year: ").strip()
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            print("\nError: Year must be a whole number.\n")
            return
    else:
        year = 0

    collection.add_book(title, author, year)
    print("\nBook added successfully.\n")


def handle_remove(collection):
    """Remove a book by title and report whether it was found."""
    print("\nRemove a Book\n")

    title = input("Enter the title of the book to remove: ").strip()

    if collection.remove_book(title):
        print(f'\nRemoved "{title}".\n')
    else:
        print(f'\nNo book titled "{title}" was found.\n')


def handle_find(collection):
    """List all books by a given author."""
    print("\nFind Books by Author\n")

    author = input("Author name: ").strip()
    print_books(collection.find_by_author(author))


def handle_read(collection):
    """Mark a book as read by title and report whether it was found."""
    print("\nMark a Book as Read\n")

    title = input("Enter the title of the book to mark as read: ").strip()

    if collection.mark_as_read(title):
        print(f'\nMarked "{title}" as read.\n')
    else:
        print(f'\nNo book titled "{title}" was found.\n')


def show_help():
    """Print the list of available commands."""
    print("""
Book Collection Helper

Commands:
  list     - Show all books
  add      - Add a new book
  remove   - Remove a book by title
  find     - Find books by author
  read     - Mark a book as read
  help     - Show this help message
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "help":
        show_help()
        return

    handlers = {
        "list": handle_list,
        "add": handle_add,
        "remove": handle_remove,
        "find": handle_find,
        "read": handle_read,
    }

    handler = handlers.get(command)
    if handler is None:
        print("Unknown command.\n")
        show_help()
        return

    collection = BookCollection()
    try:
        handler(collection)
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.\n")


if __name__ == "__main__":
    main()
