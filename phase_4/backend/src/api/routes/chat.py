import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...agents.todo_orchestrator import TodoOrchestrator, ChatMessage
from ...db import get_session
from ...services.conversation_service import ConversationService

class ChatRequest(BaseModel):
    message: str
    conversation_id: int = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    task_operations: List[Dict[str, Any]]


from ...services.auth_service import get_current_user


router = APIRouter(tags=["Chat"])

# Route where user_id is in the path and must match JWT sub
@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat_with_user_id(
    user_id: str,
    chat_request: ChatRequest,
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # If user_id is present in the path, verify it matches the JWT 'sub' claim
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Path user_id does not match authenticated user"
        )

    # Use the authenticated user_id for all operations
    authenticated_user_id = current_user_id

    # Process AI chat message with proper DB session handling
    if not chat_request.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    orchestrator = TodoOrchestrator()
    conversation_service = ConversationService()

    try:
        # Load or create conversation
        current_conversation_id = chat_request.conversation_id
        conversation_history = []

        if current_conversation_id:
            conversation = await conversation_service.get_conversation_by_id(session, current_conversation_id, authenticated_user_id)
            if not conversation:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found or access denied")

            messages = await conversation_service.get_messages_for_conversation(session, current_conversation_id, authenticated_user_id)
            conversation_history = [ChatMessage(role=m.role, content=m.content) for m in messages]
        else:
            new_conversation = await conversation_service.create_conversation(session, authenticated_user_id)
            current_conversation_id = new_conversation.id

        # Process the AI message using the orchestrator
        result = await orchestrator.process_message(
            user_id=authenticated_user_id,
            message=chat_request.message,
            conversation_history=conversation_history
        )

        # Execute any pending task operations identified by the assistant
        for i, task_op in enumerate(result.task_operations):
            if task_op["status"] == "pending_execution":
                operation = task_op["operation"]
                arguments = task_op["arguments"]

                try:
                    # Import the appropriate tool function based on the operation
                    if operation == "add_task":
                        from ...agents.tools.add_task_tool import add_task
                        tool_result = await add_task(
                            user_id=arguments["user_id"],
                            title=arguments["title"],
                            description=arguments.get("description"),
                            priority=arguments.get("priority", "medium"),
                            session=session
                        )
                    elif operation == "list_tasks":
                        from ...agents.tools.list_tasks_tool import list_tasks
                        tool_result = await list_tasks(
                            user_id=arguments["user_id"],
                            status=arguments.get("status", "all"),
                            session=session
                        )
                    elif operation == "complete_task":
                        from ...agents.tools.complete_task_tool import complete_task
                        tool_result = await complete_task(
                            user_id=arguments["user_id"],
                            task_id=arguments["task_id"],
                            session=session
                        )
                    elif operation == "delete_task":
                        from ...agents.tools.delete_task_tool import delete_task
                        tool_result = await delete_task(
                            user_id=arguments["user_id"],
                            task_id=arguments["task_id"],
                            session=session
                        )
                    elif operation == "update_task":
                        from ...agents.tools.update_task_tool import update_task
                        tool_result = await update_task(
                            user_id=arguments["user_id"],
                            task_id=arguments["task_id"],
                            title=arguments.get("title"),
                            description=arguments.get("description"),
                            priority=arguments.get("priority"),
                            session=session
                        )

                    # Update the task operation with the execution result
                    result.task_operations[i]["status"] = "executed"
                    result.task_operations[i]["result"] = tool_result
                except Exception as e:
                    # Log the error and update the task operation status
                    print(f"Error executing {operation}: {str(e)}")
                    result.task_operations[i]["status"] = "failed"
                    result.task_operations[i]["error"] = str(e)

        # Save messages
        await conversation_service.add_message_to_conversation(session, current_conversation_id, authenticated_user_id, "user", chat_request.message)
        await conversation_service.add_message_to_conversation(session, current_conversation_id, authenticated_user_id, "assistant", result.response)

        # Return response
        result.conversation_id = current_conversation_id
        return ChatResponse(
            response=result.response,
            conversation_id=result.conversation_id,
            task_operations=result.task_operations
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Rollback on any other exception
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

# Alternative route where user_id is extracted from JWT only (user_id in path is OPTIONAL)
@router.post("/api/chat", response_model=ChatResponse)
async def chat_without_user_id(
    chat_request: ChatRequest,
    current_user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Use the authenticated user_id directly without path verification
    authenticated_user_id = current_user_id

    # Process AI chat message with proper DB session handling
    if not chat_request.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    orchestrator = TodoOrchestrator()
    conversation_service = ConversationService()

    try:
        # Load or create conversation
        current_conversation_id = chat_request.conversation_id
        conversation_history = []

        if current_conversation_id:
            conversation = await conversation_service.get_conversation_by_id(session, current_conversation_id, authenticated_user_id)
            if not conversation:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found or access denied")

            messages = await conversation_service.get_messages_for_conversation(session, current_conversation_id, authenticated_user_id)
            conversation_history = [ChatMessage(role=m.role, content=m.content) for m in messages]
        else:
            new_conversation = await conversation_service.create_conversation(session, authenticated_user_id)
            current_conversation_id = new_conversation.id

        # Process the AI message using the orchestrator
        result = await orchestrator.process_message(
            user_id=authenticated_user_id,
            message=chat_request.message,
            conversation_history=conversation_history
        )


        # Execute any pending task operations identified by the assistant
        for i, task_op in enumerate(result.task_operations):
            if task_op["status"] == "pending_execution":
                operation = task_op["operation"]
                arguments = task_op["arguments"]

                try:
                    # Import the appropriate tool function based on the operation
                    if operation == "add_task":
                        from ...agents.tools.add_task_tool import add_task
                        tool_result = await add_task(
                            user_id=arguments["user_id"],
                            title=arguments["title"],
                            description=arguments.get("description"),
                            priority=arguments.get("priority", "medium"),
                            session=session
                        )
                    elif operation == "list_tasks":
                        from ...agents.tools.list_tasks_tool import list_tasks
                        tool_result = await list_tasks(
                            user_id=arguments["user_id"],
                            status=arguments.get("status", "all"),
                            session=session
                        )
                    elif operation == "complete_task":
                        from ...agents.tools.complete_task_tool import complete_task
                        tool_result = await complete_task(
                            user_id=arguments["user_id"],
                            task_id=arguments["task_id"],
                            session=session
                        )
                    elif operation == "delete_task":
                        from ...agents.tools.delete_task_tool import delete_task
                        tool_result = await delete_task(
                            user_id=arguments["user_id"],
                            task_id=arguments["task_id"],
                            session=session
                        )
                    elif operation == "update_task":
                        from ...agents.tools.update_task_tool import update_task
                        tool_result = await update_task(
                            user_id=arguments["user_id"],
                            task_id=arguments["task_id"],
                            title=arguments.get("title"),
                            description=arguments.get("description"),
                            priority=arguments.get("priority"),
                            session=session
                        )

                    # Update the task operation with the execution result
                    result.task_operations[i]["status"] = "executed"
                    result.task_operations[i]["result"] = tool_result
                except Exception as e:
                    # Log the error and update the task operation status
                    print(f"Error executing {operation}: {str(e)}")
                    result.task_operations[i]["status"] = "failed"
                    result.task_operations[i]["error"] = str(e)

        # Save messages
        await conversation_service.add_message_to_conversation(session, current_conversation_id, authenticated_user_id, "user", chat_request.message)
        await conversation_service.add_message_to_conversation(session, current_conversation_id, authenticated_user_id, "assistant", result.response)

        # Return response
        result.conversation_id = current_conversation_id
        return ChatResponse(
            response=result.response,
            conversation_id=result.conversation_id,
            task_operations=result.task_operations
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Rollback on any other exception
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )