from django.urls import path

from .views import *

urlpatterns = [
    path("event/<str:name>/dashboard", event_dashboard, name="event-dashboard"),
]
