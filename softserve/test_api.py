from random import choice

from fastapi.testclient import TestClient

from .api import app


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

    # TODO terminal states instead of hardcoded depth
    for _ in range(20):
        action = choice(list(get_actions(state).keys()))
        r = client.get(f"/state/{state}/act/{action}")
        assert r.status_code == 200
        state = r.json()["state"]
        print(action)
        print(r.json()["log"])
