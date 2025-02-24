#todo make chapter and position ino setters and getters @properties

import json
import traceback
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
            self.create_empty_state_file()
        else:
            try:
                with self.state_file.open("r") as f:
                    self.state = json.load(f)
            except (json.JSONDecodeError, ValueError):
                print("State - Invalid JSON file. Creating a new state...")
                self.create_empty_state_file()
        return self.state
    
    def create_empty_state_file(self):
        self.state = {
                "current_book": "",
                "books": {}
            }
        self.save_state() 

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
                author, title = books.get_author_and_title(book)
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
        """Saves the state to the JSON file, with explicit error handling."""
        try:
            with self.state_file.open("w") as f:
                json.dump(self.state, f, indent=4)
            print(f"State saved successfully to {self.state_file}")
        except PermissionError:
            print(f"Error: Permission denied when trying to write to {self.state_file}")
        except FileNotFoundError:
            print(f"Error: The file {self.state_file} was not found. Check if the path is correct.")
        except IsADirectoryError:
            print(f"Error: {self.state_file} is a directory, not a file.")
        except json.JSONDecodeError:
            print("Error: Failed to serialize state data to JSON. Check for invalid data.")
        except Exception as e:
            print(f"Unexpected error while saving state: {e}")
            traceback.print_exc()

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
        book_name = self.state.get("current_book", "")
        if book_name in self.state["books"]:
            return book_name
        # Get the first book in state["books"] if no valid current book is set
        if self.state["books"]:
            first_book = next(iter(self.state["books"]))
            print(f"State - No current book set. Defaulting to first book: {first_book}")
            self.state["current_book"] = first_book
            self.save_state()
            return first_book
        # If no books are available, return an empty string
        return ""

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