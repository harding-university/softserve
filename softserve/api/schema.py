from typing import List, Mapping

from pydantic import BaseModel


class AIvAIPlayState(BaseModel):
    event: str
    player: str
    token: str


class AIvAIPlayStateResponse(BaseModel):
    action_id: int
    state: str
    game_id: int
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
    name: str | None = None
    players: List[str]
    game_pairs: int


class EventCreateResponse(BaseModel):
    name: str
    token: str


class EventData(BaseModel):
    event_id: int
    forfeits: bool | None = True
    token: str


class EventDataResponse(BaseModel):
    name: str
    data: Mapping[str, Mapping[str, Mapping[str, int]] | List[Mapping[str, int | str]]]


class GameData(BaseModel):
    game_id: int
    token: str


class GameDataResponse(BaseModel):
    event: str
    players: List[str]
    initial_state: str
    states: List[str]
    actions: List[str]
    start_timestamp: str
    end_timestamp: str
    result: str
    forfeit: str


class PlayerCreate(BaseModel):
    name: str
    email: str


class PlayerCreateResponse(BaseModel):
    token: str


class PlayerGames(BaseModel):
    name: str
    token: str


class PlayerGamesResponse(BaseModel):
    game_ids: List[int]


class StateInitialResponse(EngineResponse):
    state: str


class StateActionsResponse(EngineResponse):
    actions: List[str]


class StateActResponse(StateActionsResponse):
    state: str


class Think(BaseModel):
    token: str
    workers: int | None = 0
    iterations: int | None = 0


class ThinkResponse(StateActionsResponse):
    action: str
    state: str


class StateWinnerResponse(EngineResponse):
    winner: str
