from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from fastapi import APIRouter, HTTPException

from ...models import Event, Player
from ..schema import *
from ...exceptions import SoftserveException

from collections import Counter


router = APIRouter(prefix="/event", tags=["event"])


@router.post(
    "/create",
    response_model=EventCreateResponse,
    summary="Create an event",
    # TODO description
    # TODO don't include while under construction
    include_in_schema=False,
)
def event_create(req: EventCreate) -> EventCreateResponse:
    users = []
    for username in req.players:
        try:
            user = User.objects.get(username=username)
            users.append(user)
        except User.DoesNotExist:
            raise HTTPException(status_code=404, detail="player not found")

    if len(users) == 1:
        raise HTTPException(
            status_code=403, detail="event must have at least 2 players"
        )

    try:
        event = Event.objects.create(name=req.name)
    except IntegrityError:
        raise HTTPException(status_code=403, detail="event name already exists")

    try:
        event.create_matchups(users, req.game_pairs)
    except SoftserveException:
        event.delete()
        raise HTTPException(
            status_code=403,
            detail=f"too many games; max is {settings.SOFTSERVE_MAX_EVENT_GAMES}",
        )

    event.send_created_email()

    return EventCreateResponse()


@router.post(
    "/data",
    response_model=EventDataResponse,
    # TODO summary and description
    # TODO don't include while under construction
    include_in_schema=False,
)
def event_data(req: EventData) -> EventDataResponse:
    event = get_object_or_404(Event, name=req.name)

    if req.token != event.dashboard_token:
        raise HTTPException(
            status_code=403,
            detail=f"invalid token",
        )

    data = {}
    data["players"] = {}

    games = event.game_set.all()
    for game in games:
        for player in game.player_set.all():
            player_name = player.user.username

            if player_name not in data["players"]:
                data["players"][player_name] = Counter()

            if not game.end_timestamp:
                data["players"][player_name]["ongoing"] += 1
                continue

            forfeit = game.forfeit
            if forfeit:
                if player == forfeit:
                    data["players"][player_name]["forfeit_losses"] += 1
                else:
                    data["players"][player_name]["forfeit_wins"] += 1
                continue

            if player.winner:
                data["players"][player_name]["wins"] += 1
            elif player.opponent.winner:
                data["players"][player_name]["losses"] += 1
            else:
                data["players"][player_name]["draws"] += 1

    return EventDataResponse(data=data)
