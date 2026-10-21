from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dipy_ai.agent import WorkflowAgent
from dipy_ai.api.services.nist_ams_mode_service import NIST_AMS_SumulationService
from dipy_ai.api.routers.conversations import router as conversations_router
from dipy_ai.api.infrastructure.database import engine, init_db
from dipy_ai.api.routers.simulation import router as simulation_router
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    simulator = NIST_AMS_100_69_CorruptModeSimulator(
        data_folder=SIMULATION_DATA_FOLDER,
        corruption_mode=CORRUPTION_MODE,
        seed=SIMULATOR_SEED,
    )
    runner = SimulationRunner(simulator)
    service = NIST_AMS_SumulationService(runner, simulator, seed=SIMULATOR_SEED)
    try:
        tool_bundles = generate_tool_bundles(service, ANOMALY_THRESHOLDS)
        app.state.agent = WorkflowAgent(
            agent_name="Agent",
            api_key=API_KEY,
            base_url=BASE_URL,
            model_name=MODEL_NAME,
            system_prompt_final_answer=SYSTEM_PROMPT_FINAL_ANSWER,
            system_prompt_tool_selection=SYSTEM_PROMPT_TOOL_SELECTION,
            tool_bundles=tool_bundles,
            use_logger=False,
        )
        app.state.simulation_service = service
        yield
    finally:
        service.close()
        engine.dispose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_BACKEND_ORIGINS,
    allow_methods=ALLOWED_BACKEND_METHODS,
    allow_headers=ALLOWED_BACKEND_HEADERS,
)
app.include_router(conversations_router)

app.include_router(simulation_router)
