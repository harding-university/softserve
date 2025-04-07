from random import choice

from django.test import TestCase, TransactionTestCase
from fastapi.testclient import TestClient

from .api.main import app
from .models import *


# When to abandon a random walk test
WALK_BACKOUT_DEPTH = 50


class APITestCase(TransactionTestCase):
    def setUp(self):
        self.client = TestClient(app)

        self.player = Player.objects.create(name="test")

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
                "player": self.player.name,
                "token": self.player.token,
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
            json={
                "player": self.player.name,
                "token": self.player.token,
                "action": action,
                "action_id": action_id,
            },
        )
        self.assertEqual(r.status_code, 200)

        # Confirm we can't post the action a second time
        r = self.client.post(
            "/aivai/submit-action",
            json={
                "player": self.player.name,
                "token": self.player.token,
                "action": action,
                "action_id": action_id,
            },
        )
        self.assertEqual(r.status_code, 401)

    def test_mirror_game(self):
        winner = "none"
        for _ in range(WALK_BACKOUT_DEPTH):
            r = self.client.post(
                "/aivai/play-state",
                json={
                    "event": "mirror",
                    "player": self.player.name,
                    "token": self.player.token,
                },
            )
            self.assertEqual(r.status_code, 200)

            state = r.json()["state"]
            action_id = r.json()["action_id"]

            action = choice(list(self.get_actions(state)))
            r = self.client.post(
                "/aivai/submit-action",
                json={
                    "player": self.player.name,
                    "token": self.player.token,
                    "action_id": action_id,
                    "action": action,
                },
            )
            self.assertEqual(r.status_code, 200)

            winner = r.json()["winner"]
            if winner != "none":
                break

        # Make sure the game actually ended (else we hit the backout depth)
        self.assertNotEqual(winner, "none")

        # Make sure we only played one game
        self.assertEqual(Game.objects.count(), 1)

        # And this should start a new game
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "mirror",
                "player": self.player.name,
                "token": self.player.token,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Game.objects.count(), 2)

    def test_invalid_token(self):
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "mirror",
                "player": self.player.name,
                "token": self.player.token + "1",
            },
        )
        self.assertEqual(r.status_code, 403)
