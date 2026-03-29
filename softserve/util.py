from os import environ
from subprocess import run
import re

from django.conf import settings
from rest_framework.exceptions import *

# TODO
MIN_WORKERS = 1
MAX_WORKERS = 4
MIN_ITERATIONS = 1000
MAX_ITERATIONS = 500000


class SoftserveException(Exception):
    pass


ENGINE = environ.get("SOFTSERVE_ENGINE")
if not ENGINE:
    raise SoftserveException("No engine defined!")


STATE_REGEX = environ.get("SOFTSERVE_STATE_REGEX")
if not STATE_REGEX:
    raise SoftserveException("No state regex defined!")


def validate_state(state):
    if not re.fullmatch(STATE_REGEX, state):
        raise ValidationError(detail="invalid state")


def __engine(*args):
    p = run([ENGINE] + list(args), capture_output=True, encoding="utf-8")

    if p.returncode:
        raise HTTPException(status_code=422, detail=p.stderr)

    return p.stdout.strip(), p.stderr.strip()


def get_initial_state():
    stdout, stderr = __engine("-I")
    return stdout.strip(), stderr


def get_actions(state) -> (list[str], str):
    validate_state(state)
    stdout, stderr = __engine("-l", state)

    if stdout.strip() == "terminal state":
        return ([], stderr)

    return (stdout.strip().split("\n"), stderr)


def get_after(state, action):
    validate_state(state)
    stdout, stderr = __engine("-l", state)

    stdout, stderr = __engine(f"-a", action, state)
    return stdout.strip(), stderr


def get_winner(state):
    validate_state(state)
    stdout, stderr = __engine("-l", state)
    stdout, stderr = __engine("-W", state)
    return stdout.strip(), stderr


def think(state, workers, iterations):
    validate_state(state)
    stdout, stderr = __engine("-l", state)
    workers = min(int(workers), MAX_WORKERS)
    workers = max(workers, MIN_WORKERS)

    iterations = min(int(iterations), MAX_ITERATIONS)
    iterations = max(iterations, MIN_ITERATIONS)

    stdout, stderr = __engine("-w", str(workers), "-i", str(iterations), "-t", state)
    return stdout.strip(), stderr
