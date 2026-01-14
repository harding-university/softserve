from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from fastapi import APIRouter, HTTPException

from ...models import Event, Player
from ..schema import *
from ...exceptions import SoftserveException

router = APIRouter(prefix="/event", tags=["event"])


@router.post(
    "/create",
    response_model=EventCreateResponse,
    summary="Create an event",
    description="""
""",
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
