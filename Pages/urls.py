from django.urls import path
from . import views

# bir recipenin detay sayfasına giderken o recipenin recipe_id'si ile gonderilicegini belirtir
# bir userin profile sayfasına giderken o userin userid'si ile gonderilicegini belirtir
urlpatterns = [
    path("", views.home, name="home"),
    path("detail/<int:recipe_id>", views.details, name="details"),
    path("profile/<int:userid>", views.profile, name="profile"),
]
