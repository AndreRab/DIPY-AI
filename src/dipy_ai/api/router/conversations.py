from fastapi import APIRouter

from dipy_ai.api.db.core import get_db
from dipy_ai.api.model.conversation import Conversation

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


router.get("/")
async def get_conversations():
    with get_db() as db:
        return await db.query(Conversation).all()