from random import choice
from datetime import datetime

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


class ModelTestCase(TransactionTestCase):
    def setUp(self):
        self.p1 = Player.objects.create(name="player 1")
        self.p2 = Player.objects.create(name="player 2")
        self.p3 = Player.objects.create(name="player 3")

        self.e1 = Event.objects.create(name="event 1")
        self.e2 = Event.objects.create(name="event 2")

        self.g1 = Game.objects.create(event=self.e1)
        self.g1.add_player(self.p1)
        self.g1.add_player(self.p2)

        self.g2 = Game.objects.create(event=self.e1)
        self.g2.add_player(self.p1)
        self.g2.add_player(self.p3)

    def test_find_game_for(self):
        self.assertIsNone(self.e1.find_game_for(self.p3))

        game = self.e1.find_game_for(self.p1)
        self.assertEqual(game, self.e1.find_game_for(self.p1))

        # p2 shouldn't have games
        # self.assertEqual(None, self.e1.find_game_for(self.p2))

        action = game.next_action()
        # We haven't submitted an action yet, so we should get the same game
        self.assertEqual(game, self.e1.find_game_for(self.p1))

        # Test this while we're here
        self.assertEqual(action, game.next_action())

        # Make a move
        action.notation = "1,-2|1,-1|0,-1|0,0"
        action.after_state = "1,-2|1,-1|0,-1|0,0|t"
        action.submit_timestamp = datetime.now()
        action.save()

        # We should get a different game now
        old_game = game
        game = self.e1.find_game_for(self.p1)
        self.assertNotEqual(game, old_game)

        # And a different action
        self.assertNotEqual(action, game.next_action())

        # Make a move in the other game
        action = game.next_action()
        action.notation = "1,-2|1,-1|0,-1|0,0"
        action.after_state = "1,-2|1,-1|0,-1|0,0|t"
        action.submit_timestamp = datetime.now()
        action.save()

        # And p1 shouldn't have any games left
        self.assertEqual(None, self.e1.find_game_for(self.p1))

        # Make p2 move
        game = self.e1.find_game_for(self.p2)
        self.assertEqual(game, self.g1)
        action = game.next_action()
        self.assertEqual(action.number, 2)
        action.notation = "1,-2|1,-1|0,-1|0,0"
        action.after_state = "1,-2|1,-1|0,-1|0,0|h"
        action.submit_timestamp = datetime.now()
        action.save()

        # And p1 should have a name now
        self.assertNotEqual(None, self.e1.find_game_for(self.p1))
