from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("anket/olustur/", views.poll_create, name="poll_create"),
    path("anket/<uuid:poll_id>/", views.poll_detail, name="poll_detail"),
]
