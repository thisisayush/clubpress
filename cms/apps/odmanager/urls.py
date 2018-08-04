from django.urls import path
from .views import *

app_name = "odmanager"

urlpatterns = [
    path("", testView )
]