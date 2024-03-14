import pickle
from pickle import UnpicklingError

from django.shortcuts import render, get_object_or_404

from Login.models import Recipe, User, Favorites


# bu python dosyasında HomePage, DetailsPage, ProfilePage html sayfaları renderlanır
# ve bu sayfalarda kullanılıcak bilgiler ayarlanır

# HomePage.html renderlanırken databasedeki recipeler liste olarak gider
def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'HomePage.html', {'recipes': recipes})


# def home ile aynı mantıkta calısır tek farkı detail'i yoksa o recipenin 404 hatası verir(get_objects_or_404)
def details(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    return render(request, 'DetailPage.html', {'recipe': recipe})


# Binary seklinde depolanan dataya erismek istedigimizde b'\xef\xbb\xbf' bu kisim ile baslar binary sayilari
# Biz bu kismi kaldırıyoruz veriyi islemek icin
def remove_bom(data):
    if data.startswith(b'\xef\xbb\xbf'):
        return data[3:]
    return data


# def home ile aynı mantıkta calısır, login olmus olan user'in id'si ile
# databasede kayıtlı olan user'in userid'si eslenen useri yollar
# ayrıca olarak user'in kac tane favori tarifi oldugunu sayan metod kullanıyoruz
def profile(request, userid):
    user = User.objects.get(userid=userid)
    # bu kısım databasedeki user tablosunun favorites columndaki binary dataları
    # stringe cevirmek icin kullandıgımız metod
    # pythonun pickle packageini kullanıyoruz
    try:
        user_favorites = pickle.loads(remove_bom(user.favorites))
        num_favorites = len(user_favorites)
    except (UnpicklingError, SyntaxError):
        # remove_bom ile baslangıctaki gereksiz charları cıkarıyoruz
        user_favorites_str = remove_bom(user.favorites).decode('utf-8')
        # favorileri int arrayine cevirip ',' leri split ile kaldırıyoruz
        user_favorites = [int(favorite.strip()) for favorite in user_favorites_str.split(',') if favorite.strip()]
        # daha sonra kac tane favori oldugunu sayıyoruz
        num_favorites = len(user_favorites)

    favorites = Favorites.objects.filter(favoritesid__in=user_favorites)

    return render(request, 'ProfilePage.html', {'user': user, 'favorites': favorites, 'num_favorites': num_favorites})
