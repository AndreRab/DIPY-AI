from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dipy_ai.api.db.core import get_db
from dipy_ai.api.model.conversation import Conversation
from dipy_ai.api.model.message import Message
from dipy_ai.api.schemas.conversation import ConversationCreate, MessageCreate

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


@router.get("/")
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).all()


@router.post("/")
def create_conversation(
    conversation_create: ConversationCreate,
    db: Session = Depends(get_db),
):
    conversation = Conversation(title=conversation_create.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}/messages")
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .all()
    )


@router.post("/{conversation_id}/messages")
def create_message(
    conversation_id: int,
    message_create: MessageCreate,
    db: Session = Depends(get_db),
):
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    message = Message(
        content=message_create.content,
        role=message_create.role,
        conversation=conversation,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
