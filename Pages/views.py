from django.shortcuts import render, get_object_or_404

from Login.models import Recipe, User


# HomePage.html renderlanırken databasedeki recipeler liste olarak gider
def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'HomePage.html', {'recipes': recipes})


# def home ile aynı mantıkta calısır tek farkı detail'i yoksa o recipenin 404 hatası verir(get_objects_or_404)
def details(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    return render(request, 'DetailPage.html', {'recipe': recipe})


# def home ile aynı mantıkta calısır, login olmus olan user'in id'si ile
# databasede kayıtlı olan user'in userid'si eslenen useri yollar
def profile(request, userid):
    user = User.objects.get(userid=userid)
    return render(request, 'ProfilePage.html', {'user': user})
