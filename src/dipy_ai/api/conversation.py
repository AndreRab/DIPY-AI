from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/conversation",
    tags=["conversation"],
)

class InvokeRequesr(BaseModel):
    prompt : str
    conversation_id : str | None = None
    
class InvokeResponse(BaseModel):
    response : str
    conversation_id : str

class ConversationResponse(BaseModel):
    conversation_id : str
    title : str 
    created_at : str
    updated_at : str

class MessageResponse(BaseModel):
    id : str
    conversation_id : str
    role : str
    content : str
    created_at : str
    

@router.get("/list", response_model=list[ConversationResponse])
async def list_conversations():
    return await list_conversations()

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(conversation_id : int):
    return await get_messages(conversation_id)

@router.post("/invoke", response_model=InvokeResponse)
async def invoke(request : InvokeRequesr):
    response = await invoke(request.prompt, request.conversation_id)
    return InvokeResponse(response=response, conversation_id=str(response.conversation_id))
