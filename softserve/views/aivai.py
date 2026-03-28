from datetime import datetime
from random import choice, randrange
from uuid import uuid4

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..models import Action, Event, Game, Player, AUTO_CREATE_EVENTS
from ..util import engine, get_actions


@api_view(["POST"])
def play_state(request):
    # Get user
    user = authenticate(
        username=request.data.get("player"), password=request.data.get("token")
    )
    if not user:
        raise AuthenticationFailed(detail="invalid credentials")

    if request.data["event"] == "*":
        # Get any event
        game = Event.objects.find_any_game_for(user)
    else:
        # Get requested event
        if request.data["event"] in AUTO_CREATE_EVENTS:
            event, _ = Event.objects.get_or_create(name=request.data["event"])
        else:
            try:
                event = Event.objects.get(name=request.data["event"])
            except Event.DoesNotExist:
                raise NotFound(detail="event not found")

        # Find a game in the event for the player
        game = event.find_game_for(user)

    if game == None:
        return Response(
            {"detail": "no games waiting; please try again"},
            status=204,
        )

    # Create a pending action on the game
    action = game.next_action()

    return Response(
        {
            "state": action.before_state,
            "action_id": action.id,
            "game_id": game.id,
            "history": game.history,
        }
    )


@api_view(["POST"])
def submit_action(request):
    # Grab the submit timestamp right away
    now = datetime.now()

    # Get user
    user = authenticate(
        username=request.data.get("player"), password=request.data.get("token")
    )
    if not user:
        raise AuthenticationFailed(detail="invalid credentials")

    # Get action
    try:
        action = Action.objects.get(pk=request.data["action_id"])
    except Action.DoesNotExist:
        raise NotFound(detail="action_id not found")

    if action.player.user != user:
        raise NotAuthenticated(detail="player-action_id mismatch")

    # Ensure action hasn't been already submitted
    if action.submit_timestamp:
        raise PermissionDenied(detail="action has already been submitted")

    # Check action submission
    state = action.before_state
    actions, _ = get_actions(state)
    if request.data["action"] not in actions:
        raise ValidationError(detail="invalid action")

    # Update action
    stdout, _ = engine(f"-a", request.data["action"], state)
    action.notation = request.data["action"]
    action.after_state = stdout.strip()
    action.submit_timestamp = now
    action.save()

    # Check if state is terminal
    game = action.game
    stdout, _ = engine("-W", action.after_state)
    winner = stdout.strip()
    if winner in ["x", "o", "draw"] or game.threefold_repetition:
        game.end_timestamp = now
        game.save()
        if winner == "x":
            player = game.player_set.get(number=0)
            player.winner = True
            player.save()
        if winner == "o":
            player = game.player_set.get(number=1)
            player.winner = True
            player.save()

    return Response({"winner": winner})
