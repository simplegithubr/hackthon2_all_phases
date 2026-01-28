import os
import asyncio

# Check if OpenRouter key is loaded
key = os.getenv("OPENROUTER_API_KEY")
print("OPENROUTER_API_KEY:", key if key else "Not found")

# Import your orchestrator
from src.agents.todo_orchestrator import TodoOrchestrator, ChatMessage  # path adjust karo agar alag ho

async def test_orchestrator():
    bot = TodoOrchestrator()
    response = await bot.process_message(
        user_id="test_user_1",
        message="Add a new task: Buy groceries",
        conversation_history=[]
    )
    print("\n--- AI Response ---")
    print(response.response)
    print("\n--- Task Operations ---")
    print(response.task_operations)

asyncio.run(test_orchestrator())
