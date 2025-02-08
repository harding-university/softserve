from fastapi import APIRouter, HTTPException, Path

from ..schema import *
from ..util import engine, get_actions


STATE_REGEX = r"(\d?\d,\d?\d\|){0,32}(\d?\d,\d?\d[ht]\d?\d|){0,32}[ht]"
# TODO action regex


router = APIRouter(prefix="/state", tags=["state"])


@router.get(
    "/initial",
    response_model=StateInitialResponse,
    summary="Get the initial state",
    description="""
Returns a serialized representation of the initial game state.
""",
)
async def state_initial() -> StateInitialResponse:
    stdout, stderr = engine("-I")
    return StateInitialResponse(state=stdout.strip(), log=stderr)


@router.get(
    "/{state}/actions",
    response_model=StateActionsResponse,
    summary="Get the actions available from the given state",
    description="""
Returns a list of all actions available from a given state.

If you believe this list is incorrect, [open an
issue](https://github.com/harding-university/softserve/issues).
""",
)
async def state_actions(state: str = Path(pattern=STATE_REGEX)) -> StateActionsResponse:
    actions, stderr = get_actions(state)
    return StateActionsResponse(actions=actions, log=stderr)


@router.get(
    "/{state}/act/{action}",
    summary="Get the resulting state after playing the given action at the given state",
    description="""
Plays the action on the given state, and returns the resulting state.
This endpoint is purely about describing state transitions, and is
unrelated to actual games. Use it without worry.

Actions will be validated against the state. If you believe an action is
being improperly validated, [open an
issue](https://github.com/harding-university/softserve/issues).
""",
)
async def state_act(
    state: str = Path(pattern=STATE_REGEX), action: str = Path()
) -> StateActResponse:
    actions, stderr = get_actions(state)
    if action not in actions:
        raise HTTPException(status_code=422, detail="invalid action")

    stdout, stderr = engine("-a", action, state)
    return StateActResponse(state=stdout.strip(), log=stderr)
