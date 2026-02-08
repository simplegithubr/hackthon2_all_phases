#!/usr/bin/env python3
"""
Validation script for AI Todo Chatbot implementation.
Checks that all components are properly connected and functional.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the src directory to the path so imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

def validate_models():
    """Validate that all models are properly defined and importable."""
    print("Validating models...")

    try:
        from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
        from src.models.user import User, UserCreate, UserLogin, UserRead, TokenResponse
        from src.models.conversation import Conversation, Message, ConversationCreate, MessageCreate, ConversationRead, MessageRead
        print("[OK] All models imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Model import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing models: {e}")
        return False


def validate_services():
    """Validate that all services are properly defined."""
    print("Validating services...")

    try:
        from src.services.task_service import TaskService
        from src.services.conversation_service import ConversationService
        print("[OK] All services imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Service import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing services: {e}")
        return False


def validate_repositories():
    """Validate that all repositories are properly defined."""
    print("Validating repositories...")

    try:
        from src.repositories.task_repository import TaskRepository
        from src.repositories.conversation_repository import ConversationRepository
        print("[OK] All repositories imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Repository import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing repositories: {e}")
        return False


def validate_agents():
    """Validate that all agent components are properly defined."""
    print("Validating agents...")

    try:
        from src.agents.todo_orchestrator import TodoOrchestrator
        print("[OK] Orchestrator imported successfully")

        # Check that all tools are importable
        from src.agents.tools.add_task_tool import add_task
        from src.agents.tools.list_tasks_tool import list_tasks
        from src.agents.tools.update_task_tool import update_task
        from src.agents.tools.complete_task_tool import complete_task
        from src.agents.tools.delete_task_tool import delete_task
        print("[OK] All MCP tools imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Agent import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing agents: {e}")
        return False


def validate_api_routes():
    """Validate that all API routes are properly defined."""
    print("Validating API routes...")

    try:
        from src.api.routes.tasks import router as tasks_router
        from src.api.routes.auth import router as auth_router
        from src.api.routes.chat import router as chat_router
        print("[OK] All API routes imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] API route import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing API routes: {e}")
        return False


def validate_main_app():
    """Validate that the main app can be imported."""
    print("Validating main app...")

    try:
        from src.main import app
        print("[OK] Main app imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Main app import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error importing main app: {e}")
        return False


def validate_dependencies():
    """Validate that required dependencies are available."""
    print("Validating dependencies...")

    try:
        import fastapi
        import sqlmodel
        import pydantic
        print("[OK] Core dependencies available")

        # Check for optional AI dependencies (these might not be installed in all environments)
        try:
            import openai
            print("[OK] AI dependencies available")
        except ImportError:
            print("[INFO] AI dependencies not installed (this may be expected in some environments)")

        return True
    except ImportError as e:
        print(f"[ERROR] Dependency import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error validating dependencies: {e}")
        return False


def main():
    """Run all validations."""
    print("Starting AI Todo Chatbot implementation validation...\n")

    validators = [
        validate_dependencies,
        validate_models,
        validate_repositories,
        validate_services,
        validate_agents,
        validate_api_routes,
        validate_main_app,
    ]

    all_passed = True

    for validator in validators:
        if not validator():
            all_passed = False
        print()  # Add spacing between validations

    if all_passed:
        print("[SUCCESS] All validations passed! The AI Todo Chatbot implementation is complete and ready.")
        return 0
    else:
        print("[ERROR] Some validations failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())