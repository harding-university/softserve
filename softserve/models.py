import secrets

from django.db import models

from .exceptions import SoftserveException


class Action(models.Model):
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    player = models.ForeignKey("GamePlayer", on_delete=models.CASCADE)

    number = models.IntegerField()

    before_state = models.TextField()

    notation = models.TextField(blank=True)
    after_state = models.TextField(blank=True)

    create_timestamp = models.DateTimeField(auto_now_add=True)
    submit_timestamp = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.game} action {self.number} ({self.player.player.name})"


class Event(models.Model):
    name = models.TextField()

    def add_game(self, p1, p2):
        game = Game.objects.create(event=self)
        game.add_player(p1)
        game.add_player(p2)
        return game

    def find_game_for(self, player):
        if self.name == "mirror":
            game_player = GamePlayer.objects.filter(
                player=player, game__event=self, game__end_timestamp=None
            ).first()
            if game_player:
                game = game_player.game
            else:
                game = Game.objects.create(event=self)
                game.add_player(player)
                game.add_player(player)

            return game

        for game_player in GamePlayer.objects.filter(
            player=player, game__event=self, game__end_timestamp=None
        ):
            if game_player.game.turn == game_player.number:
                return game_player.game

        return None

    def __str__(self):
        return self.name


class Game(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    players = models.ManyToManyField("Player", through="GamePlayer")

    initial_state = models.TextField(default="h")

    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField(blank=True, null=True)

    @property
    def turn(self):
        self.last_action = self.action_set.order_by("number").last()
        if self.last_action:
            if self.last_action.submit_timestamp:
                state = self.last_action.after_state
            else:
                state = self.last_action.before_state
        else:
            state = self.initial_state
        return 0 if state.endswith("h") else 1

    def add_player(self, player):
        if self.players.count() >= 2:
            raise SoftserveException("Game is full")
        GamePlayer.objects.create(game=self, player=player, number=self.players.count())

    # Create (if necessary) and return an Action for the next action in the state
    def next_action(self):
        turn_player = self.gameplayer_set.get(number=self.turn)

        # TODO the way this is handled can be improved
        # self.last_action is a side effect of self.turn
        if self.last_action:
            if self.last_action.submit_timestamp == None:
                return self.last_action
            state = self.last_action.after_state
            number = self.last_action.number + 1
        else:
            state = self.initial_state
            number = 1

        return Action.objects.create(
            game=self,
            player=turn_player,
            number=number,
            before_state=state,
        )

    def __str__(self):
        try:
            p1 = self.gameplayer_set.get(number=0).player
            p2 = self.gameplayer_set.get(number=1).player
            return f"#{self.id} {self.event}: {p1} vs. {p2}"
        except GamePlayer.DoesNotExist:
            return f"#{self.id} {self.event}: awaiting matchup"


class GamePlayer(models.Model):
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    player = models.ForeignKey("Player", on_delete=models.CASCADE)

    number = models.IntegerField()
    winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player.name} P{self.number + 1} in {self.game}"


def generate_token():
    return secrets.token_urlsafe()


class Player(models.Model):
    name = models.TextField(unique=True)
    token = models.TextField(blank=True)

    def save(self, **kwargs):
        if self.token == "":
            self.token = generate_token()

        super().save(**kwargs)

    def __str__(self):
        return self.name
