from django.urls import path
from Pages.views import home
from . import views

# Register, home ve loginin pathleri veirlmiştir ve kodda kullanılıcak isimleri
# FoodRecipeApp\urls.py da belirtirdiği gibi html kodlarını calıştırmak icin gerekli prosedurler bu kısım
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout")
]
