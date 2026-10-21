from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from dipy_ai.api.services.nist_ams_mode_service import NIST_AMS_SumulationService

router = APIRouter(prefix="/simulation", tags=["simulation"])


class IntervalRequest(BaseModel):
    interval_ms: int = Field(default=1000, ge=50, le=2000, strict=True)


class StartRequest(IntervalRequest):
    mode: str


def get_simulation_service(request: Request) -> NIST_AMS_SumulationService:
    return request.app.state.simulation_service


SimulationService = Annotated[NIST_AMS_SumulationService, Depends(get_simulation_service)]


@router.get("/modes")
def simulation_modes(service: SimulationService):
    return service.available_modes()


@router.get("")
def simulation_state(service: SimulationService):
    return service.snapshot()


@router.post("/start")
def simulation_start(request: StartRequest, service: SimulationService):
    try:
        return service.start(request.mode, request.interval_ms)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (OSError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/stop")
def simulation_stop(service: SimulationService):
    return service.stop()


@router.post("/resume")
def simulation_resume(service: SimulationService, request: IntervalRequest | None = None):
    try:
        return service.resume(request.interval_ms if request else None)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
