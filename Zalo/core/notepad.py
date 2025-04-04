import json
import os
from datetime import datetime


class Notepad:
    def __init__(self, filename="notes.json"):
        """Initialize the Notepad with a JSON storage file.
        
        Args:
            filename (str): Path to the JSON file for storing notes.
        """
        self.filename = filename
        self.notes = self._load_notes()

    def _load_notes(self):
        """Load notes from JSON file."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        return {}

    def _save_notes(self):
        """Save notes to JSON file."""
        with open(self.filename, 'w') as file:
            json.dump(self.notes, file, indent=4)

    def add_note(self, title, content):
        """Add a new note.
        
        Args:
            title (str): Note title (used as key)
            content (str): Note content
            
        Returns:
            str: Confirmation message
        """
        self.notes[title] = {
            'content': content,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_notes()
        return f"Note '{title}' saved successfully."

    def get_note(self, title):
        """Retrieve a note by title.
        
        Args:
            title (str): Title of the note to retrieve
            
        Returns:
            str/dict: Note content if found, else error message
        """
        return self.notes.get(title, "Note not found.")

    def list_notes(self):
        """List all note titles.
        
        Returns:
            list: All note titles or empty list
        """
        return list(self.notes.keys())

    def delete_note(self, title):
        """Delete a note.
        
        Args:
            title (str): Title of note to delete
            
        Returns:
            str: Confirmation message
        """
        if title in self.notes:
            del self.notes[title]
            self._save_notes()
            return f"Note '{title}' deleted."
        return "Note not found."

    def update_note(self, title, new_content):
        """Update an existing note.
        
        Args:
            title (str): Title of note to update
            new_content (str): New content
            
        Returns:
            str: Confirmation message
        """
        if title in self.notes:
            self.notes[title]['content'] = new_content
            self.notes[title]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_notes()
            return f"Note '{title}' updated."
        return "Note not found."