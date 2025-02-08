from random import choice

import pytest
from fastapi.testclient import TestClient

from .main import app


# When to abandon a random walk test
WALK_BACKOUT_DEPTH = 50


client = TestClient(app)


def get_initial_state():
    r = client.get("/state/initial")
    return r.json()["state"]


def get_actions(state):
    r = client.get(f"/state/{state}/actions")
    return r.json()["actions"]


def test_initial_state_actions():
    state = get_initial_state()
    assert len(get_actions(state)) == 3


def test_state_action_walk():
    state = get_initial_state()

    for _ in range(WALK_BACKOUT_DEPTH):
        actions = get_actions(state)

        # Terminal state
        if not actions:
            return

        action = choice(list(get_actions(state)))
        r = client.get(f"/state/{state}/act/{action}")
        assert r.status_code == 200
        state = r.json()["state"]

    pytest.fail("Random walk depth exceeded")


def test_player_play():
    r = client.post("/aivai/play-state")
    assert r.status_code == 200

    state = r.json()["state"]
    uuid = r.json()["uuid"]

    # Try an invalid action
    r = client.post("/aivai/submit-action", json={"action": "invalid", "uuid": uuid})
    assert r.status_code == 422

    action = choice(list(get_actions(state)))
    r = client.post("/aivai/submit-action", json={"action": action, "uuid": uuid})
    assert r.status_code == 200

    # Confirm uuid no longer exists
    r = client.post("/aivai/submit-action", json={"action": action, "uuid": uuid})
    assert r.status_code == 404
