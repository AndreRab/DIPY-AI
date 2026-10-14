from sqlalchemy.orm import Mapped, relationship
from dipy_ai.api.db.base import Base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime

from dipy_ai.api.model.conversation import Conversation       

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    conversation : Mapped[Conversation] = relationship("Conversation", back_populates="messages")