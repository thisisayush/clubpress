from django.urls import path

from .views import *

app_name = "club"

urlpatterns = [
    path("register/", ClubRegistrationView, name="register-club"),
    path("<slug>/event/create/", EventEditView, kwargs={"id":-1}, name="create-event"),
    path("<slug>/event/<int:id>/manage/edit/", EventEditView, name="edit-event"),
    path("<slug>/event/<int:id>/manage/od/", EventEditView, name="od-event"),
    path("<slug>/event/<int:id>/", EventView, name="event"),
    path("<slug>/event/<int:id>/apply-od/", ApplyODView, name="apply-od"),
    path("<slug>/event/<int:id>/rsvp/<rsvp>/", SetRSVPView, name="event-rsvp"),
    path("<slug>/event/<int:id>/register/", RegisterEventView, name="register-event"),
    path("<slug>/", ClubIndexView, name="club-home"),
    path("<slug>/join/", ClubJoinView, name="club-join"),
    path("<slug>/edit/", ClubEditView, name="club-edit"),
]
