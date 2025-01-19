#todo make chapter and position ino setters and getters @properties

import json
from pathlib import Path
import config
from books import books

class State:
    def __init__(self):
        self.state_file = Path(config.STATE_FILE)
        self.state = self.load_state()
        self.load_books()

    def load_state(self):
        """Loads the current state from the JSON file or creates a new one if it doesn't exist."""
        if not self.state_file.exists():
            print("State - State file not found. Creating a new one...")
            # Default state structure
            state = {
                "current_book": "",
                "books": {}
            }
            self.save_state(state)
        else:
            with self.state_file.open("r") as f:
                state = json.load(f)
        return state

    def load_books(self):
        """Loads all books via `books.get_books()` and updates the state file."""
        book_folders = books.get_books()

        # Extract the current list of books in the state
        existing_books = set(self.state["books"].keys())
        new_books = set(book_folders)

        # Add new books
        for book in book_folders:
            if book not in existing_books:
                print(f"State - Adding new book: {book}")
                author, title = books.get_title_and_author(book)
                self.state["books"][book] = {
                    "position": 0,
                    "chapter": 0,
                }

        # Remove non-existent books
        for book in existing_books:
            if book not in new_books:
                print(f"State - Removing book: {book}")
                del self.state["books"][book]

        # Ensure the current book is valid
        if self.state["current_book"] not in book_folders:
            if book_folders:
                self.state["current_book"] = book_folders[0]
            else:
                self.state["current_book"] = ""

        # Save changes
        self.save_state()

    def save_state(self):
        """Saves the state to the JSON file."""
        with self.state_file.open("w") as f:
            json.dump(self.state, f, indent=4)

    @property
    def position(self):
        return self.current_book_data.get("position", 0)
   
    @position.setter
    def position(self, position):
        self.current_book_data["position"] = position
        self.save_state()

    @property
    def chapter(self):
        return self.current_book_data.get("chapter", 0)
   
    @chapter.setter
    def chapter(self, chapter):
        self.current_book_data["chapter"] = chapter
        self.save_state()

    @property
    def current_book(self):
        """Returns the current book name."""
        return self.state.get("current_book", "")

    @current_book.setter
    def current_book(self, book_name):
        """Sets the current book and validates it exists in the state."""
        if book_name in self.state["books"]:
            self.state["current_book"] = book_name
            self.save_state()
        else:
            print(f"State - current_book(): Book '{book_name}' not found in the state.")

    @property
    def current_book_data(self):
        """Returns the data for the current book."""
        book_name = self.current_book
        return self.state["books"].get(book_name, None)

state = State()  # Create a single global instance