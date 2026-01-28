"""
CLI Application

Provides the command-line interface for the todo application.
Handles user input and displays output.
"""
from src.services.todo_service import TodoService


class CLIApp:
    """
    Command-line interface for the todo application.
    Provides menu options and handles user interaction.
    """

    def __init__(self):
        """
        Initialize the CLI application with a TodoService instance.
        """
        self.todo_service = TodoService()
        self.running = True

    def display_menu(self):
        """
        Display the main menu options to the user.
        """
        print("\n" + "="*60)
        print("TODO APPLICATION")
        print("="*60)
        print("1. Add Todo        - Create a new todo item")
        print("2. View All Todos  - See all your todos")
        print("3. Update Todo     - Modify an existing todo")
        print("4. Delete Todo     - Remove a todo")
        print("5. Mark Complete   - Mark a todo as complete")
        print("6. Mark Incomplete - Mark a todo as incomplete")
        print("7. Exit            - Quit the application")
        print("-"*60)
        print("Instructions: Enter the number of your choice (1-7)")
        print("Tips: Use Ctrl+C at any time to exit safely")
        print("-"*60)

    def get_user_choice(self):
        """
        Get the user's menu choice.

        Returns:
            str: The user's menu choice
        """
        try:
            choice = input("Enter your choice (1-7): ").strip()
            return choice
        except (EOFError, KeyboardInterrupt):
            return "7"  # Treat as exit

    def add_todo(self):
        """
        Handle adding a new todo.
        """
        print("\n--- Add New Todo ---")
        print("Tip: A title is required, description is optional")
        try:
            title = input("Enter todo title: ").strip()
            if not title:
                print("Error: Title cannot be empty! Please enter a valid title.")
                return

            description = input("Enter todo description (optional): ").strip()

            todo = self.todo_service.add_todo(title, description)
            print(f"✓ Successfully added todo: {todo}")
        except ValueError as e:
            print(f"Error: {e}")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")

    def view_todos(self):
        """
        Handle viewing all todos.
        """
        print("\n--- All Todos ---")
        todos = self.todo_service.get_all_todos()

        if not todos:
            print("No todos found.")
            return

        for todo in todos:
            status = "✓" if todo.completed else "○"
            print(f"{status} [{todo.id}] {todo.title}")
            if todo.description:
                print(f"    Description: {todo.description}")
            print()

    def update_todo(self):
        """
        Handle updating an existing todo.
        """
        print("\n--- Update Todo ---")
        try:
            todo_id = input("Enter todo ID to update: ").strip()
            if not todo_id.isdigit():
                print("Error: Please enter a valid numeric ID.")
                return

            todo_id = int(todo_id)
            existing_todo = self.todo_service.get_todo_by_id(todo_id)
            if not existing_todo:
                print(f"Error: Todo with ID {todo_id} not found.")
                return

            print(f"Current todo: {existing_todo}")
            if existing_todo.description:
                print(f"Current description: {existing_todo.description}")

            title = input(f"Enter new title (current: '{existing_todo.title}'): ").strip()
            if title == "":
                title = None  # Use None to indicate no change

            description = input(f"Enter new description (current: '{existing_todo.description}'): ").strip()
            if description == "":
                description = None  # Use None to indicate no change

            updated_todo = self.todo_service.update_todo(todo_id, title, description)
            if updated_todo:
                print(f"Successfully updated todo: {updated_todo}")
            else:
                print("Error: Failed to update todo.")
        except ValueError as e:
            print(f"Error: {e}")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")

    def delete_todo(self):
        """
        Handle deleting a todo.
        """
        print("\n--- Delete Todo ---")
        try:
            todo_id = input("Enter todo ID to delete: ").strip()
            if not todo_id.isdigit():
                print("Error: Please enter a valid numeric ID.")
                return

            todo_id = int(todo_id)
            success = self.todo_service.delete_todo(todo_id)
            if success:
                print(f"Successfully deleted todo with ID {todo_id}.")
            else:
                print(f"Error: Todo with ID {todo_id} not found.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")

    def mark_todo_complete(self):
        """
        Handle marking a todo as complete.
        """
        print("\n--- Mark Todo Complete ---")
        try:
            todo_id = input("Enter todo ID to mark complete: ").strip()
            if not todo_id.isdigit():
                print("Error: Please enter a valid numeric ID.")
                return

            todo_id = int(todo_id)
            success = self.todo_service.mark_complete(todo_id)
            if success:
                print(f"Successfully marked todo with ID {todo_id} as complete.")
            else:
                print(f"Error: Todo with ID {todo_id} not found.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")

    def mark_todo_incomplete(self):
        """
        Handle marking a todo as incomplete.
        """
        print("\n--- Mark Todo Incomplete ---")
        try:
            todo_id = input("Enter todo ID to mark incomplete: ").strip()
            if not todo_id.isdigit():
                print("Error: Please enter a valid numeric ID.")
                return

            todo_id = int(todo_id)
            success = self.todo_service.mark_incomplete(todo_id)
            if success:
                print(f"Successfully marked todo with ID {todo_id} as incomplete.")
            else:
                print(f"Error: Todo with ID {todo_id} not found.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")

    def run(self):
        """
        Run the main application loop.
        """
        print("Welcome to the Todo Application!")
        print("Type '7' or use Ctrl+C to exit at any time.")

        while self.running:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == "1":
                self.add_todo()
            elif choice == "2":
                self.view_todos()
            elif choice == "3":
                self.update_todo()
            elif choice == "4":
                self.delete_todo()
            elif choice == "5":
                self.mark_todo_complete()
            elif choice == "6":
                self.mark_todo_incomplete()
            elif choice == "7":
                self.running = False
                print("Goodbye!")
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")