"""Conversation service layer for business logic and orchestration.

This service layer coordinates between API routes and the repository layer,
providing business logic and input validation.
Constitution compliance: Coordinates MCP tools while maintaining user isolation.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.conversation import Conversation, Message, ConversationCreate, MessageCreate
from ..repositories.conversation_repository import ConversationRepository


class ConversationService:
    """Service for Conversation business operations"""

    def __init__(self) -> None:
        """Initialize conversation service with repository"""
        self.repository = ConversationRepository()

    async def create_conversation(self, session: AsyncSession, user_id: str) -> Conversation:
        """Create a new conversation for a user

        Args:
            session: Database session
            user_id: ID of user creating the conversation

        Returns:
            Conversation: Created conversation

        Constitution compliance:
        - Maintains user_id ownership
        - Uses repository for database operations
        """
        conversation = Conversation(
            user_id=user_id,
            metadata_json="{}"  # Use empty JSON object instead of None
        )
        return await self.repository.create_conversation(session, conversation)

    async def get_conversation_by_id(self, session: AsyncSession, conversation_id: int, user_id: str) -> Optional[Conversation]:
        """Get a specific conversation for a user

        Args:
            session: Database session
            conversation_id: ID of conversation to retrieve
            user_id: ID of user requesting the conversation

        Returns:
            Conversation if found and owned by user, None otherwise

        Constitution compliance:
        - Validates user_id ownership
        - Prevents cross-user access
        """
        return await self.repository.get_conversation_by_id(session, conversation_id, user_id)

    async def get_conversations_by_user(self, session: AsyncSession, user_id: str) -> List[Conversation]:
        """Get all conversations for a user

        Args:
            session: Database session
            user_id: ID of user requesting conversations

        Returns:
            List[Conversation]: List of conversations belonging to the user

        Constitution compliance:
        - Enforces multi-user data isolation
        """
        return await self.repository.get_conversations_by_user(session, user_id)

    async def add_message_to_conversation(self, session: AsyncSession, conversation_id: int, user_id: str, role: str, content: str) -> Optional[Message]:
        """Add a message to a conversation

        Args:
            session: Database session
            conversation_id: ID of conversation to add message to
            user_id: ID of user adding the message
            role: Role of the message sender (user/assistant/system)
            content: Content of the message

        Returns:
            Message if added successfully, None if conversation not found/owned by user

        Constitution compliance:
        - Validates user_id ownership of conversation
        - Maintains data isolation
        """
        # First verify that the conversation belongs to the user
        conversation = await self.repository.get_conversation_by_id(session, conversation_id, user_id)
        if not conversation:
            return None

        # Create and add the message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        return await self.repository.create_message(session, message)

    async def get_messages_for_conversation(self, session: AsyncSession, conversation_id: int, user_id: str) -> List[Message]:
        """Get all messages for a conversation

        Args:
            session: Database session
            conversation_id: ID of conversation to get messages for
            user_id: ID of user requesting messages

        Returns:
            List[Message]: List of messages in the conversation

        Constitution compliance:
        - Validates user_id ownership of conversation
        - Maintains data isolation
        """
        return await self.repository.get_messages_by_conversation(session, conversation_id, user_id)

    async def update_conversation_metadata(self, session: AsyncSession, conversation_id: int, user_id: str, metadata_json: str) -> Optional[Conversation]:
        """Update conversation metadata

        Args:
            session: Database session
            conversation_id: ID of conversation to update
            user_id: ID of user attempting update
            metadata_json: New metadata as JSON string

        Returns:
            Updated conversation if found and owned by user, None otherwise

        Constitution compliance:
        - Validates user_id ownership
        - Prevents cross-user updates
        """
        return await self.repository.update_conversation(session, conversation_id, user_id, metadata_json=metadata_json)

    async def delete_conversation(self, session: AsyncSession, conversation_id: int, user_id: str) -> bool:
        """Delete a conversation

        Args:
            session: Database session
            conversation_id: ID of conversation to delete
            user_id: ID of user attempting deletion

        Returns:
            bool: True if deleted, False if not found or access denied

        Constitution compliance:
        - Validates user_id ownership
        - Prevents cross-user deletions
        """
        return await self.repository.delete_conversation(session, conversation_id, user_id)