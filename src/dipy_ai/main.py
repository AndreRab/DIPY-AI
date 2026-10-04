from dipy_ai.agent import WorkflowAgent, UserMessage
from dipy_ai.simulation import NIST_AMS_100_69_Simulator, SimulationRunner
from dipy_ai.tools import generate_tool_bundles_from_simulator
from dipy_ai.config import (
    API_KEY, 
    BASE_URL, 
    MODEL_NAME,
    SYSTEM_PROMPT_FINAL_ANSWER,
    SYSTEM_PROMPT_TOOL_SELECTION,
    SIMULATION_DATA_FOLDER
)
import logging

workflow_logger = logging.getLogger("dipy_ai.workflow")
workflow_logger.setLevel(logging.INFO)
workflow_logger.propagate = False
workflow_log_handler = logging.StreamHandler()
workflow_log_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
)
workflow_logger.addHandler(workflow_log_handler)

simulator = NIST_AMS_100_69_Simulator(
    data_folder=SIMULATION_DATA_FOLDER,
)
tool_bundles = generate_tool_bundles_from_simulator(simulator)
agent = WorkflowAgent(
    agent_name="Agent",
    api_key=API_KEY,
    base_url=BASE_URL,
    model_name=MODEL_NAME,
    system_prompt_final_answer=SYSTEM_PROMPT_FINAL_ANSWER,
    system_prompt_tool_selection=SYSTEM_PROMPT_TOOL_SELECTION,
    tool_bundles=tool_bundles,
    logger=workflow_logger,
    use_logger=True,
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

