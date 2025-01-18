from pathlib import Path
import config
import os

class Books:
    def __init__(self):
        # Load books on initialization, assuming they are directories inside AUDIO_FOLDER
        self.books = self.get_books()

    def get_books(self):
        """Returns a list of available book directories."""
        
        book_folders = []
        
        # Iterate over all subdirectories (books) in AUDIO_FOLDER
        for d in Path(config.AUDIO_FOLDER).iterdir():
            if d.is_dir():  # Check if it's a directory
                # Use get_number_of_chapters to check if the book has MP3 files
                if self.get_number_of_chapters(d.name) > 0:
                    book_folders.append(d.name)

        return book_folders

    def get_title_and_author(self, book):
        """Fetches the title and author of the book (for example purposes, assume format 'Author - Title')."""
        # Split folder na,e by -
        if book in self.books:
            author, title = book.split("-")
            return author, title
        else:
            raise ValueError(f"Book {book} not found in the list of available books.")

    def get_number_of_chapters(self, book):
        """Returns the number of chapters (MP3 files) in the book."""
        if book in self.books:
            mp3_files = self.get_file_list(book)
            return len(mp3_files)
        else:
            raise ValueError(f"Book {book} not found in the list of available books.")
     
    def get_file_list(self, book):
        """Returns the list of MP3 files for a book."""
        if book in self.books:
            # Get the path to the selected book folder
            book_path = self.get_path(book)
            # Get and return the list of MP3 files in the book folder
            mp3_files = sorted([
                    f for f in book_path.glob("*.mp3") if not f.name.startswith("._")
            ])
            return mp3_files    
        else:
            raise ValueError(f"Book {book} not found in the list of available books.")

    def get_path(self, book):
        if book in self.books:
            book_path = Path(config.AUDIO_FOLDER) / book
            return book_path
        else:
            raise ValueError(f"Book name {book} is not found in the audio folder.")

