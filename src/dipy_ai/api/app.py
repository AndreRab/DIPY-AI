from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dipy_ai.agent import WorkflowAgent, UserMessage
from dipy_ai.simulation import SimulationRunner
from dipy_ai.simulation.nist_ams_100_69_simulator import NIST_AMS_100_69_Simulator
from dipy_ai.tools import generate_tool_bundles_from_simulator
from dipy_ai.config import (
    API_KEY, BASE_URL, MODEL_NAME, DATA_FOLDER,
    SYSTEM_PROMPT_FINAL_ANSWER, SYSTEM_PROMPT_TOOL_SELECTION,
)

simulator = NIST_AMS_100_69_Simulator(data_folder=DATA_FOLDER)
tool_bundles = generate_tool_bundles_from_simulator(simulator)
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
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvokeRequest(BaseModel):
    prompt: str


@app.post("/invoke")
async def invoke(request: InvokeRequest):
    response = await run_in_threadpool(
        agent.handle_message, UserMessage(message=request.prompt)
    )
    return {"response": response}