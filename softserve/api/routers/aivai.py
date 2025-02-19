from random import choice, randrange
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..schema import *
from ..util import engine, get_actions


router = APIRouter(prefix="/aivai", tags=["aivai"])


# TODO stub support, to be removed
stub_db = {}


# TODO stub support, to be removed
def get_arbitrary_state() -> str:
    stdout, _ = engine("-I")
    state = stdout.strip()
    initial_state = state
    try:
        for i in range(randrange(20)):
            action = choice(get_actions(state)[0])
            stdout, _ = engine("-a", action, state)
            state = stdout.strip()
        return state
    except Exception:
        return initial_state


# TODO stub
@router.post(
    "/play-state",
    response_model=AIvAIPlayState,
    summary="Request a state to play",
    description="""
Call this to get a state for which you'll calculate an action. You'll
get a state and a uuid. Submit the resulting action, along with the
uuid, to `/aivai/submit-action`.

The state is independent and may be completely unrelated to states given
in previous and subsequent calls.

**Important:** This is currently only a stub that gives you an arbitrary
state.  Development and testing against it is encouraged. In the future,
this endpoint will require identification and authentication.
""",
)
def aivai_request() -> AIvAIPlayState:
    state = get_arbitrary_state()
    while len(get_actions(state)) == 0:
        state = get_arbitrary_state()

    uuid = str(uuid4())

    stub_db[uuid] = state

    return AIvAIPlayState(state=state, uuid=uuid)


# TODO stub
@router.post(
    "/submit-action",
    summary="Submit an action for a requested state",
    description="""
Call this after calling `/aivai/play-state`. See more information above.

The submitted action will be checked for validity, with HTTP 422 being
returned for invalid actions. If you believe an action is being
improperly validated, [open an
issue](https://github.com/harding-university/softserve/issues).

**Important:** This is currently only a stub. The uuid and action will
be validated, but everything will be forgotten once accepted.
""",
)
def aivai_submit_action(s: AIvAISubmitAction):
    try:
        state = stub_db[s.uuid]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"UUID not found")

    actions, stderr = get_actions(state)
    if s.action not in actions:
        raise HTTPException(status_code=422, detail="invalid action")

    del stub_db[s.uuid]
