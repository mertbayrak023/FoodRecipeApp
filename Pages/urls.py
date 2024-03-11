from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("detail/<int:recipe_id>", views.details, name="details"),
    path("profile/<int:userid>", views.profile, name="profile"),
]
