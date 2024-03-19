from pickle import UnpicklingError

from django.shortcuts import render, get_object_or_404

from Login.models import Recipe, User, Favorites


# bu python dosyasında HomePage, DetailsPage, ProfilePage html sayfaları renderlanır
# ve bu sayfalarda kullanılıcak bilgiler ayarlanır

# HomePage.html renderlanırken databasedeki recipeler liste olarak gider
def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'HomePage.html', {'recipes': recipes})


# Tarif bilgilerini yolluyoruz recipe_id ' sine gore detay sayfasına
# Yıldız sisteminin matematigi, rating ' e gore half_star ve empty_star_range yolluyoruz
def details(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    # Yarım yıldız icin gerekli denklem
    half_star = (recipe.rating % 2) - 1
    # Bos yildiz icin gerekli denklem
    empty_star = round(5 - recipe.rating)
    empty_star_range = range(empty_star)
    # Kullandıgımız denklem round metodunun  3.5 2.5 ve 1.5 i assagi yuvarlamasından dolayi bu 3 durumda hata verir
    # Bizde bu 3 durumu ozellikle belirtiyoruz rating e 0.1 ekleyerek ozel durum olmadan cıkarıyoruz
    # 3.5 'i 3.6 gibi isliyoruz
    if recipe.rating == 3.5:
        half_star = ((recipe.rating + 0.1) % 2) - 1
        empty_star = round(5 - recipe.rating + 0.1)
        empty_star_range = range(empty_star - 1)
    if recipe.rating == 2.5:
        half_star = ((recipe.rating + 0.1) % 2) - 1
        empty_star = round(5 - recipe.rating + 0.1)
        empty_star_range = range(empty_star - 1)
    if recipe.rating == 1.5:
        half_star = ((recipe.rating + 0.1) % 2) - 1
        empty_star = round(5 - recipe.rating + 0.1)
        empty_star_range = range(empty_star - 1)
    return render(request, 'DetailPage.html',
                  {'recipe': recipe, 'half_star': half_star, 'empty_star_range': empty_star_range})


# Binary seklinde depolanan dataya erismek istedigimizde b'\xef\xbb\xbf' bu kisim ile baslar binary sayilari
# Biz bu kismi kaldırıyoruz veriyi islemek icin
def remove_bom(data):
    if data.startswith(b'\xef\xbb\xbf'):
        return data[3:]
    elif data.startswith(b''):
        return data[0:]
    return data


def profile(request, userid):
    import pickle
    user = User.objects.get(userid=userid)
    # Kullanıcının begendigi tarif sayısını ve ekledigi tarif sayisini binary'den int veya int listesine donusturen
    # metod, databasede bu veriler binary olarak tutuldugu icin bizim bunu islemememiz icin donusturme yapmamız
    # gerekli, bunu remove_bom yardımıyla bu metodda yapıyoruz
    # Bunu yaparken pythonun pickle kutuphanesini kullanırız
    # Bos bir profil geldigi zaman ise binary veri islemede hata cıkmasın diye direk olarak 0 atıyoruz
    # num_favorites ve num_recipes ' e 0 atıyoruz
    try:
        user_favorites = pickle.loads(remove_bom(user.favorites)) if user.favorites else 0
        num_favorites = len(user_favorites) if user.favorites else 0

        user_recipes = pickle.loads(remove_bom(user.recipes)) if user.recipes else 0
        num_recipes = len(user_recipes) if user.recipes else 0

    except (UnpicklingError, SyntaxError):
        user_favorites_str = remove_bom(user.favorites).decode('utf8')
        user_favorites = [int(favorite.strip()) for favorite in user_favorites_str.split(',') if favorite.strip()]
        num_favorites = len(user_favorites)

        user_recipes_str = remove_bom(user.recipes).decode('utf8')
        user_recipes = [int(recipe.strip()) for recipe in user_recipes_str.split(',') if recipe.strip()]
        num_recipes = len(user_recipes)
    # Bu kısım ise bos profil ve dolu profil ayrımı icin gerekli yine
    # Kullanıcının begendigi ve ekledigi tarifleri Profil sayfasına yollarız bu sekilde
    # recipe_id__in = user_recipes esitligi ile
    # Profil bos ise normal bir sekilde yollarız filter kullanmadan
    if num_recipes > 0:
        recipes = Recipe.objects.filter(recipe_id__in=user_recipes)
    else:
        recipes = Recipe.objects.all()

    if num_favorites > 0:
        favorites_recipeid = Favorites.objects.filter(favoritesid__in=user_favorites)
        favorites = Recipe.objects.filter(recipe_id__in=[favorite.recipeid for favorite in favorites_recipeid])
    else:
        favorites = Favorites.objects.all()
    # Sonuc olarak num_recipes, num_favorites olarak ProfilePage'le yollanır
    return render(request, 'ProfilePage.html', {'user': user, 'favorites': favorites, 'num_favorites': num_favorites,
                                                'recipes': recipes, 'num_recipes': num_recipes})
