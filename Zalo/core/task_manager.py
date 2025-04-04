import json
from datetime import datetime, timedelta
import os

class TaskManager:
    def __init__(self, tasks_path="tasks.json"):
        """
        Initialize the Task Manager
        
        :param tasks_path: Path to the tasks JSON file
        """
        # Ensure paths work on different platforms
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.tasks_path = os.path.join(base_dir, tasks_path)
        except:
            self.tasks_path = tasks_path
        
        # Load tasks
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """
        Load tasks from JSON file
        
        :return: Dictionary of tasks
        """
        try:
            if not os.path.exists(self.tasks_path):
                # Create an empty tasks file if it doesn't exist
                base_tasks = {
                    "active_tasks": [],
                    "completed_tasks": []
                }
                with open(self.tasks_path, 'w') as file:
                    json.dump(base_tasks, file, indent=4)
                return base_tasks
            
            with open(self.tasks_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return {"active_tasks": [], "completed_tasks": []}

    def save_tasks(self):
        """
        Save tasks to JSON file
        """
        try:
            with open(self.tasks_path, 'w') as file:
                json.dump(self.tasks, file, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, task_name, due_date=None, priority=None):
        """
        Add a new task
        
        :param task_name: Name of the task
        :param due_date: Optional due date for the task
        :param priority: Optional priority of the task
        :return: Confirmation message
        """
        # Generate a unique task ID
        task_id = len(self.tasks["active_tasks"]) + 1
        
        # Create task dictionary
        task = {
            "id": task_id,
            "name": task_name,
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "priority": priority,
            "status": "active"
        }
        
        # Add to active tasks
        self.tasks["active_tasks"].append(task)
        
        # Save tasks
        self.save_tasks()
        
        return f"Task '{task_name}' added successfully with ID {task_id}!"

    def edit_task(self, task_id, **kwargs):
        """
        Edit an existing task
        
        :param task_id: ID of the task to edit
        :param kwargs: Keyword arguments for task attributes to modify
        :return: Confirmation message
        """
        for task in self.tasks["active_tasks"]:
            if task["id"] == task_id:
                # Update specified attributes
                for key, value in kwargs.items():
                    task[key] = value
                
                # Save changes
                self.save_tasks()
                return f"Task {task_id} updated successfully!"
        
        return f"Task {task_id} not found."

    def list_tasks(self, status="active", filter_by=None):
        """
        List tasks with advanced filtering
        
        :param status: Status of tasks to list
        :param filter_by: Dictionary of filter conditions
        :return: Formatted list of tasks
        """
        if status not in ["active", "completed"]:
            return "Invalid status. Use 'active' or 'completed'."
        
        tasks_list = self.tasks.get(f"{status}_tasks", [])
        
        # Apply filters if provided
        if filter_by:
            filtered_tasks = []
            for task in tasks_list:
                match = True
                for key, value in filter_by.items():
                    if task.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_tasks.append(task)
            tasks_list = filtered_tasks
        
        if not tasks_list:
            return f"No {status} tasks found."
        
        # Format tasks for display
        formatted_tasks = [
            f"ID: {task['id']}, Name: {task['name']}, " + 
            (f"Due: {task['due_date']}, " if task.get('due_date') else "") +
            (f"Priority: {task['priority']}" if task.get('priority') else "")
            for task in tasks_list
        ]
        
        return "\n".join(formatted_tasks)

    def check_due_tasks(self):
        """
        Check for and return tasks that are due soon
        
        :return: List of due tasks
        """
        current_time = datetime.now()
        due_tasks = []
        
        for task in self.tasks["active_tasks"]:
            if task.get('due_date'):
                due_date = datetime.fromisoformat(task['due_date'])
                time_to_due = due_date - current_time
                
                # Check if task is due within the next 24 hours
                if timedelta(0) <= time_to_due <= timedelta(days=1):
                    due_tasks.append({
                        'id': task['id'],
                        'name': task['name'],
                        'due_date': task['due_date']
                    })
        
        return due_tasks

    def get_reminders(self):
        """
        Get formatted reminder messages
        
        :return: String of reminder messages
        """
        due_tasks = self.check_due_tasks()
        if not due_tasks:
            return "No upcoming tasks due in the next 24 hours."
        
        reminder_messages = ["Upcoming Tasks:"]
        for task in due_tasks:
            reminder_messages.append(
                f"- Task {task['id']}: {task['name']} (Due: {task['due_date']})"
            )
        
        return "\n".join(reminder_messages)

    def complete_task(self, task_id):
        """
        Mark a task as completed
        
        :param task_id: ID of the task to complete
        :return: Confirmation message
        """
        for task in self.tasks["active_tasks"]:
            if task["id"] == task_id:
                # Remove from active tasks
                self.tasks["active_tasks"].remove(task)
                
                # Add to completed tasks
                task["completed_at"] = datetime.now().isoformat()
                task["status"] = "completed"
                self.tasks["completed_tasks"].append(task)
                
                # Save changes
                self.save_tasks()
                
                return f"Task {task_id} marked as completed!"
        
        return f"Task {task_id} not found."