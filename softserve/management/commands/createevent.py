from itertools import combinations

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from softserve.models import *


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("players", nargs="+")
        parser.add_argument("--games", default=5, type=int)

    def handle(self, *args, **options):
        players = [User.objects.get(username=name) for name in options["players"]]

        event = Event.objects.create(name=options["name"])

        for p1, p2 in combinations(players, 2):
            for _ in range(options["games"]):
                event.add_game(p1, p2)
                event.add_game(p2, p1)
