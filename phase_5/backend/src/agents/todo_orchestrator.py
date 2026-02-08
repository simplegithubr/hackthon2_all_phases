

"""
Main orchestrator agent for the AI Todo Chatbot using OpenRouter API.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional

from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# -------------------------
# Models
# -------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    task_operations: List[Dict[str, Any]]


# -------------------------
# Orchestrator
# -------------------------

class TodoOrchestrator:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        print(f"DEBUG: OPENROUTER_API_KEY loaded: {'SET' if api_key else 'NOT SET'}")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing in .env")

        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3.3-70b-instruct:free"
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Todo AI Chatbot"
                }
            )
        return self._client

    # -------------------------
    # Main Logic
    # -------------------------

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:

        try:
            messages = []

            # System prompt
            messages.append({
                "role": "system",
                "content": f"""
You are a friendly and helpful Todo AI assistant for the user with email/ID: {user_id}

Follow these strict rules:

1. ONLY use tools when the user is clearly asking to manage a task:
   - Words like "add", "create", "remember", "new task" → use add_task
   - "list", "show", "my tasks", "pending", "completed" → use list_tasks
   - "done", "complete", "finished", "mark as done" → use complete_task
   - "delete", "remove", "cancel" → use delete_task
   - "change", "update", "edit", "rename" → use update_task

2. If the user just says "hi", "hello", "hey", "good morning", "good evening", "how are you", or any casual/normal chat →
   respond normally in a friendly way. DO NOT respond in JSON format.

3. If the user asks about their login, email, or who they are →
   reply: "You are logged in as {user_id}."

4. If user clearly asks for a task operation, respond ONLY in JSON format:
   {{"operation": "<name>", "arguments": {{...}}}}

Available operations:
- add_task
- list_tasks
- complete_task
- delete_task
- update_task
"""
            })

            if conversation_history:
                for m in conversation_history:
                    messages.append({"role": m.role, "content": m.content})

            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=800
            )

            ai_text = response.choices[0].message.content.strip()
            task_operations = []

            # -------------------------
            # SAFE JSON PARSING
            # -------------------------

            parsed = None

            try:
                parsed = json.loads(ai_text)
            except:
                try:
                    parsed = json.loads(json.loads(ai_text))
                except:
                    parsed = None

            if isinstance(parsed, dict) and "operation" in parsed:
                operation = parsed["operation"]
                arguments = parsed.get("arguments", {})
                arguments["user_id"] = user_id

                task_operations.append({
                    "operation": operation,
                    "status": "pending_execution",
                    "arguments": arguments
                })

                ai_response = f"Processing: {operation.replace('_', ' ')}"
            else:
                ai_response = ai_text

            return ChatResponse(
                response=ai_response,
                conversation_id=0,
                task_operations=task_operations
            )

        except Exception as e:
            logging.error(f"AI error: {e}")
            return ChatResponse(
                response="AI service error",
                conversation_id=0,
                task_operations=[{
                    "operation": "error",
                    "status": "failed",
                    "error": str(e)
                }]
            )


# -------------------------
# Local Test
# -------------------------

if __name__ == "__main__":
    async def test():
        bot = TodoOrchestrator()
        res = await bot.process_message(
            user_id="test",
            message="list my tasks",
            conversation_history=[]
        )
        print(res)

    asyncio.run(test())
