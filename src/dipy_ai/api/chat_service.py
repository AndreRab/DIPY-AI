
from datetime import datetime
from openai import APITimeoutError
from sqlalchemy.orm import Session

from dipy_ai.agent.workflow_agent import WorkflowAgent
from dipy_ai.agent.base_agent import UserMessage
from dipy_ai.api.enum.role import Role
from dipy_ai.api.models import Conversation, Message

class ConversationNotFound(Exception):
    pass


class GenerationFailed(Exception):
    pass


class GenerationTimeout(GenerationFailed):
    pass

class ChatService:
    def __init__(self, db : Session,agent : WorkflowAgent):
        self.db = db
        self.agent = agent
    def list_conversations(self):
        return self.db.query(Conversation).order_by(Conversation.updated_at.desc(),Conversation.id.desc()).all()

    def get_messages(self, conversation_id : int):
        if self.db.get(Conversation, conversation_id) is None:
            raise ConversationNotFound()
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.id.asc()).all()

    def invoke(self, prompt : str, conversation_id : int | None = None):
        history = []
        if conversation_id is not None:
            history = [
                {"role": message.role.value, "content": message.content}
                for message in self.get_messages(conversation_id)
            ]
        # Finish reading before waiting for the model; history now contains plain values.
        self.db.rollback()

        try:
            response = self.agent.handle_message(UserMessage(message=prompt), history)
            if not isinstance(response, str) or not response.strip():
                raise ValueError("The model returned an empty response")
        except (APITimeoutError, TimeoutError) as exc:
            raise GenerationTimeout() from exc
        except Exception as exc:
            raise GenerationFailed() from exc

        try:
            if conversation_id is None:
                conversation = Conversation(title=prompt[:20])
                self.db.add(conversation)
                self.db.flush()
                conversation_id = conversation.id
            else:
                conversation = self.db.get(Conversation, conversation_id)
                if conversation is None:
                    raise ConversationNotFound()

            conversation.updated_at = datetime.now()
            self.db.add_all([
                Message(
                    content=prompt,
                    role=Role.USER,
                    conversation_id=conversation_id,
                ),
                Message(
                    content=response,
                    role=Role.ASSISTANT,
                    conversation_id=conversation_id,
                ),
            ])
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"response": response, "conversation_id": conversation_id}
