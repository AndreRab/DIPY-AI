from dipy_ai.agent import WorkflowAgent, UserMessage
from dipy_ai.agent.one_step_llm_agent import OneStepLLMAgent
from dipy_ai.simulation import MockSimulator, SimulationRunner
from dipy_ai.tools import generate_tool_bundles_from_simulator
from dipy_ai.config import (
    API_KEY, 
    BASE_URL, 
    MODEL_NAME,
    SYSTEM_PROMPT_FINAL_ANSWER,
    SYSTEM_PROMPT_TOOL_SELECTION
)

simulator = MockSimulator()
tool_bundles = generate_tool_bundles_from_simulator(MockSimulator())
agent = WorkflowAgent(
    agent_name="Agent",
    api_key=API_KEY,
    base_url=BASE_URL,
    model_name=MODEL_NAME,
    system_prompt_final_answer=SYSTEM_PROMPT_FINAL_ANSWER,
    system_prompt_tool_selection=SYSTEM_PROMPT_TOOL_SELECTION,
    tool_bundles=tool_bundles
)


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

