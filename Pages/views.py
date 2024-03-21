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
# Yıldız sisteminin matematigi, rating ' e gore full, half ve empty yolluyoruz
# Bu degerlere gore html kısmında for loopu ile uygun yıldızları vermek icin kullanıyoruz
def print_rating(rating_):
    rating = rating_
    maximum = 5.0
    empty = round(maximum - rating)
    full = int(round(rating, 1))
    half = (rating % 2) - 1

    if rating == 1.5 or rating == 3.5:
        return {'empty': range(empty - 1), 'full': range(full), 'half': half}

    else:
        return {'empty': range(empty), 'full': range(full), 'half': half}


# Detay sayfasının def'i
# rating print_rating 'i cagırır buda bize empty,full ve half degerlerine erisimi verir
def details(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    rating = print_rating(recipe.rating)
    # ingredients binary tutuldugu icin onun pickle ile stringe ceviriyoruz
    ingredients_str = remove_bom(recipe.ingredients).decode('utf8') if recipe.ingredients else ""
    # gelen string [' bu sekilde basladıgı icin biz bunu join ile yeni stringde birlestiriyoruz
    # Bu sekilde duzgun bir sekilde gosteriyoruz
    ingredients_list = [ingredient.strip() for ingredient in ingredients_str.split(',') if ingredient.strip()]
    ingredients = ", ".join(ingredients_list)

    return render(request, 'DetailPage.html', {'recipe': recipe, 'rating': rating, 'ingredients': ingredients})


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
