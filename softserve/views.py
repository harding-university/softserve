from collections import Counter, OrderedDict
from operator import attrgetter

from django.shortcuts import get_object_or_404, render

from .models import *


def event_dashboard(request, name):
    event = get_object_or_404(Event, name=name)

    games = event.game_set.all()
    open_games = []
    finished_games = []
    for game in games:
        if game.end_timestamp == None:
            open_games.append(game)
        else:
            finished_games.append(game)

    if finished_games:
        average_game_depth = sum([game.depth for game in finished_games]) / len(
            finished_games
        )
    else:
        average_game_depth = "n/a"

    players = sorted(
        set(
            gameplayer.player
            for gameplayer in GamePlayer.objects.filter(game__event=event)
        ),
        key=attrgetter("name"),
    )

    table_rows = []
    for player in players:
        row = []
        row.append(player.name)

        wins = OrderedDict()
        for opponent in players:
            wins[opponent] = 0

        losses = 0
        draws = 0
        forfeits = 0

        for gp in GamePlayer.objects.filter(
            player=player,
            game__event=event,
        ):
            if gp.game.end_timestamp == None:
                continue

            forfeit = gp.game.forfeit
            if forfeit:
                if forfeit == player:
                    forfeits += 1
                elif forfeit == gp.opponent.player:
                    wins[gp.opponent.player] += 1
                continue

            if gp.winner:
                wins[gp.opponent.player] += 1
            elif gp.opponent.winner:
                losses += 1
            else:
                draws += 1

        row.append(wins.values())
        row.append(sum(wins.values()))
        row.append(losses)
        row.append(sum(wins.values()) / losses if losses else "inf")
        row.append(draws)
        row.append(forfeits)
        row.append(sum(wins.values()) * 2 + draws * 1)

        table_rows.append(row)

    redact = request.GET.get("redact")

    return render(request, "softserve/event_dashboard.html", locals())
