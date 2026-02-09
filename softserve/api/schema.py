from typing import List, Mapping

from pydantic import BaseModel


class AIvAIPlayState(BaseModel):
    event: str
    player: str
    token: str


class AIvAIPlayStateResponse(BaseModel):
    state: str
    action_id: int
    history: List[str]


class AIvAISubmitAction(BaseModel):
    action: str
    player: str
    token: str
    action_id: int


class AIvAISubmitActionResponse(BaseModel):
    winner: str


class EngineResponse(BaseModel):
    log: str


class EventCreate(BaseModel):
    name: str
    players: List[str]
    game_pairs: int


class EventCreateResponse(BaseModel):
    pass


class EventData(BaseModel):
    name: str
    token: str


class EventDataResponse(BaseModel):
    data: Mapping[str, Mapping[str, Mapping[str, int]]]


class PlayerCreate(BaseModel):
    name: str
    email: str


class PlayerCreateResponse(BaseModel):
    token: str


class StateInitialResponse(EngineResponse):
    state: str


class StateActionsResponse(EngineResponse):
    actions: List[str]


class StateActResponse(StateActionsResponse):
    state: str


class StateThinkResponse(StateActionsResponse):
    action: str
    state: str


class StateWinnerResponse(EngineResponse):
    winner: str
