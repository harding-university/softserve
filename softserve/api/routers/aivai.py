from datetime import datetime
from random import choice, randrange
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ...models import Action, Event, Game, Player
from ..schema import *
from ..util import engine, get_actions


AUTO_CREATE_EVENTS = [
    "mirror",
]


router = APIRouter(prefix="/aivai", tags=["aivai"])


@router.post(
    "/play-state",
    response_model=AIvAIPlayStateResponse,
    summary="Request a state to play",
    description="""
Call this to get a state for which you'll calculate an action. You'll
get a state and a uuid. Submit the resulting action, along with the
uuid, to `/aivai/submit-action`.

The state is independent and may be completely unrelated to states given
in previous and subsequent calls.
""",
)
def aivai_request(req: AIvAIPlayState) -> AIvAIPlayStateResponse:
    # Get event
    if req.event in AUTO_CREATE_EVENTS:
        event, _ = Event.objects.get_or_create(name=req.event)
    else:
        try:
            event = Event.objects.get(name=req.event)
        except Event.DoesNotExist:
            raise HTTPException(status_code=404, detail="event not found")

    # Get player
    # TODO add authentication
    player, _ = Player.objects.get_or_create(name=req.player)

    # Find a game in the event for the player
    game = Game.objects.find_for(event, player)

    # Create a pending action on the game
    action = game.next_action()

    return AIvAIPlayStateResponse(state=action.before_state, aid=action.id)


@router.post(
    "/submit-action",
    response_model=AIvAISubmitActionResponse,
    summary="Submit an action for a requested state",
    description="""
Call this after calling `/aivai/play-state`. See more information above.

The submitted action will be checked for validity, with HTTP 422 being
returned for invalid actions. If you believe an action is being
improperly validated, [open an
issue](https://github.com/harding-university/softserve/issues).
""",
)
def aivai_submit_action(req: AIvAISubmitAction) -> AIvAISubmitActionResponse:
    now = datetime.now()

    # Get player
    try:
        player = Player.objects.get(name=req.player)
    except Player.DoesNotExist:
        raise HTTPException(status_code=404, detail="player not found")

    # Get action
    try:
        action = Action.objects.get(pk=req.aid)
    except Action.DoesNotExist:
        raise HTTPException(status_code=404, detail="action_id not found")

    # Check auth
    # TODO do actual auth
    if action.player.player != player:
        raise HTTPException(status_code=401, detail="player-action_id mismatch")

    # Ensure action hasn't been already submitted
    if action.submit_timestamp:
        raise HTTPException(status_code=401, detail="action has already been submitted")

    # Check action submission
    state = action.before_state
    actions, _ = get_actions(state)
    if req.action not in actions:
        raise HTTPException(status_code=422, detail="invalid action")

    # Update action
    stdout, _ = engine("-a", req.action, state)
    action.notation = req.action
    action.after_state = stdout.strip()
    action.submit_timestamp = now
    action.save()

    # Check if state is terminal
    stdout, _ = engine("-W", action.after_state)
    winner = stdout.strip()
    if winner in ["h", "t", "draw"]:
        game.end_timestamp = now
        if winner == "h":
            gameplayer = game.gameplayer_set.get(number=1)
            gameplayer.winner = True
            gameplayer.save()
        if winner == "t":
            gameplayer = game.gameplayer_set.get(number=2)
            gameplayer.winner = True
            gameplayer.save()

    return AIvAISubmitActionResponse(winner=winner)
