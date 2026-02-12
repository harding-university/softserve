from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
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
    description=f"""
Call this to create a custom tournament for your own AI testing purposes.

Your POST must contain a json object with the following fields:
- `players`: a list of player names to include in the tournament
- `game_pairs`: the number of game pairs to play between players (so 5
   means each player plays each other player a total of 10 times, 5
   going first and 5 going second)
- `name`: the name of the event (optional; a name will be assigned if absent)

Events have a maximum number of total games. On this Softserve instance,
the maximum is f{settings.SOFTSERVE_MAX_EVENT_GAMES} games.

After the event is created, each player's email will receive a link to
the event dashboard, which displays the results.
""",
)
def event_create(req: EventCreate) -> EventCreateResponse:
    users = set()
    for username in req.players:
        try:
            user = User.objects.get(username=username)
            users.add(user)
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

    return EventCreateResponse(name=event.name, token=event.dashboard_token)


@router.post(
    "/data",
    response_model=EventDataResponse,
    summary="Get data for an event",
    description="""
Call this to get results and other data for an event.

You shouldn't need to call this yourself, unless you're creating your
own custom event dashboard. Otherwise, use the link sent in the email
at time of event creation to view event results.

If you are building a custom dashboard or otherwise in need of this,
you'll need the token included as part of the URL in the email.
""",
)
def event_data(req: EventData) -> EventDataResponse:
    try:
        event = Event.objects.get(pk=req.event_id)
    except Event.DoesNotExist:
        raise HTTPException(status_code=404, detail="event not found")

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

    return EventDataResponse(name=event.name, data=data)
