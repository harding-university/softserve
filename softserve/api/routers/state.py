from os import environ
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Path

from ..schema import *
from ..util import engine, get_actions


STATE_REGEX = environ.get("SOFTSERVE_STATE_REGEX")
if not STATE_REGEX:
    raise SoftserveException("No state regex defined!")


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
    after = stdout.strip()
    actions, _ = get_actions(after)
    return StateActResponse(state=after, actions=actions, log=stderr)


@router.get("/{state}/think", response_model=StateThinkResponse)
async def state_think(
    state: str = Path(pattern=STATE_REGEX),
    workers: Annotated[str | None, Header()] = None,
    iterations: Annotated[str | None, Header()] = None,
) -> StateThinkResponse:

    if workers:
        workers = min(int(workers), MAX_WORKERS)
        workers = max(workers, MIN_WORKERS)

    if iterations:
        iterations = min(int(iterations), MAX_ITERATIONS)
        iterations = max(iterations, MIN_ITERATIONS)

    action, stderr = engine(f"-t", state)
    after, _ = engine("-a", action, state)
    actions, _ = get_actions(after)
    return StateThinkResponse(action=action, state=after, actions=actions, log=stderr)


@router.get(
    "/{state}/winner",
    response_model=StateWinnerResponse,
    summary="Get the winner at a given state, if any",
    description="""
Returns one of the following, describing the winner of the current state:
- `none` (ongoing game)
- `x`
- `o`
- `draw`

If you believe the determination is incorrect, [open an
issue](https://github.com/harding-university/softserve/issues).
""",
)
async def state_winner(state: str = Path(pattern=STATE_REGEX)) -> StateWinnerResponse:
    stdout, stderr = engine("-W", state)
    return StateWinnerResponse(winner=stdout.strip(), log=stderr)
