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
    description="""""",
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
        raise HTTPException(status_code=403, detail="username already exists")

    return PlayerCreateResponse(token=password)
