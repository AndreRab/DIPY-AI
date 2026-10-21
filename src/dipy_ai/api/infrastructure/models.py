from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum as PythonEnum

from typing import List

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.types import TypeDecorator

from dipy_ai.api.infrastructure.database import Base



class Role(str, PythonEnum):
    USER = "user"
    ASSISTANT = "assistant"


class UTCDateTime(TypeDecorator):
    """Store naive UTC in SQLite and return aware UTC timestamps."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Timestamps must include a timezone")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # Legacy naive timestamps cannot reveal their original timezone.
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class Conversation(Base):
    __tablename__ = "conversations"

    id  : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title : Mapped[str] = mapped_column(String, nullable=False)
    created_at  : Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))
    updated_at : Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))
    messages: Mapped[List[Message]] = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id : Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), index=True, nullable=False)
    content : Mapped[str] = mapped_column(String, nullable=False)
    role : Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.USER)
    created_at : Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
