# Quickstart: Todo Application

## Getting Started

The Todo application is a console-based Python application that allows users to manage their tasks in memory. The application provides functionality to add, view, update, delete, and mark todos as complete or incomplete.

## Prerequisites

- Python 3.8 or higher
- No additional dependencies required (uses only standard Python libraries)

## Running the Application

1. Clone or navigate to the project directory
2. Run the application using Python:
   ```bash
   python src/main.py
   ```

## Basic Usage

The application presents a menu-based interface where users can:

1. **Add Todo**: Create a new todo with a required title and optional description
2. **View Todos**: See all todos with their ID, title, description, and completion status
3. **Update Todo**: Modify an existing todo's title and description by ID
4. **Delete Todo**: Remove a todo by ID
5. **Mark Complete/Incomplete**: Change a todo's completion status by ID
6. **Exit**: Quit the application

## Project Structure

```
src/
├── models/
│   └── todo.py          # Todo data model
├── services/
│   └── todo_service.py  # Todo business logic
├── cli/
│   └── cli_app.py       # Command-line interface
└── main.py              # Entry point
```

## Development

The application follows a clean architecture pattern:
- **Models**: Define the data structures
- **Services**: Handle business logic and operations
- **CLI**: Handle user interface and input/output
- **Main**: Entry point that orchestrates the application