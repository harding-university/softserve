from os import environ
from random import choice, randrange
from subprocess import run
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel


class SoftserveException(Exception):
    pass


ENGINE = environ.get("ENGINE")
if not ENGINE:
    raise SoftserveException("No engine defined!")


STATE_REGEX = r"(\d?\d,\d?\d\|){0,32}(\d?\d,\d?\d[ht]\d?\d|){0,32}[ht]"
# TODO action regex


app = FastAPI()

# TODO stub support, to be removed
stub_db = {}


def engine(*args) -> (str, str):
    p = run([ENGINE] + list(args), capture_output=True, encoding="utf-8")

    if p.returncode:
        raise HTTPException(status_code=422, detail=p.stderr)

    return p.stdout, p.stderr


def get_actions(state: str) -> (list[str], str):
    stdout, stderr = engine("-l", state)

    if stdout.strip() == "terminal state":
        return ([], stderr)

    return (stdout.strip().split("\n"), stderr)


# TODO stub support, to be removed
def get_arbitrary_state() -> str:
    stdout, _ = engine("-I")
    state = stdout.strip()
    for i in range(randrange(20)):
        action = choice(get_actions(state)[0])
        stdout, _ = engine("-a", action, state)
        state = stdout.strip()
    return state


class PlayerRequest(BaseModel):
    state: str
    uuid: str


# TODO stub
@app.get("/player/{player}/request", response_model=PlayerRequest)
def player_request(player: int) -> PlayerRequest:
    state = get_arbitrary_state()
    uuid = str(uuid4())
    return PlayerRequest(state=state, uuid=uuid)


class EngineResponse(BaseModel):
    log: str


class StateInitialResponse(EngineResponse):
    state: str


@app.get("/state/initial", response_model=StateInitialResponse)
async def state_initial() -> StateInitialResponse:
    stdout, stderr = engine("-I")
    return StateInitialResponse(state=stdout.strip(), log=stderr)


class StateActionsResponse(EngineResponse):
    actions: dict[str, str]


@app.get("/state/{state}/actions", response_model=StateActionsResponse)
async def state_actions(state: str = Path(pattern=STATE_REGEX)) -> StateActionsResponse:
    actions, stderr = get_actions(state)
    action_states = {
        action: engine("-a", action, state)[0].strip() for action in actions
    }
    return StateActionsResponse(actions=action_states, log=stderr)


class StateActResponse(EngineResponse):
    state: str


@app.get("/state/{state}/act/{action}")
async def state_act(
    state: str = Path(pattern=STATE_REGEX), action: str = Path()
) -> StateActResponse:
    actions, stderr = get_actions(state)
    if action not in actions:
        raise HTTPException(status_code=422, detail="invalid action")

    stdout, stderr = engine("-a", action, state)
    return StateActResponse(state=stdout.strip(), log=stderr)
