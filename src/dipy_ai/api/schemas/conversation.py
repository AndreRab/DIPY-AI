from datetime import datetime

from pydantic import BaseModel

from dipy_ai.api.enum.role import Role


class ConversationCreate(BaseModel):
    title: str


class Conversation(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Message(BaseModel):
    id: int
    content: str
    role: Role
    created_at: datetime
    updated_at: datetime
    conversation_id: int

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str
    role: Role
