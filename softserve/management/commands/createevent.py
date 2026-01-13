from itertools import combinations

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from softserve.models import *


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("players", nargs="+")
        parser.add_argument("--game-pairs", default=5, type=int)

    def handle(self, *args, **options):
        users = [User.objects.get(username=name) for name in options["players"]]

        event = Event.objects.create(name=options["name"])
        try:
            event.create_matchups(users, options["games-pairs"])
        except SoftserveException as e:
            print(e)
            event.delete()
