from typing import List

from pydantic import BaseModel


class AIvAIPlayState(BaseModel):
    state: str
    uuid: str


class AIvAISubmitAction(BaseModel):
    action: str
    uuid: str


class EngineResponse(BaseModel):
    log: str


class StateInitialResponse(EngineResponse):
    state: str


class StateActionsResponse(EngineResponse):
    actions: List[str]


class StateActResponse(EngineResponse):
    state: str
