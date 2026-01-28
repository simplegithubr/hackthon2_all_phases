#!/usr/bin/env python3
"""
Test script to verify the greeting fix in the TodoOrchestrator
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.todo_orchestrator import TodoOrchestrator

async def test_greeting_responses():
    """
    Test that greeting messages return proper responses without task operations
    """
    # Mock user ID for testing
    user_id = "test_user_123"

    orchestrator = TodoOrchestrator()

    # Test cases for different greetings
    greeting_messages = [
        "hi",
        "hello",
        "hey",
        "Hi there!",
        "Hello, how are you?",
        "Good morning"
    ]

    print("Testing greeting responses...\n")

    for msg in greeting_messages:
        print(f"Input: '{msg}'")

        try:
            result = await orchestrator.process_message(
                user_id=user_id,
                message=msg,
                conversation_history=[]
            )

            print(f"Response: {result.response}")
            print(f"Task operations: {result.task_operations}")
            print(f"Has operations: {len(result.task_operations) > 0}")
            print("-" * 50)

        except Exception as e:
            print(f"Error processing '{msg}': {e}")
            print("-" * 50)

    # Also test a legitimate task command to make sure it still works
    print("\nTesting legitimate task command...")
    task_msg = "add a new task to buy groceries"

    try:
        result = await orchestrator.process_message(
            user_id=user_id,
            message=task_msg,
            conversation_history=[]
        )

        print(f"Input: '{task_msg}'")
        print(f"Response: {result.response}")
        print(f"Task operations: {result.task_operations}")
        print(f"Has operations: {len(result.task_operations) > 0}")
        print("-" * 50)

    except Exception as e:
        print(f"Error processing task command: {e}")

if __name__ == "__main__":
    # Set environment variable if not already set (for testing purposes)
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY not set. This test will fail without a valid API key.")
        print("Please set OPENROUTER_API_KEY in your environment to run this test.")
        exit(1)

    asyncio.run(test_greeting_responses())