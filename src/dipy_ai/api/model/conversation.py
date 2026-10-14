from typing import List

from sqlalchemy.orm import Mapped, relationship
from dipy_ai.api.db.base import Base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime

from dipy_ai.api.model.message import Message

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    messages : Mapped[List[Message]] = relationship("Message", back_populates="conversation")