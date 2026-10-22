from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, PositiveInt, StringConstraints
from sqlalchemy.orm import Session

from dipy_ai.api.infrastructure.database import get_db
from dipy_ai.api.services.chat_service import ChatService, ConversationBusy, ConversationNotFound, GenerationFailed, GenerationTimeout
from dipy_ai.api.infrastructure.models import Role

router = APIRouter(
    tags=["conversation"],
)

class InvokeRequest(BaseModel):
    prompt : Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    conversation_id : PositiveInt | None = None
    
class InvokeResponse(BaseModel):
    response : str
    conversation_id : int

class ConversationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id : int
    title : str 
    created_at : datetime
    updated_at : datetime

class MessageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id : int
    conversation_id : int
    role : Role
    content : str
    created_at : datetime
    

def get_chat_service(request: Request, db: Session = Depends(get_db)):
    return ChatService(db=db, agent=request.app.state.agent)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(chat_service : ChatService = Depends(get_chat_service)):
    return chat_service.list_conversations()

@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(conversation_id : PositiveInt, chat_service : ChatService = Depends(get_chat_service)):
    try:
        return chat_service.get_messages(conversation_id)
    except ConversationNotFound as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc

@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: PositiveInt, chat_service: ChatService = Depends(get_chat_service)):
    try:
        chat_service.delete_conversation(conversation_id)
    except ConversationNotFound as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    except ConversationBusy as exc:
        raise HTTPException(status_code=409, detail="Conversation is busy") from exc
    return Response(status_code=204)


@router.post("/invoke", response_model=InvokeResponse)
def invoke(request : InvokeRequest, chat_service : ChatService = Depends(get_chat_service)):
    try:
        return chat_service.invoke(request.prompt, request.conversation_id)
    except ConversationBusy as exc:
        raise HTTPException(status_code=409, detail="Conversation is busy") from exc
    except ConversationNotFound as exc:
        raise HTTPException(status_code=404, detail="Conversation not found") from exc
    except GenerationTimeout as exc:
        raise HTTPException(status_code=504, detail="Response generation timed out") from exc
    except GenerationFailed as exc:
        raise HTTPException(status_code=502, detail="Response generation failed") from exc
