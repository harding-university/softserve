from django.urls import path

from .views import think

urlpatterns = [
    #path("event/<str:name>/dashboard", event_dashboard, name="event-dashboard"),
    path("think/action/<str:state>", think.action),
    path("think/limits", think.limits),
]
