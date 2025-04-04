import json
import os
from datetime import datetime


class NotesManager:
    def __init__(self, notes_file="notes.json"):
        """Initialize the NotesManager with a JSON file for storage.
        
        :param notes_file: Path to the JSON file for storing notes
        """
        self.notes_file = notes_file
        self.notes = self.load_notes()

    def load_notes(self):
        """Load notes from JSON file.
        
        :return: Dictionary containing all notes
        """
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r") as file:
                return json.load(file)
        return {}

    def save_notes(self):
        """Save notes to JSON file."""
        with open(self.notes_file, "w") as file:
            json.dump(self.notes, file, indent=4)

    def add_note(self, title, content):
        """Add a new note.
        
        :param title: Title of the note
        :param content: Content of the note
        :return: Confirmation message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes[title] = {
            "content": content,
            "timestamp": timestamp
        }
        self.save_notes()
        return f"Note '{title}' saved."

    def get_note(self, title):
        """Retrieve a note by title.
        
        :param title: Title of the note to retrieve
        :return: Note content or 'not found' message
        """
        return self.notes.get(title, "Note not found.")

    def list_notes(self):
        """List all saved notes.
        
        :return: List of note titles or 'no notes' message
        """
        return list(self.notes.keys()) if self.notes else "No notes available."

    def delete_note(self, title):
        """Delete a note.
        
        :param title: Title of the note to delete
        :return: Confirmation message
        """
        if title in self.notes:
            del self.notes[title]
            self.save_notes()
            return f"Note '{title}' deleted."
        return "Note not found."

    def edit_note(self, title, new_content):
        """Edit an existing note.
        
        :param title: Title of the note to edit
        :param new_content: New content for the note
        :return: Confirmation message
        """
        if title in self.notes:
            self.notes[title]["content"] = new_content
            self.notes[title]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_notes()
            return f"Note '{title}' updated."
        return "Note not found."


# Example Usage
if __name__ == "__main__":
    notes_manager = NotesManager()
    
    # Corrected method name from 'add_note' (was 'add_note')
    print(notes_manager.add_note("Meeting", "Discuss project updates"))
    print(notes_manager.get_note("Meeting"))
    print(notes_manager.list_notes())
    print(notes_manager.edit_note("Meeting", "Discuss project updates and deadlines"))
    print(notes_manager.delete_note("Meeting"))