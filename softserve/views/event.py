from collections import Counter

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..exceptions import SoftserveException
from ..models import Event, Player

EVENT_DATA_CACHE_TIMEOUT = 20


@api_view(["POST"])
def create(request):
    users = set()
    for username in request.data["players"]:
        try:
            user = User.objects.get(username=username)
            users.add(user)
        except User.DoesNotExist:
            raise NotFound(detail="player not found")

    if len(users) == 1:
        raise PermissionDenied(detail="event must have at least 2 players")

    try:
        event = Event.objects.create(name=request.data.get("name"))
    except IntegrityError:
        raise PermissionDenied(detail="event name already exists")

    try:
        event.create_matchups(users, request.data["game_pairs"])
    except SoftserveException:
        event.delete()
        raise PermissionDenied(
            detail=f"too many games; max is {settings.SOFTSERVE_MAX_EVENT_GAMES}",
        )

    event.send_created_email()

    return Response({"name": event.name, "token": event.dashboard_token})


@api_view(["POST"])
def data(request):
    try:
        event = Event.objects.get(pk=request.data["event_id"])
    except Event.DoesNotExist:
        raise NotFound(detail="event not found")

    if request.data["token"] != event.dashboard_token:
        raise PermissionDenied(detail="invalid token")

    cache_key = f"event:{event.id}:data"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response({"name": event.name, "data": cached_data})

    data = {}
    data["players"] = {}
    data["games"] = []

    games = event.game_set.all()
    for game in games:
        game_data = {}
        game_data["id"] = game.id
        data["games"].append(game_data)

        game_data["x"] = game.player_name(0)
        game_data["y"] = game.player_name(1)

        for player in game.player_set.all():
            player_name = player.name()

            if player_name not in data["players"]:
                data["players"][player_name] = Counter()

            if not game.end_timestamp:
                data["players"][player_name]["ongoing"] += 1
                game_data["result"] = "ongoing"
                continue

            if request.data.get("forfeits"):
                forfeit = game.forfeit
                if forfeit:
                    if player == forfeit:
                        data["players"][player_name]["forfeit_losses"] += 1
                        if player_name == game_data["x"]:
                            game_data["result"] = "x forfeit"
                        if player_name == game_data["y"]:
                            game_data["result"] = "y forfeit"
                    else:
                        data["players"][player_name]["forfeit_wins"] += 1
                    continue

            if player.winner:
                data["players"][player_name]["wins"] += 1
                if player_name == game_data["x"]:
                    game_data["result"] = "x win"
                if player_name == game_data["y"]:
                    game_data["result"] = "y win"
            elif player.opponent.winner:
                data["players"][player_name]["losses"] += 1
            else:
                data["players"][player_name]["draws"] += 1
                game_data["result"] = "draw"

    cache.set(cache_key, data, timeout=30)

    return Response({"name": event.name, "data": data})
