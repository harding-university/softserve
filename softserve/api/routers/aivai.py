from random import choice, randrange
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..util import engine, get_actions


router = APIRouter()


# TODO stub support, to be removed
stub_db = {}


# TODO stub support, to be removed
def get_arbitrary_state() -> str:
    stdout, _ = engine("-I")
    state = stdout.strip()
    for i in range(randrange(20)):
        action = choice(get_actions(state)[0])
        stdout, _ = engine("-a", action, state)
        state = stdout.strip()
    return state


class AIvAIPlayState(BaseModel):
    state: str
    uuid: str


# TODO stub
@router.post(
    "/aivai/play-state",
    response_model=AIvAIPlayState,
    tags=["aivai"],
    summary="Get a state to play.",
)
def aivai_request() -> AIvAIPlayState:
    state = get_arbitrary_state()
    uuid = str(uuid4())

    stub_db[uuid] = state

    return AIvAIPlayState(state=state, uuid=uuid)


class AIvAISubmitAction(BaseModel):
    action: str
    uuid: str


@router.post(
    "/aivai/submit-action",
    tags=["aivai"],
    summary="Submit an action for a requested state.",
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
