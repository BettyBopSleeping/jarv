import re
from core.notepad import Notepad
from core.conversation_handler import ConversationHandler
from core.knowledge_base import KnowledgeBase
from core.task_manager import TaskManager

class ZaloCore:
    def __init__(self, name="Zalo"):
        self.name = name
        self.notepad = Notepad()
        self.conversation_handler = ConversationHandler(name)
        self.task_manager = TaskManager()  # Keep but don't show commands
        self.knowledge_base = KnowledgeBase()  # Keep but don't show commands

    def respond(self, user_input):
        # Notepad commands
        if user_input.startswith("save note"):
            content = user_input.replace("save note", "").strip()
            return self.notepad.add_note("Untitled", content)
        elif user_input.startswith("list notes"):
            notes = self.notepad.list_notes()
            return "\n".join(notes) if notes else "No notes found"
        elif user_input.startswith("view note"):
            title = user_input.replace("view note", "").strip()
            note = self.notepad.get_note(title)
            return note if note != "Note not found." else note
        elif user_input.startswith("delete note"):
            title = user_input.replace("delete note", "").strip()
            return self.notepad.delete_note(title)

        # Task commands (still work but not shown at startup)
        task_match = re.match(r'add task (.+)', user_input, re.IGNORECASE)
        if task_match:
            return self.task_manager.add_task(task_match.group(1))
        
        # Knowledge commands (still work but not shown)
        learn_match = re.match(r'/learn\s+(\w+)\s+(.+)', user_input)
        if learn_match:
            return self.knowledge_base.learn(learn_match.group(1), learn_match.group(2))

        # General conversation
        return self.conversation_handler.handle_conversation(user_input)

    def interactive_mode(self):
        print("(Type 'help' to see available commands)")
        print(f"{self.name}: Hello! How can I help you today?")
        
        
        while True:
            user_input = input("You: ").strip().lower()
            
            if user_input in ['bye', 'exit', 'quit']:
                print(f"{self.name}: Goodbye!")
                break
            elif user_input == 'help':
                print("\nAvailable commands:")
                print("Notepad:")
                print("- save note [content]")
                print("- list notes")
                print("- view note [title]")
                print("- delete note [title]")
                print("\nTasks:")
                print("- add task [description]")
                print("- list tasks")
                print("- complete task [id]")
                print("\nLearning:")
                print("- /learn [topic] [information]")
            else:
                response = self.respond(user_input)
                print(f"{self.name}: {response}")

if __name__ == "__main__":
    assistant = ZaloCore()
    assistant.interactive_mode()