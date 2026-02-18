from fastapi import APIRouter, HTTPException

from ...exceptions import SoftserveException
from ...models import Game
from ..schema import *

router = APIRouter(prefix="/game", tags=["event"])


@router.post(
    "/data",
    response_model=GameDataResponse,
)
def game_history(req: GameData) -> GameDataResponse:
    try:
        game = Game.objects.get(pk=req.game_id)
    except Game.DoesNotExist:
        raise HTTPException(status_code=404, detail="game not found")

    players = game.player_set.order_by("number")

    good_player_token = max(
        [player.user.check_password(req.token) for player in players]
    )
    if not good_player_token and req.token != game.event.dashboard_token:
        raise HTTPException(
            status_code=403,
            detail=f"invalid token",
        )

    result = "draw"
    if not game.end_timestamp:
        result = "ongoing"
    winner = game.player_set.filter(winner=True).first()
    if winner:
        result = winner.user.username

    forfeit = game.forfeit.user.username if game.forfeit else "none"

    return GameDataResponse(
        event=game.event.name,
        players=[player.user.username for player in players],
        result=result,
        forfeit=forfeit,
        initial_state=game.initial_state,
        states=game.history,
        actions=game.history_actions,
        start_timestamp=str(game.start_timestamp),
        end_timestamp=str(game.end_timestamp),
    )
