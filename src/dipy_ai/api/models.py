from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, relationship ,mapped_column

from dipy_ai.api.database import Base
from dipy_ai.api.enum.role import Role

if TYPE_CHECKING:
    from dipy_ai.api.model.message import Message
    from dipy_ai.api.model.conversation import Conversation


class Conversation(Base):
    __tablename__ = "conversations"

    id  : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title : Mapped[str] = mapped_column(String, nullable=False)
    created_at  : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    messages: Mapped[List[Message]] = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id : Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), index=True, nullable=False)
    content : Mapped[str] = mapped_column(String, nullable=False)
    role : Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
