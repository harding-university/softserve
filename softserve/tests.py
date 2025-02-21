from random import choice

from django.test import TestCase
from fastapi.testclient import TestClient

from .api.main import app


# When to abandon a random walk test
WALK_BACKOUT_DEPTH = 50


class APITestCase(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def get_initial_state(self):
        r = self.client.get("/state/initial")
        return r.json()["state"]

    def get_actions(self, state):
        r = self.client.get(f"/state/{state}/actions")
        return r.json()["actions"]

    def test_initial_state_actions(self):
        state = self.get_initial_state()
        self.assertEqual(len(self.get_actions(state)), 3 * 24)

    def test_state_action_walk(self):
        state = self.get_initial_state()

        for _ in range(WALK_BACKOUT_DEPTH):
            actions = self.get_actions(state)

            # Terminal state
            if not actions:
                return

            action = choice(list(self.get_actions(state)))
            r = self.client.get(f"/state/{state}/act/{action}")
            assert r.status_code == 200
            state = r.json()["state"]

        self.fail("Random walk depth exceeded")

    def test_player_play(self):
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "mirror",
                "player": "test",
            },
        )
        self.assertEqual(r.status_code, 200)

        state = r.json()["state"]
        action_id = r.json()["action_id"]

        # Try an invalid action
        r = self.client.post(
            "/aivai/submit-action", json={"action": "invalid", "action_id": action_id}
        )
        self.assertEqual(r.status_code, 422)

        action = choice(list(self.get_actions(state)))
        r = self.client.post(
            "/aivai/submit-action",
            json={"player": "test", "action": action, "action_id": action_id},
        )
        self.assertEqual(r.status_code, 200)

        # Confirm uuid no longer exists
        r = self.client.post(
            "/aivai/submit-action",
            json={"player": "test", "action": action, "action_id": action_id},
        )
        self.assertEqual(r.status_code, 401)

    def test_mirror_game(self):
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "mirror",
                "player": "test",
            },
        )
        
        # TODO
