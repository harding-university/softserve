import secrets

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..models import Player


@api_view(["POST"])
def create(request):
    password = secrets.token_urlsafe()
    try:
        u = User.objects.create_user(
            username=request.data["name"],
            email=request.data["email"],
            password=password,
        )
    except IntegrityError:
        raise PermissionDenied(detail="player name already exists")

    return Response({"token": password})


@api_view(["POST"])
def games(request):
    user = authenticate(username=request.data["name"], password=request.data["token"])
    if not user:
        raise AuthenticationFailed(detail="invalid credentials")

    return Response(
        {"game_ids": [player.game.id for player in Player.objects.filter(user=user)]}
    )
