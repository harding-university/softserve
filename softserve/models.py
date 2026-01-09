from django.conf import settings
from django.contrib.auth.admin import UserAdmin
from django.db import models

from .exceptions import SoftserveException


class Action(models.Model):
    """A single, discrete action taken by a player during a game"""

    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    player = models.ForeignKey("Player", on_delete=models.CASCADE)

    # Sequence number in game
    number = models.IntegerField()

    # State before the action
    before_state = models.TextField()
    # Notation for the action itself
    notation = models.TextField(blank=True)
    # State after the action
    after_state = models.TextField(blank=True)

    # Create and submit times are tracked separately, to determine think time
    create_timestamp = models.DateTimeField(auto_now_add=True)
    submit_timestamp = models.DateTimeField(blank=True, null=True)

    @property
    def think_time(self):
        if not self.submit_timestamp:
            return None
        return self.submit_timestamp - self.create_timestamp

    def __str__(self):
        return f"{self.game} action {self.number} ({self.user.username})"


class Event(models.Model):
    name = models.TextField(unique=True)

    def add_game(self, p1, p2):
        game = Game.objects.create(event=self)
        game.add_player(p1)
        game.add_player(p2)
        return game

    def find_game_for(self, user):
        if self.name == "mirror":
            player = Player.objects.filter(
                user=user, game__event=self, game__end_timestamp=None
            ).first()
            if player:
                game = player.game
            else:
                game = Game.objects.create(event=self)
                game.add_player(user)
                game.add_player(user)

            return game

        for player in Player.objects.filter(
            user=user, game__event=self, game__end_timestamp=None
        ):
            if player.game.turn == player:
                return player.game

        return None

    def __str__(self):
        return self.name


class Game(models.Model):
    """A matchup between users, each having a player"""

    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Player")

    # NOTE: This is loaded from the external engine binary
    # Decision pending on whether this is a good idea
    initial_state = models.TextField(default=settings.SOFTSERVE_INIITAL_STATE)

    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField(blank=True, null=True)

    @property
    def last_action(self):
        """Get the sequencially highest action (but don't create a new one)"""
        return self.action_set.order_by("number").last()

    @property
    def turn(self):
        """Get the player whose turn it is to act"""
        # NOTE: This assumes one action per turn and no skipping players
        last_action = self.last_action

        if not last_action:
            return self.player_set.get(number=0)

        if last_action.submit_timestamp:
            return self.last_action.player.opponent
        return self.last_action.player

    @property
    def duration(self):
        return self.end_timestamp - self.start_timestamp

    @property
    def depth(self):
        return self.action_set.order_by("-number").first().number + 1

    @property
    def forfeit(self):
        """Returns the first player to exceed think time, if any"""
        for action in self.action_set.order_by("number"):
            if action.think_time > settings.SOFTSERVE_THINK_TIME:
                return action.player
        return None

    def add_player(self, user):
        if self.player_set.count() >= 2:
            raise SoftserveException(f"{ str(self) } is full")
        Player.objects.create(game=self, user=user, number=self.player_set.count())

    def next_action(self):
        """Create (if necessary) and return the next action"""
        last_action = self.last_action

        if last_action:
            # If we've created an action but it hasn't been submitted yet
            if last_action.submit_timestamp == None:
                return last_action

            state = last_action.after_state
            number = last_action.number + 1
        else:
            state = self.initial_state
            number = 1
            number = 1

        return Action.objects.create(
            game=self,
            player=self.turn,
            number=number,
            before_state=state,
        )

    def __str__(self):
        try:
            p1 = self.player_set.get(number=0).player
            p2 = self.player_set.get(number=1).player
            return f"#{self.id} {self.event}: {p1} vs. {p2}"
        except GamePlayer.DoesNotExist:
            return f"#{self.id} {self.event}: awaiting matchup"


# NOTE: When the user-facing API uses the term player, it referse to a
# Django user, not this class. This class here is the junction between
# users and games.
class Player(models.Model):
    """A user's role in a game"""

    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # I.e. first player, second player (zero-indexed)
    number = models.IntegerField()
    # Did they win this game? (True only if the game is over and they won)
    winner = models.BooleanField(default=False)

    @property
    def opponent(self):
        for player in self.game.player_set.all():
            if player != self:
                return player

    def __str__(self):
        return f"{self.user.name} P{self.number + 1} in {self.game}"
