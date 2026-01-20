import secrets

from django.contrib.auth.models import User
from django.db import IntegrityError
from fastapi import APIRouter, HTTPException

from ..schema import *

router = APIRouter(prefix="/player", tags=["player"])


@router.post(
    "/create",
    response_model=PlayerCreateResponse,
    summary="Create a player",
    description="""
Call this to create a new player. Save the token (persistently&mdash;do
not call this every time you run your program) and use it to
authenticate to `/aivai` endpoints.
""",
)
def player_create(req: PlayerCreate) -> PlayerCreateResponse:
    password = secrets.token_urlsafe()
    try:
        u = User.objects.create_user(
            username=req.name,
            email=req.email,
            password=password,
        )
    except IntegrityError:
        raise HTTPException(status_code=403, detail="player name already exists")

    return PlayerCreateResponse(token=password)
