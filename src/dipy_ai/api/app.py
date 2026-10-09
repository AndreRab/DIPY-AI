from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dipy_ai.agent import WorkflowAgent, UserMessage
from dipy_ai.simulation import SimulationRunner, create_simulator
from dipy_ai.tools import generate_tool_bundles_from_simulator
from dipy_ai.config import (
    ALLOWED_BACKEND_HEADERS,
    API_KEY, 
    BASE_URL,
    MODEL_NAME, 
    ANOMALY_THRESHOLDS,
    ALLOWED_BACKEND_ORIGINS,
    ALLOWED_BACKEND_METHODS,
    ALLOWED_BACKEND_HEADERS,
    SIMULATION_DATA_FOLDER,
    SYSTEM_PROMPT_FINAL_ANSWER,
    SYSTEM_PROMPT_TOOL_SELECTION,
    SIMULATOR_SEED,
    SIMULATOR,
    CORRUPTION_MODE,
)

simulator = create_simulator(
    SIMULATOR,
    data_folder=SIMULATION_DATA_FOLDER,
    seed=SIMULATOR_SEED,
    corruption_mode=CORRUPTION_MODE,
)
tool_bundles = generate_tool_bundles_from_simulator(simulator,ANOMALY_THRESHOLDS)
agent = WorkflowAgent(
    agent_name="Agent",
    api_key=API_KEY,
    base_url=BASE_URL,
    model_name=MODEL_NAME,
    system_prompt_final_answer=SYSTEM_PROMPT_FINAL_ANSWER,
    system_prompt_tool_selection=SYSTEM_PROMPT_TOOL_SELECTION,
    tool_bundles=tool_bundles,
    use_logger=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    runner = SimulationRunner(simulator=simulator)
    runner.start()
    yield
    runner.stop()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_BACKEND_ORIGINS,
    allow_methods=ALLOWED_BACKEND_METHODS,
    allow_headers=ALLOWED_BACKEND_HEADERS,
)


class InvokeRequest(BaseModel):
    prompt: str


@app.post("/invoke")
def invoke(request: InvokeRequest):
    response = agent.handle_message(UserMessage(message=request.prompt))
    return {"response": response}