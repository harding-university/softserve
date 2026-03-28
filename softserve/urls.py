from django.urls import path

from .views import aivai, event, game, player, state, think

urlpatterns = [
    # path("event/<str:name>/dashboard", event_dashboard, name="event-dashboard"),
    path("think/action/<str:state>", think.action),
    path("think/limits", think.limits),
    path("player/create", player.create),
    path("player/games", player.games),
    path("aivai/play-state", aivai.play_state),
    path("aivai/submit-action", aivai.submit_action),
    path("event/create", event.create),
    path("event/data", event.data),
    path("game/data", game.data),
    path("state/initial", state.initial),
    path("state/<str:state>/actions", state.actions),
    path("state/<str:state>/act/<str:action>", state.act),
    path("state/<str:state>/winner", state.winner),
]
