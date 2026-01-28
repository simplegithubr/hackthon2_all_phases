"""Conversation and Message SQLModel definitions for chat history.
Constitution compliance: All data operations will go through MCP tools exclusively.
Maintains multi-user data isolation through user_id foreign key.
"""
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from .user import User


class MessageBase(SQLModel):
    """Base Message model with shared fields"""
    role: str = Field(max_length=20, description="Role of the message sender (user/assistant/system)")
    content: str = Field(description="Content of the message")
    metadata_json: Optional[str] = Field(default=None, description="Additional metadata as JSON string")


class MessageCreate(MessageBase):
    """Request model for creating a message"""
    pass


class Message(MessageBase, table=True):
    """Database table model for Message"""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, description="ID of conversation this message belongs to")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when message was created")

    # Relationship back to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __tablename__ = "messages"


class ConversationBase(SQLModel):
    """Base Conversation model with shared fields"""
    metadata_json: Optional[str] = Field(default=None, description="Additional metadata as JSON string")


class ConversationCreate(ConversationBase):
    """Request model for creating a conversation"""
    pass


class Conversation(ConversationBase, table=True):
    """Database table model for Conversation"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, description="ID of user who owns this conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when conversation was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when conversation was last updated")

    # Relationships
    messages: List[Message] = Relationship(back_populates="conversation", cascade_delete=True)
    user: Optional[User] = Relationship()

    __tablename__ = "conversations"


class ConversationRead(ConversationBase):
    """Response model for reading a conversation"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class MessageRead(MessageBase):
    """Response model for reading a message"""
    id: int
    conversation_id: int
    timestamp: datetime