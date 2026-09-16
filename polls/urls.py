from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("anket/olustur/", views.poll_create, name="poll_create"),
    path("anket/<uuid:poll_id>/", views.poll_detail, name="poll_detail"),
    path("anket/<uuid:poll_id>/kapat/", views.poll_close, name="poll_close"),
    path("anket/<uuid:poll_id>/sil/", views.poll_delete, name="poll_delete"),
    path("api/anket/<uuid:poll_id>/oy/", views.vote_api, name="vote_api"),
    path("u/<str:username>/", views.profile, name="profile"),
]
