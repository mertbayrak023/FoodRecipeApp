import os

from better_profanity import profanity
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from Login.models import Recipe, User, Comments, Ingredients


# bu python dosyasında HomePage, DetailsPage, ProfilePage html sayfaları renderlanır
# ve bu sayfalarda kullanılıcak bilgiler ayarlanır

# HomePage.html renderlanırken databasedeki recipeler liste olarak gider
def home(request):
    recipes = Recipe.objects.filter(allowed=True)
    return render(request, 'HomePage.html', {'recipes': recipes})


def update_rating(request, recipe_id):
    recipeid = request.POST.get('recipe_id')
    if request.method == 'POST':
        rating = float(request.POST.get('rating'))

        recipe = Recipe.objects.get(recipe_id=recipeid)
        recipe.rating_num += rating
        recipe.rating_person += 1
        recipe.rating = round(float(recipe.rating_num / recipe.rating_person), 2)
        recipe.save()

        return redirect("details", recipe_id)

    return redirect("details", recipe_id)


def update_favorite(request, recipe_id):
    recipeid = recipe_id
    if request.method == 'POST':
        user_id = request.session.get('userid')
        user = User.objects.get(userid=user_id)
        user_favorites_str = remove_bom(user.favorites).decode('utf-8-sig') if user.favorites else ''
        user_favorites = [int(favorite.strip()) for favorite in user_favorites_str.split(',') if favorite.strip()]

        if recipeid in user_favorites:
            user_favorites.remove(recipeid)
        else:
            user_favorites.append(recipeid)

        user.favorites = ','.join(str(favorite) for favorite in user_favorites)
        user.favorites = user.favorites.encode('utf-8-sig')
        user.save()
        return redirect("details", recipe_id=recipeid)
    return redirect("details", recipe_id=recipeid)


def load_turkish_profanity():
    file_path = os.path.join(os.path.dirname(__file__), 'turkish_profanity.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    else:
        return []


def add_comment(request, recipe_id):
    user_id = request.session.get('userid')
    new_recipeid = recipe_id

    turkish_profanity = load_turkish_profanity()
    turkish_censor = profanity.add_censor_words(turkish_profanity)

    if request.method == 'POST':
        description = request.POST.get('new_comment').strip()

        if profanity.contains_profanity(description) or turkish_censor.contains_profanity(description):
            new_comment = Comments(recipeid=new_recipeid, description=description, userid=user_id, is_bad=True)
            new_comment.save()
        else:
            new_comment = Comments(recipeid=new_recipeid, description=description, userid=user_id)
            new_comment.save()

        return redirect("details", recipe_id)

    return redirect("details", recipe_id)


# Detay sayfasının def'i
# rating print_rating 'i cagırır buda bize empty,full ve half degerlerine erisimi verir
def details(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    comments = Comments.objects.filter(recipeid=recipe_id)
    comments = comments.filter(is_bad=False)
    is_favorite = False
    is_added = False
    commentable = True

    user_id = request.session.get('userid')
    if user_id:
        try:
            user = User.objects.get(userid=user_id)
        except User.DoesNotExist:
            is_favorite = False

        user_favorites_str = remove_bom(user.favorites).decode('utf-8-sig') if user.favorites else ''
        user_favorites = [int(favorite.strip()) for favorite in user_favorites_str.split(',') if favorite.strip()]
        for favorite in user_favorites:
            if favorite == recipe_id:
                is_favorite = True
                break
            else:
                is_favorite = False

        user_recipes_str = remove_bom(user.recipes).decode('utf-8-sig') if user.recipes else ''
        user_recipes = [int(recipes.strip()) for recipes in user_recipes_str.split(',') if recipes.strip()]
        for recipes in user_recipes:
            if recipes == recipe_id:
                is_added = True
                break
            else:
                is_added = False

    for comment in comments:
        if comment.userid == user_id:
            commentable = False
            break
        else:
            commentable = True

    ingredients_str = remove_bom(recipe.ingredients).decode('utf-8-sig') if recipe.ingredients else 0
    ingredients_list = [ingre.strip() for ingre in ingredients_str.split(',') if ingre.strip()]
    ingredients = ', '.join(ingredients_list)
    range_html = range(1, 6)

    preparation_steps = [step.strip() for step in recipe.preparation.strip().split("\n")] if recipe.preparation else ''

    context = {'recipe': recipe,
               'ingredients': ingredients,
               'range_html': range_html,
               'comments': comments,
               'is_favorite': is_favorite,
               'commentable': commentable,
               'preparation': preparation_steps,
               'is_added': is_added}

    return render(request, 'DetailPage.html', context)


# Binary seklinde depolanan dataya erismek istedigimizde b'\xef\xbb\xbf' bu kisim ile baslar binary sayilari
# Biz bu kismi kaldırıyoruz veriyi islemek icin
def remove_bom(data):
    if data.startswith(b'\xef\xbb\xbf'):
        return data[3:]
    elif data.startswith(b''):
        return data[0:]
    return data


def profile(request, userid):
    user = User.objects.get(userid=userid)

    user_favorites_str = remove_bom(user.favorites).decode('utf-8-sig') if user.favorites else 0
    user_favorites = [int(favorite.strip()) for favorite in user_favorites_str.split(',') if
                      favorite.strip()] if user_favorites_str else 0
    num_favorites = len(user_favorites) if user_favorites_str else 0

    user_recipes_str = remove_bom(user.recipes).decode('utf-8-sig') if user.recipes else 0
    user_recipes = [int(recipe.strip()) for recipe in user_recipes_str.split(',') if
                    recipe.strip()] if user_recipes_str else 0
    num_recipes = len(user_recipes) if user_recipes_str else 0

    if num_recipes > 0:
        recipes = Recipe.objects.filter(recipe_id__in=user_recipes)
    else:
        recipes = Recipe.objects.all()

    if num_favorites > 0:
        favorites = Recipe.objects.filter(recipe_id__in=user_favorites)
    else:
        favorites = Recipe.objects.all()

    return render(request, 'ProfilePage.html', {'user': user, 'favorites': favorites, 'num_favorites': num_favorites,
                                                'recipes': recipes, 'num_recipes': num_recipes})


def most_favorites(request):
    recipes = Recipe.objects.order_by('-rating')[:5]
    return render(request, 'FavoritesPage.html', {'recipes': recipes})


def add_recipe(request):
    if request.method == 'POST':
        recipe_name = request.POST.get('recipe_name')
        description = request.POST.get('description')
        ingredients_str = request.POST.get('ingre')
        ingredients_str = ingredients_str.replace(',', ', ')
        preparation = request.POST.get('preparation')
        image_file = request.FILES.get('image') if request.FILES.get('image') else None
        if image_file:
            filename, file_extension = os.path.splitext(image_file.name)
            file_name = recipe_name
            image_file.name = f"{file_name}{file_extension}"

        ingredients = ingredients_str.encode('utf-8-sig')
        recipe = Recipe.objects.create(recipe_name=recipe_name, description=description, ingredients=ingredients,
                                       image=image_file, image_url=image_file, preparation=preparation)

        recipe.save()

        if image_file:
            recipe.image_url = recipe.image.url
            recipe.save()

        recipe_id = recipe.recipe_id
        user_id = request.session.get('userid')
        user = User.objects.get(userid=user_id)
        if user.recipes:
            user_recipes_str = remove_bom(user.recipes).decode('utf-8-sig')
            user_recipes = [int(recipes.strip()) for recipes in user_recipes_str.split(',') if recipes.strip()]
        else:
            user_recipes = []

        user_recipes.append(recipe_id)
        user_recipes_str = ','.join(str(recipes) for recipes in user_recipes)

        user.recipes = user_recipes_str.encode('utf-8-sig')
        user.save()

    ingredients = Ingredients.objects.all()
    return render(request, 'AddRecipePage.html', {'ingredients': ingredients})


def options(request, userid):
    user = User.objects.get(userid=userid)

    if request.method == 'POST':
        new_username = request.POST.get('username') if request.POST.get('username') else None
        new_email = request.POST.get('email') if request.POST.get('email') else None

        old_password = request.POST.get('password_old') if request.POST.get('password_old') else None
        new_password1 = request.POST.get('password_new1') if request.POST.get('password_new1') else None
        new_password2 = request.POST.get('password_new2') if request.POST.get('password_new2') else None

        delete_value = request.POST.get('delete_button')

        image_file = request.FILES.get('image') if request.FILES.get('image') else None
        if image_file:
            os.remove(user.profile_photo.path)
            filename, file_extension = os.path.splitext(image_file.name)
            file_name = user.username
            image_file.name = f"{file_name}{file_extension}"
            user.profile_photo = image_file
            user.save()
            user.profile_photo_url = user.profile_photo.url
            user.save()

        if new_username:
            user.username = new_username
            user.save()

        if new_email:
            user.email = new_email
            user.save()

        if new_password1 and new_password2:
            if user.check_password(old_password):
                if new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()

        if delete_value == "1":
            del request.session['userid']
            user.delete()
            return HttpResponseRedirect('http://localhost:8000')

    return render(request, 'OptionsPage.html', {'user': user})


def search(request):
    recipes = Recipe.objects.all()
    filtered = []
    search_terms = request.GET.get('search')
    search_terms = search_terms.split()
    search_terms = [search_term.lower() for search_term in search_terms]
    for recipe in recipes:
        for search_term in search_terms:
            names = recipe.recipe_name.split()
            lowered_names = [name.lower() for name in names]
            if search_term in lowered_names:
                filtered.append(recipe)
                filtered = list(dict.fromkeys(filtered))
    return render(request, 'HomePage.html', {'recipes': filtered})


def edit_recipe(request, recipe_id):
    recipe = Recipe.objects.get(recipe_id=recipe_id)
    user = User.objects.get(userid=request.session.get('userid'))
    comments = Comments.objects.filter(recipeid=recipe_id)

    if request.method == 'POST':
        new_name = request.POST.get('recipe_name')
        new_description = request.POST.get('description')
        new_preparation = request.POST.get('preparation')
        ingredients_str = request.POST.get('ingre')
        ingredients_str = ingredients_str.replace(',', ', ')
        delete_value = request.POST.get('delete_button')
        image_file = request.FILES.get('image') if request.FILES.get('image') else None

        if delete_value == '1':
            user_recipes_str = remove_bom(user.recipes).decode('utf-8-sig') if user.recipes else 0
            user_recipes = [int(recipes.strip()) for recipes in user_recipes_str.split(',') if
                            recipes.strip()]
            user_recipes.remove(recipe_id)
            user.recipes = ','.join(str(favorite) for favorite in user_recipes)
            user.recipes = user.recipes.encode('utf-8-sig')

            user_favorites_str = remove_bom(user.favorites).decode('utf-8-sig') if user.favorites else ''
            user_favorites = [int(favorite.strip()) for favorite in user_favorites_str.split(',') if favorite.strip()]

            if recipe_id in user_favorites:
                user_favorites.remove(recipe_id)

            user.favorites = ','.join(str(favorite) for favorite in user_favorites)
            user.favorites = user.favorites.encode('utf-8-sig')

            user.save()
            os.remove(recipe.image.path)
            recipe.delete()
            comments.delete()
            return HttpResponseRedirect('http://localhost:8000')

        if image_file:
            os.remove(recipe.image.path)
            filename, file_extension = os.path.splitext(image_file.name)
            file_name = new_name
            image_file.name = f"{file_name}{file_extension}"
            recipe.image = image_file
            recipe.save()
            recipe.image_url = recipe.image.url
        recipe.recipe_name = new_name
        recipe.description = new_description
        recipe.preparation = new_preparation
        recipe.ingredients = ingredients_str.encode('utf-8-sig')
        recipe.save()

    ingredients = Ingredients.objects.all()
    recipe_ingres = remove_bom(recipe.ingredients).decode('utf-8-sig')
    recipe_ingres = recipe_ingres.split(',')
    return render(request, 'RecipeEditPage.html',
                  {'recipe': recipe, 'ingredients': ingredients, 'recipe_ingres': recipe_ingres})


def admin(request):
    recipes = Recipe.objects.filter(allowed=False)
    user = User.objects.get(userid=request.session.get('userid'))
    comments = Comments.objects.filter(is_bad=True)

    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        comment_id = request.POST.get('comment_id')
        if recipe_id:
            button_value = request.POST.get('button1')
            recipe_id = request.POST.get('recipe_id')
            if button_value == '0':
                recipe = recipes.get(recipe_id=recipe_id)
                recipe.allowed = 1
                recipe.save()
            if button_value == '1':
                recipe = recipes.get(recipe_id=recipe_id)
                user_recipes_str = remove_bom(user.recipes).decode('utf-8-sig') if user.recipes else 0
                user_recipes = [int(recipes.strip()) for recipes in user_recipes_str.split(',') if
                                recipes.strip()]
                user_recipes.remove(recipe.recipe_id)
                user.recipes = ','.join(str(recipes) for recipes in user_recipes)
                user.recipes = user.recipes.encode('utf-8-sig')
                user.save()
                if recipe.image:
                    os.remove(recipe.image.path)
                recipe.delete()

            recipes = Recipe.objects.filter(allowed=False)

        if comment_id:
            button_value = request.POST.get('button2')
            if button_value == '0':
                comment = comments.get(commentid=comment_id)
                comment.is_bad = False
                comment.save()
            if button_value == '1':
                comment = comments.get(commentid=comment_id)
                comment.delete()

            comments = Comments.objects.filter(is_bad=True)

    com_count = comments.count()
    recipe_count = recipes.count()
    return render(request, 'AdminPage.html',
                  {'recipes': recipes, 'comments': comments, 'com_count': com_count, 'recipe_count': recipe_count})
