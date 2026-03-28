from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..exceptions import SoftserveException
from ..models import Game


@api_view(["POST"])
def data(request):
    try:
        game = Game.objects.get(pk=request.data["game_id"])
    except Game.DoesNotExist:
        raise NotFound(detail="game not found")

    players = game.player_set.order_by("number")

    good_player_token = max(
        [player.user.check_password(request.data["token"]) for player in players]
    )
    if not good_player_token and request.data["token"] != game.event.dashboard_token:
        raise PermissionDenied(detail="invalid token")

    result = "draw"
    if not game.end_timestamp:
        result = "ongoing"
    winner = game.player_set.filter(winner=True).first()
    if winner:
        result = winner.user.username

    forfeit = game.forfeit.user.username if game.forfeit else "none"

    return Response(
        {
            "event": game.event.name,
            "players": [player.user.username for player in players],
            "result": result,
            "forfeit": forfeit,
            "initial_state": game.initial_state,
            "states": game.history,
            "actions": game.history_actions,
            "start_timestamp": str(game.start_timestamp),
            "end_timestamp": str(game.end_timestamp),
        }
    )
