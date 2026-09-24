from dipy_ai.agent import OneStepLLMAgent, UserMessage
from dipy_ai.simulation import MockSimulator, SimulationRunner
from dipy_ai.config import (
    API_KEY, 
    BASE_URL, 
    MODEL_NAME,
    SYSTEM_PROMPT
)

agent = OneStepLLMAgent(
    agent_name="Mock agent",
    api_key=API_KEY,
    base_url=BASE_URL,
    model_name=MODEL_NAME,
    system_prompt=SYSTEM_PROMPT
)

simulator = MockSimulator()

runner = SimulationRunner(simulator=simulator)
runner.start()

while True:
    user_input = UserMessage(
        message=input("You: ")
    )
    if user_input.message.lower() in ["exit", "quit"]:
        print("Exiting the chat. Goodbye!")
        runner.stop()
        break
    response = agent.handle_message(user_input)
    print(f"{agent}: {response}")

