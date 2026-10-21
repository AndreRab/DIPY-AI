from dipy_ai.agent import BaseAgent, UserMessage
from dipy_ai.agent.base_agent import ChatMessage
from openai import OpenAI

class OneStepLLMAgent(BaseAgent):
    def __init__(self, 
                api_key: str,
                base_url: str,
                model_name: str,
                system_prompt: str,
                agent_name: str = 'OneStepLLMAgent'
        ):
        super().__init__(agent_name)
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._system_prompt = system_prompt
        self._model_name = model_name

    def handle_message(self, message: UserMessage, history: list[ChatMessage]) -> str:
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": self._system_prompt},
                *(dict(item) for item in history),
                {"role": "user", "content": message.message}
            ]
        )
        return response.choices[0].message.content
