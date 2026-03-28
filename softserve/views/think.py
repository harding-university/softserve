from os import environ

from rest_framework.decorators import api_view
from rest_framework.exceptions import *
from rest_framework.response import Response

from ..util import engine, get_actions, get_initial_state, SoftserveException

THINK_TOKEN = environ.get("SOFTSERVE_THINK_TOKEN")

# TODO
MIN_WORKERS = 1
MAX_WORKERS = 4
MIN_ITERATIONS = 1000
MAX_ITERATIONS = 500000

STATE_REGEX = environ.get("SOFTSERVE_STATE_REGEX")
if not STATE_REGEX:
    raise SoftserveException("No state regex defined!")


@api_view(["POST"])
def action(request, state):
    if "token" not in request.data:
        raise NotAuthenticated(detail="think token required")
    if request.data["token"] != THINK_TOKEN:
        raise AuthenticationFailed(detail="invalid think token")

    workers = min(int(request.data.get("workers", MIN_WORKERS)), MAX_WORKERS)
    workers = max(workers, MIN_WORKERS)

    iterations = min(
        int(request.data.get("iterations", MIN_ITERATIONS)), MAX_ITERATIONS
    )
    iterations = max(iterations, MIN_ITERATIONS)

    action, stderr = engine("-w", str(workers), "-i", str(iterations), "-t", state)
    after, _ = engine("-a", action, state)
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
