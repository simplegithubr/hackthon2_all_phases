# Data Model: Todo Application

## Todo Entity

**Name**: Todo
**Description**: Represents a single task that a user wants to track

### Fields
- **id** (integer): Unique identifier for the todo item
- **title** (string): Required title of the todo (cannot be empty)
- **description** (string): Optional description of the todo (can be empty/null)
- **completed** (boolean): Status indicating whether the todo is completed (default: False)

### Validation Rules
- Title must be provided and cannot be empty
- ID must be unique within the application
- Description is optional and can be empty
- Completed status defaults to False when creating a new todo

### State Transitions
- New Todo: `completed = False` (default)
- Mark Complete: `completed = True`
- Mark Incomplete: `completed = False`

### Relationships
- Todo exists independently (no relationships to other entities)

## Todo List

**Name**: Todo List
**Description**: Collection of Todo entities stored in memory

### Operations
- Add Todo: Insert a new Todo with unique ID
- Get All Todos: Retrieve all Todo entities
- Get Todo by ID: Retrieve specific Todo by its ID
- Update Todo: Modify existing Todo by ID
- Delete Todo: Remove Todo by ID
- Mark Complete/Incomplete: Update completion status by ID

### Constraints
- All todos must have unique IDs
- Operations should provide clear error messages for invalid IDs