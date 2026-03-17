from os import environ

from fastapi import APIRouter, HTTPException, Path

from ..schema import *
from ..util import engine, get_actions, get_initial_state, SoftserveException

THINK_TOKEN = environ.get("SOFTSERVE_THINK_TOKEN")

# TODO
MIN_WORKERS = 1
MAX_WORKERS = 4
MIN_ITERATIONS = 1000
MAX_ITERATIONS = 500000

STATE_REGEX = environ.get("SOFTSERVE_STATE_REGEX")
if not STATE_REGEX:
    raise SoftserveException("No state regex defined!")


router = APIRouter(prefix="/think", tags=["think"])


@router.post(
    "/action/{state}", response_model=ThinkActionResponse, include_in_schema=False
)
async def think_action(
    req: ThinkAction, state: str = Path(pattern=STATE_REGEX)
) -> ThinkActionResponse:
    if not req.token:
        raise HTTPException(status_code=403, detail="think token required")
    if req.token != THINK_TOKEN:
        raise HTTPException(status_code=403, detail="invalid think token")

    workers = min(int(req.workers), MAX_WORKERS)
    workers = max(workers, MIN_WORKERS)

    iterations = min(int(req.iterations), MAX_ITERATIONS)
    iterations = max(iterations, MIN_ITERATIONS)

    action, stderr = engine("-w", str(workers), "-i", str(iterations), "-t", state)
    after, _ = engine("-a", action, state)
    actions, _ = get_actions(after)

    return ThinkActionResponse(action=action, state=after, actions=actions, log=stderr)


@router.post("/limits")
async def think_limits(req: ThinkLimits) -> ThinkLimitsResponse:
    if not req.token:
        raise HTTPException(status_code=403, detail="think token required")
    if req.token != THINK_TOKEN:
        raise HTTPException(status_code=403, detail="invalid think token")

    return ThinkLimitsResponse(
        min_iterations=MIN_ITERATIONS,
        max_iterations=MAX_ITERATIONS,
        min_workers=MIN_WORKERS,
        max_workers=MAX_WORKERS,
    )
