from django.shortcuts import render, get_object_or_404
from Login.models import Recipe, User


#
def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'HomePage.html', {'recipes': recipes})


def details(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    return render(request, 'DetailPage.html', {'recipe': recipe})


def profile(request, userid):
    user = User.objects.get(userid=userid)
    return render(request, 'ProfilePage.html', {'user': user})
