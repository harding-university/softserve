from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from ..util import engine, get_actions


STATE_REGEX = r"(\d?\d,\d?\d\|){0,32}(\d?\d,\d?\d[ht]\d?\d|){0,32}[ht]"
# TODO action regex


router = APIRouter()


class EngineResponse(BaseModel):
    log: str


class StateInitialResponse(EngineResponse):
    state: str


@router.get(
    "/state/initial",
    response_model=StateInitialResponse,
    tags=["state"],
    summary="Get initial state.",
)
async def state_initial() -> StateInitialResponse:
    stdout, stderr = engine("-I")
    return StateInitialResponse(state=stdout.strip(), log=stderr)


class StateActionsResponse(EngineResponse):
    actions: dict[str, str]


@router.get(
    "/state/{state}/actions",
    response_model=StateActionsResponse,
    tags=["state"],
    summary="Get actions available from the given state.",
)
async def state_actions(state: str = Path(pattern=STATE_REGEX)) -> StateActionsResponse:
    actions, stderr = get_actions(state)
    action_states = {
        action: engine("-a", action, state)[0].strip() for action in actions
    }
    return StateActionsResponse(actions=action_states, log=stderr)


class StateActResponse(EngineResponse):
    state: str


@router.get(
    "/state/{state}/act/{action}",
    tags=["state"],
    summary="Get resulting state after playing the given action at the given state.",
)
async def state_act(
    state: str = Path(pattern=STATE_REGEX), action: str = Path()
) -> StateActResponse:
    actions, stderr = get_actions(state)
    if action not in actions:
        raise HTTPException(status_code=422, detail="invalid action")

    stdout, stderr = engine("-a", action, state)
    return StateActResponse(state=stdout.strip(), log=stderr)
