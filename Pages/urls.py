from django.contrib import admin
from django.urls import path
from FoodRecipeApp import settings
from django.conf.urls.static import static
from . import views

# bir recipenin detay sayfasına giderken o recipenin recipe_id'si ile gonderilicegini belirtir
# bir userin profile sayfasına giderken o userin userid'si ile gonderilicegini belirtir
urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", views.admin, name="admin"),
    path("detail/<int:recipe_id>", views.details, name="details"),
    path("profile/<int:userid>", views.profile, name="profile"),
    path("update_rating/<int:recipe_id>", views.update_rating, name="update_rating"),
    path("add_comment/<int:recipe_id>", views.add_comment, name="add_comment"),
    path("most_favorites/", views.most_favorites, name="most_favorites"),
    path("update_favorite/<int:recipe_id>", views.update_favorite, name="update_favorite"),
    path("add_recipe/", views.add_recipe, name="add_recipe"),
    path("options/<int:userid>", views.options, name="options"),
    path("search/", views.search, name="search"),
    path("edit_recipe/<int:recipe_id>", views.edit_recipe, name="edit_recipe"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
