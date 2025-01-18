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
        """Loads the current state from the JSON file, or creates a new one if it doesn't exist."""
        if not self.state_file.exists():
            print("State file not found. Creating a new one...")
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
        """Loads all books from AUDIO_FOLDER via books.get_books() and updates the state file."""
        # Get the list of book folders using the global books instance
        book_folders = books.get_books()

        # Extract the current list of books in the state
        existing_books = set(self.state["books"].keys())
        new_books = set(book_folders)

        # Add new books or update existing ones
        for book in book_folders:
            if book not in existing_books:
                print(f"Adding new book: {book}")
                # Get author and title from the global books instance
                author, title = books.get_title_and_author(book)
                print(f"{title} by {author}")
                self.state["books"][book] = {
                    "position": 0,
                    "chapter": 0,
                }

        # Remove books that no longer exist
        for book in existing_books:
            if book not in new_books:
                print(f"Removing book: {book}")
                del self.state["books"][book]

        # Validate the current book
        if self.state["current_book"] not in book_folders:
            print(f"Current book {self.state['current_book']} not found, using the first available book.")
            self.state["current_book"] = book_folders[0] if book_folders else ""

        # Save the updated state
        self.save_state()
        return self.state

    def save_state(self):
        """Saves the state to the JSON file."""
        with self.state_file.open("w") as f:
            json.dump(self.state, f, indent=4)

    @property
    def current_book(self):
        """Returns the data for the current book as a shorthand."""
        book_name = self.state["current_book"]
        if book_name and book_name in self.state["books"]:
            return self.state["books"][book_name]
        else:
            print("No valid current book selected.")
            return None

    @current_book.setter
    def current_book(self, book_name):
        """Sets the current book and validates if it exists in the state."""
        if book_name in self.state["books"]:
            self.state["current_book"] = book_name
            print(f"Current book set to: {book_name}")
            self.save_state()
        else:
            print(f"Book '{book_name}' not found in the state. Cannot set as current book.")

    def get_position(self):
        """Returns the progress of the current book."""
        if self.current_book:
            return self.current_book.get("position", 0)
        else:
            print("No current book selected.")
            return None

    def get_chapter(self):
        """Returns the duration of the current book."""
        if self.current_book:
            return self.current_book.get("chapter", 0)
        else:
            print("No current book selected.")
            return None

    def set_position(self, progress):
        """Sets the progress for the current book."""
        if self.current_book:
            self.current_book["position"] = progress
            self.save_state()
        else:
            print("No current book selected. Cannot set progress.")

    def set_chapter(self, duration):
        """Sets the duration for the current book."""
        if self.current_book:
            self.current_book["chapter"] = duration
            self.save_state()
        else:
            print("No current book selected. Cannot set duration.")