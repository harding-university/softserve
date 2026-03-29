from os import environ

from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..util import get_actions, get_initial_state, get_after, think

THINK_TOKEN = environ.get("SOFTSERVE_THINK_TOKEN")


@api_view(["POST"])
def action(request, state):
    if "token" not in request.data:
        raise NotAuthenticated(detail="think token required")
    if request.data["token"] != THINK_TOKEN:
        raise AuthenticationFailed(detail="invalid think token")

    action, stderr = think(state, request.data["workers"], request.data["iterations"])
    after, _ = get_after(state, action)
    actions, _ = get_actions(after)

    return Response(
        {"action": action, "state": after, "actions": actions, "log": stderr}
    )


@api_view(["POST"])
def limits(request):
    if "token" not in request.data:
        raise NotAuthenticated(detail="think token required")
    if request.data["token"] != THINK_TOKEN:
        raise AuthenticationFailed(detail="invalid think token")

    return Response(
        {
            "min_iterations": MIN_ITERATIONS,
            "max_iterations": MAX_ITERATIONS,
            "min_workers": MIN_WORKERS,
            "max_workers": MAX_WORKERS,
        }
    )
