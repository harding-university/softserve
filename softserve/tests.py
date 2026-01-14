from random import choice
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
from fastapi.testclient import TestClient

from .api.main import app
from .api.util import engine, get_actions
from .models import *


class APITestCase(TransactionTestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.username = "test"
        r = self.client.post(
            "/player/create", json={"name": self.username, "email": "test@example.com"}
        )
        self.password = r.json()["token"]

        self.username2 = "test2"
        r = self.client.post(
            "/player/create",
            json={"name": self.username2, "email": "test2@example.com"},
        )
        self.password2 = r.json()["token"]

        self.username3 = "test3"
        r = self.client.post(
            "/player/create",
            json={"name": self.username3, "email": "test3@example.com"},
        )
        self.password3 = r.json()["token"]

    def get_initial_state(self):
        r = self.client.get("/state/initial")
        return r.json()["state"]

    def get_actions(self, state):
        r = self.client.get(f"/state/{state}/actions")
        return r.json()["actions"]

    def test_player_play(self):
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "mirror",
                "player": self.username,
                "token": self.password,
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
                "player": self.username,
                "token": self.password,
                "action": action,
                "action_id": action_id,
            },
        )
        self.assertEqual(r.status_code, 200)

        # Confirm we can't post the action a second time
        r = self.client.post(
            "/aivai/submit-action",
            json={
                "player": self.username,
                "token": self.password,
                "action": action,
                "action_id": action_id,
            },
        )
        self.assertEqual(r.status_code, 401)

    def test_invalid_token(self):
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "mirror",
                "player": self.username,
                "token": self.password + "1",
            },
        )
        self.assertEqual(r.status_code, 403)

    def test_event_create(self):
        r = self.client.post(
            "/event/create",
            json={
                "name": "test event",
                "players": ["test", "test2"],
                "game_pairs": 10,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Game.objects.count(), 2 * 10)

        # Can't make duplicate event name
        r = self.client.post(
            "/event/create",
            json={
                "name": "test event",
                "players": ["test", "test2"],
                "game_pairs": 10,
            },
        )
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Game.objects.count(), 2 * 10)

        r = self.client.post(
            "/event/create",
            json={
                "name": "test event 2",
                "players": ["test", "test2", "test3"],
                "game_pairs": 10,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Game.objects.count(), 2 * 10 + 2 * 3 * 10)

        # Try play-state with the event
        self.assertEqual(Action.objects.count(), 0)
        r = self.client.post(
            "/aivai/play-state",
            json={
                "event": "test event 2",
                "player": self.username,
                "token": self.password,
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Action.objects.count(), 1)


class ModelTestCase(TransactionTestCase):
    def setUp(self):
        self.password = "test"
        self.u1 = User.objects.create_user(username="player 1", password=self.password)
        self.u2 = User.objects.create_user(username="player 2", password=self.password)
        self.u3 = User.objects.create_user(username="player 3", password=self.password)

        self.e1 = Event.objects.create(name="event 1")
        self.e2 = Event.objects.create(name="event 2")

        self.g1 = Game.objects.create(event=self.e1)
        self.g1.add_player(self.u1)
        self.g1.add_player(self.u2)

        self.g2 = Game.objects.create(event=self.e1)
        self.g2.add_player(self.u1)
        self.g2.add_player(self.u3)

    def test_find_game_for(self):
        self.assertIsNone(self.e1.find_game_for(self.u3))

        game = self.e1.find_game_for(self.u1)
        self.assertIsNotNone(game)
        self.assertEqual(game, self.e1.find_game_for(self.u1))

        # u2 shouldn't have games
        # self.assertEqual(None, self.e1.find_game_for(self.u2))

        action = game.next_action()
        # We haven't submitted an action yet, so we should get the same game
        self.assertEqual(game, self.e1.find_game_for(self.u1))

        # Test this while we're here
        self.assertEqual(action, game.next_action())

        # Make a move
        action.notation = "1,-2|1,-1|0,-1|0,0"
        action.after_state = "1,-2|1,-1|0,-1|0,0|t"
        action.submit_timestamp = datetime.now()
        action.save()

        # We should get a different game now
        old_game = game
        game = self.e1.find_game_for(self.u1)
        self.assertNotEqual(game, old_game)

        # And a different action
        self.assertNotEqual(action, game.next_action())

        # Make a move in the other game
        action = game.next_action()
        action.notation = "1,-2|1,-1|0,-1|0,0"
        action.after_state = "1,-2|1,-1|0,-1|0,0|t"
        action.submit_timestamp = datetime.now()
        action.save()

        # And u1 shouldn't have any games left
        self.assertEqual(None, self.e1.find_game_for(self.u1))

        # Make u2 move
        game = self.e1.find_game_for(self.u2)
        self.assertEqual(game, self.g1)
        action = game.next_action()
        self.assertEqual(action.number, 2)
        action.notation = "1,-2|1,-1|0,-1|0,0"
        action.after_state = "1,-2|1,-1|0,-1|0,0|h"
        action.submit_timestamp = datetime.now()
        action.save()

        # And u1 should have a name now
        self.assertNotEqual(None, self.e1.find_game_for(self.u1))
