from dipy_ai.agent import WorkflowAgent, UserMessage
from dipy_ai.agent.base_agent import ChatMessage
from dipy_ai.simulation import NIST_AMS_100_69_CorruptModeSimulator, SimulationRunner
from dipy_ai.api.nist_ams_mode_service import NIST_AMS_SumulationService
from dipy_ai.tools import generate_tool_bundles
from dipy_ai.config import (
    API_KEY, 
    BASE_URL, 
    MODEL_NAME,
    SYSTEM_PROMPT_FINAL_ANSWER,
    SYSTEM_PROMPT_TOOL_SELECTION,
    SIMULATION_DATA_FOLDER,
    ANOMALY_THRESHOLDS,
    CORRUPTION_MODE,
    SIMULATOR_SEED,
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

simulator = NIST_AMS_100_69_CorruptModeSimulator(
    data_folder=SIMULATION_DATA_FOLDER,
    corruption_mode=CORRUPTION_MODE,
    seed=SIMULATOR_SEED,
)
runner = SimulationRunner(simulator)
service = NIST_AMS_SumulationService(runner, simulator, seed=SIMULATOR_SEED)
tool_bundles = generate_tool_bundles(
    service,
    anomaly_thresholds=ANOMALY_THRESHOLDS,
)
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


history: list[ChatMessage] = []

try:
    service.start(CORRUPTION_MODE)
    while True:
        user_input = UserMessage(message=input("You: "))
        if user_input.message.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        response = agent.handle_message(user_input, history)
        history.extend([
            {"role": "user", "content": user_input.message},
            {"role": "assistant", "content": response},
        ])
        print(f"{agent}: {response}")
finally:
    service.close()
