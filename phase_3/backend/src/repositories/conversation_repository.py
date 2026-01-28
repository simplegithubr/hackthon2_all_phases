"""Conversation repository for database access with multi-user isolation.

All queries enforce user_id filtering at repository layer
to prevent cross-user data access.
Constitution compliance: Enforces multi-user data isolation.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.conversation import Conversation, Message


class ConversationRepository:
    """Repository for Conversation database operations with user_id isolation"""

    async def create_conversation(self, session: AsyncSession, conversation: Conversation) -> Conversation:
        """Create a new conversation in database

        Args:
            session: Database session
            conversation: Conversation object to create

        Returns:
            Conversation: Created conversation with id populated

        Constitution compliance:
        - Maintains multi-user data isolation
        """
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

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
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_conversations_by_user(self, session: AsyncSession, user_id: str) -> List[Conversation]:
        """Get all conversations belonging to a specific user

        Args:
            session: Database session
            user_id: ID of user to fetch conversations for

        Returns:
            List[Conversation]: List of conversations belonging to the user,
                              sorted by creation date (newest first)

        Constitution compliance:
        - Enforces multi-user data isolation
        - Filters ALL results by user_id
        """
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_conversation(self, session: AsyncSession, conversation_id: int, user_id: str, **updates) -> Optional[Conversation]:
        """Update an existing conversation

        Args:
            session: Database session
            conversation_id: ID of conversation to update
            user_id: ID of user attempting update
            **updates: Fields to update

        Returns:
            Updated conversation if found and owned by user, None otherwise

        Constitution compliance:
        - Validates user_id ownership
        - Prevents cross-user updates
        """
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        existing_conversation = result.scalar_one_or_none()

        if not existing_conversation:
            return None

        # Update provided fields
        for field, value in updates.items():
            if hasattr(existing_conversation, field):
                setattr(existing_conversation, field, value)

        existing_conversation.updated_at = existing_conversation.__class__.updated_at.default.arg()

        await session.commit()
        await session.refresh(existing_conversation)
        return existing_conversation

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
        result = await session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            return False

        await session.delete(conversation)
        await session.commit()
        return True

    # Message-related methods
    async def create_message(self, session: AsyncSession, message: Message) -> Message:
        """Create a new message in database

        Args:
            session: Database session
            message: Message object to create

        Returns:
            Message: Created message with id populated

        Constitution compliance:
        - Maintains multi-user data isolation through conversation relationship
        """
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    async def get_messages_by_conversation(self, session: AsyncSession, conversation_id: int, user_id: str) -> List[Message]:
        """Get all messages for a conversation belonging to a user

        Args:
            session: Database session
            conversation_id: ID of conversation to fetch messages for
            user_id: ID of user requesting messages

        Returns:
            List[Message]: List of messages in the conversation

        Constitution compliance:
        - Enforces multi-user data isolation
        - Validates user owns the conversation
        """
        result = await session.execute(
            select(Message)
            .join(Conversation)
            .where(Message.conversation_id == conversation_id)
            .where(Conversation.user_id == user_id)
            .order_by(Message.timestamp.asc())
        )
        return list(result.scalars().all())