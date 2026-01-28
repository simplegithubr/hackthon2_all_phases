# Todo Application

A simple in-memory console-based todo application built with Python.

## Features

- Add new todos with titles and optional descriptions
- View all todos with their completion status
- Update existing todos
- Delete todos
- Mark todos as complete or incomplete

## Requirements

- Python 3.8 or higher

## Usage

Run the application with:

```bash
python main.py
```

Follow the on-screen menu prompts to interact with your todos.

## Known Limitations

- Todos are stored only in memory and will be lost when the application exits
- No persistent storage (no file or database integration)
- Single-user application (no user accounts or sharing)
- Console-based interface only (no GUI or web interface)

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

tests/
├── unit/
│   ├── models/
│   └── services/
├── integration/
└── cli/
```

## Architecture

The application follows a clean architecture pattern:
- **Models**: Define the data structures
- **Services**: Handle business logic and operations
- **CLI**: Handle user interface and input/output
- **Main**: Entry point that orchestrates the application