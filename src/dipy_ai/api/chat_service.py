
from typing import List
from fastapi import Depends

from dipy_ai.api.app import agent
from dipy_ai.agent.base_agent import UserMessage
from dipy_ai.api.conversation import ConversationResponse, InvokeResponse, MessageResponse
from dipy_ai.api.database import get_db
from dipy_ai.api.enum.role import Role
from dipy_ai.api.models import Conversation, Message


async def list_conversations(db = Depends(get_db)):
    list = db.select(Conversation).all().order_by(Conversation.updated_at.desc(),Conversation.id.desc()).all()
    response : List[ConversationResponse] = []
    for conversation in list:
        response.append(
            ConversationResponse(
                conversation_id = str(conversation.id),
                title = conversation.title,
                created_at = str(conversation.created_at),
                updated_at = str(conversation.updated_at)
            )
        )    

    return response
async def get_messages(conversation_id : int,db = Depends(get_db)):
    if conversation_id is None or conversation_id < 1:
        return None
    data = db.select(Conversation).where(Conversation.id == conversation_id).order_by(Conversation.id.desc()).all()
    response : List[MessageResponse] = []
    for conversation in data:
        for message in conversation.messages:
            response.append(
                MessageResponse(
                    id = str(message.id),
                    conversation_id = str(message.conversation_id),
                    role = message.role.name,
                    content = message.content,
                    created_at = str(message.created_at)
                )
            )
    return response

async def invoke(prompt : str, conversation_id : int | None = None, db = Depends(get_db)):
    
    if conversation_id is None or conversation_id < 1:
        new_conversation = Conversation(title=prompt[:20])
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        conversation_id = new_conversation.id
    else:
        Conversation = db.get(Conversation, conversation_id)
        if not Conversation:
            new_conversation = Conversation(title=prompt[:20])
            db.add(new_conversation)
            db.commit()
            db.refresh(new_conversation)
            conversation_id = new_conversation.id

    db.add(
        Message(
            content=prompt.strip(),
            role=Role.USER,
            conversation_id=conversation_id,
        )
    )
    db.commit() 
    
    response = agent.handle_message(UserMessage(message=prompt))
    
    db.add(
        Message(
            content=response,
            role=Role.ASSISTANT,
            conversation_id=conversation_id,
        )
    )
    db.commit()
    
    return InvokeResponse(
        response=response,
        conversation_id=str(conversation_id)    
    )
    