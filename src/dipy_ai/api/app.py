from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dipy_ai.agent import  WorkflowAgent
from dipy_ai.api.nist_ams_mode_service import NIST_AMS_SumulationService
from dipy_ai.api.router.conversations import router as conversations_router
from dipy_ai.config import (
    ALLOWED_BACKEND_HEADERS,
    ALLOWED_BACKEND_METHODS,
    ALLOWED_BACKEND_ORIGINS,
    ANOMALY_THRESHOLDS,
    API_KEY,
    BASE_URL,
    CORRUPTION_MODE,
    MODEL_NAME,
    SIMULATION_DATA_FOLDER,
    SIMULATOR_SEED,
    SYSTEM_PROMPT_FINAL_ANSWER,
    SYSTEM_PROMPT_TOOL_SELECTION,
)
from dipy_ai.simulation import NIST_AMS_100_69_CorruptModeSimulator, SimulationRunner
from dipy_ai.tools import generate_tool_bundles

simulator = NIST_AMS_100_69_CorruptModeSimulator(
    data_folder=SIMULATION_DATA_FOLDER,
    corruption_mode=CORRUPTION_MODE,
    seed=SIMULATOR_SEED,
)
runner = SimulationRunner(simulator)
nist_ams_service = NIST_AMS_SumulationService(runner, simulator, seed=SIMULATOR_SEED)
tool_bundles = generate_tool_bundles(nist_ams_service, ANOMALY_THRESHOLDS)

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
    try:
        yield
    finally:
        nist_ams_service.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_BACKEND_ORIGINS,
    allow_methods=ALLOWED_BACKEND_METHODS,
    allow_headers=ALLOWED_BACKEND_HEADERS,
)
app.include_router(conversations_router)


class InvokeRequest(BaseModel):
    prompt: str
    conversation_id: int | None = None


# @app.post("/invoke")
# def invoke(request: InvokeRequest, db: Session = Depends(get_db)):
#     if request.conversation_id is not None:
#         conversation = db.get(Conversation, request.conversation_id)
#         if not conversation:
#             raise HTTPException(status_code=404, detail="Conversation not found")
#     else:
#         conversation = Conversation(title="New Conversation")
#         db.add(conversation)
#         db.commit()
#         db.refresh(conversation)

#     db.add(
#         Message(
#             content=request.prompt,
#             role=Role.USER,
#             conversation=conversation,
#         )
#     )
#     db.commit()

#     response = agent.handle_message(UserMessage(message=request.prompt))

#     db.add(
#         Message(
#             content=response,
#             role=Role.ASSISTANT,
#             conversation=conversation,
#         )
#     )
#     db.commit()

#     return {"response": response}


@app.get("/simulation/modes")
def simulation_modes():
    return nist_ams_service.available_modes()


@app.get("/simulation")
def simulation_state():
    return nist_ams_service.snapshot()


class IntervalRequest(BaseModel):
    interval_ms: int = Field(default=1000, ge=50, le=2000, strict=True)


class StartRequest(IntervalRequest):
    mode: str


@app.post("/simulation/start")
def simulation_start(request: StartRequest):
    try:
        return nist_ams_service.start(request.mode, request.interval_ms)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/simulation/stop")
def simulation_stop():
    return nist_ams_service.stop()


@app.post("/simulation/resume")
def simulation_resume(request: IntervalRequest | None = None):
    try:
        return nist_ams_service.resume(request.interval_ms if request else None)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
