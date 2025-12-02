from os import environ
from subprocess import run

from fastapi import HTTPException


class SoftserveException(Exception):
    pass


ENGINE = environ.get("SOFTSERVE_ENGINE")
if not ENGINE:
    raise SoftserveException("No engine defined!")


def engine(*args) -> (str, str):
    p = run([ENGINE] + list(args), capture_output=True, encoding="utf-8")

    if p.returncode:
        raise HTTPException(status_code=422, detail=p.stderr)

    return p.stdout.strip(), p.stderr.strip()


def get_actions(state: str) -> (list[str], str):
    stdout, stderr = engine("-l", state)

    if stdout.strip() == "terminal state":
        return ([], stderr)

    return (stdout.strip().split("\n"), stderr)
