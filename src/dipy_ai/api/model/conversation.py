from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, relationship

from dipy_ai.api.db.base import Base

if TYPE_CHECKING:
    from dipy_ai.api.model.message import Message


class Conversation(Base):
    __tablename__ = "conversations"

    id  : Mapped[int] = Column(Integer, primary_key=True, index=True)
    title : Mapped[str] = Column(String, nullable=False)
    created_at  : Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = Column(DateTime, default=datetime.now)
    messages: Mapped[List[Message]] = relationship("Message", back_populates="conversation")
