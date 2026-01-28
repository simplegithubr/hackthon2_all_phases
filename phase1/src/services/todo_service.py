"""
Todo Service

Handles all business logic for todo operations including adding, viewing,
updating, deleting, and marking todos as complete/incomplete.
"""
from src.models.todo import Todo


class TodoService:
    """
    Service class to handle all todo operations.
    Stores todos in memory only.
    """

    def __init__(self):
        """
        Initialize the TodoService with an empty list of todos and ID counter.
        """
        self.todos = []
        self._next_id = 1

    def add_todo(self, title, description=""):
        """
        Add a new todo with the given title and optional description.

        Args:
            title (str): Required title of the todo
            description (str): Optional description of the todo

        Returns:
            Todo: The newly created Todo object

        Raises:
            ValueError: If title is empty
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # Create new todo with unique ID
        new_todo = Todo(todo_id=self._next_id, title=title, description=description, completed=False)
        self.todos.append(new_todo)

        # Increment ID for next todo
        self._next_id += 1

        return new_todo

    def get_all_todos(self):
        """
        Get all todos in the system.

        Returns:
            list: List of all Todo objects
        """
        return self.todos.copy()

    def get_todo_by_id(self, todo_id):
        """
        Get a specific todo by its ID.

        Args:
            todo_id (int): The ID of the todo to retrieve

        Returns:
            Todo: The Todo object with the given ID, or None if not found
        """
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def update_todo(self, todo_id, title=None, description=None):
        """
        Update an existing todo's title and/or description.

        Args:
            todo_id (int): The ID of the todo to update
            title (str, optional): New title for the todo
            description (str, optional): New description for the todo

        Returns:
            Todo: The updated Todo object, or None if todo doesn't exist

        Raises:
            ValueError: If the new title is empty
        """
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            return None

        # If title is provided, validate it
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Title cannot be empty")
            todo.title = title.strip()

        # If description is provided, update it
        if description is not None:
            todo.description = description.strip() if description else ""

        return todo

    def delete_todo(self, todo_id):
        """
        Delete a todo by its ID.

        Args:
            todo_id (int): The ID of the todo to delete

        Returns:
            bool: True if the todo was deleted, False if it didn't exist
        """
        todo = self.get_todo_by_id(todo_id)
        if todo:
            self.todos.remove(todo)
            return True
        return False

    def mark_complete(self, todo_id):
        """
        Mark a todo as complete by its ID.

        Args:
            todo_id (int): The ID of the todo to mark as complete

        Returns:
            bool: True if the todo was marked complete, False if it didn't exist
        """
        todo = self.get_todo_by_id(todo_id)
        if todo:
            todo.mark_complete()
            return True
        return False

    def mark_incomplete(self, todo_id):
        """
        Mark a todo as incomplete by its ID.

        Args:
            todo_id (int): The ID of the todo to mark as incomplete

        Returns:
            bool: True if the todo was marked incomplete, False if it didn't exist
        """
        todo = self.get_todo_by_id(todo_id)
        if todo:
            todo.mark_incomplete()
            return True
        return False