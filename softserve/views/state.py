from os import environ

from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..util import engine, get_actions, get_initial_state, SoftserveException

STATE_REGEX = environ.get("SOFTSERVE_STATE_REGEX")
if not STATE_REGEX:
    raise SoftserveException("No state regex defined!")


@api_view(["GET"])
def initial(request):
    state, stderr = get_initial_state()
    return Response({"state": state, "log": stderr})


@api_view(["GET"])
def actions(request, state):
    actions, stderr = get_actions(state)
    return Response({"actions": actions, "log": stderr})


@api_view(["GET"])
def act(request, state, action):
    actions, stderr = get_actions(state)
    if action not in actions:
        raise ValidationError(detail="invalid action")

    stdout, stderr = engine("-a", action, state)
    after = stdout.strip()
    actions, _ = get_actions(after)
    return Response({"state": after, "actions": actions, "log": stderr})


@api_view(["GET"])
def winner(request, state):
    stdout, stderr = engine("-W", state)
    return Response({"winner": stdout.strip(), "log": stderr})
