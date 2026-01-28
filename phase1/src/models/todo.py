"""
Todo Model

Represents a single task that a user wants to track.
"""


class Todo:
    """
    Represents a single todo item with id, title, description, and completion status.
    """

    def __init__(self, todo_id, title, description="", completed=False):
        """
        Initialize a Todo instance.

        Args:
            todo_id (int): Unique identifier for the todo item
            title (str): Required title of the todo (cannot be empty)
            description (str): Optional description of the todo (can be empty)
            completed (bool): Status indicating whether the todo is completed (default: False)
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        self.id = todo_id
        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.completed = completed

    def __str__(self):
        """
        String representation of the Todo.

        Returns:
            str: Formatted string showing the todo details
        """
        status = "Complete" if self.completed else "Incomplete"
        return f"[{self.id}] {self.title} - {status}"

    def __repr__(self):
        """
        Developer-friendly representation of the Todo.

        Returns:
            str: Detailed representation of the Todo object
        """
        return f"Todo(id={self.id}, title='{self.title}', description='{self.description}', completed={self.completed})"

    def to_dict(self):
        """
        Convert the Todo to a dictionary representation.

        Returns:
            dict: Dictionary containing all todo attributes
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }

    def mark_complete(self):
        """
        Mark the todo as complete.
        """
        self.completed = True

    def mark_incomplete(self):
        """
        Mark the todo as incomplete.
        """
        self.completed = False