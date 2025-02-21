from typing import List

from pydantic import BaseModel


class AIvAIPlayState(BaseModel):
    event: str
    player: str


class AIvAIPlayStateResponse(BaseModel):
    state: str
    aid: int


class AIvAISubmitAction(BaseModel):
    action: str
    player: str
    aid: str


class AIvAISubmitActionResponse(BaseModel):
    winner: str


class EngineResponse(BaseModel):
    log: str


class StateInitialResponse(EngineResponse):
    state: str


class StateActionsResponse(EngineResponse):
    actions: List[str]


class StateActResponse(EngineResponse):
    state: str
