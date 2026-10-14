from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from dipy_ai.api.db.base import Base
from dipy_ai.api.enum.role import Role

if TYPE_CHECKING:
    from dipy_ai.api.model.conversation import Conversation


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True, nullable=False)
    content = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
