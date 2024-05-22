from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from Forms.views import UserRegistrationForm, UserLoginForm
from Login.models import User


# login için kullanılan post metodu
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = form.validate_credentials(username, password)
            for_userid = User.objects.get(username=username)
            if user is not None:
                login(request, user)
                request.session["userid"] = for_userid.userid
                return HttpResponseRedirect('http://localhost:8000')
            else:
                print(form.errors)
                return render(request, 'LoginPage.html', {'form': form, 'errors': form.errors})
    else:
        form = UserLoginForm()
    if 'userid' in request.session:
        user = User.objects.get(userid=request.session['userid'])
        return render(request, 'Homepage.html', {'user': user})
    return render(request, 'LoginPage.html', {'form': form})


# logout icin kullanılan method
def user_logout(request):
    # kullanıcıyı arka plandan silinir
    if request.user.is_authenticated:
        logout(request)
    if 'userid' in request.session:
        del request.session['userid']
    # kullanıcıyı sildikten sonra ana sayfaya atar, urls.py da belirttigimiz uzere localhost:8000 de ana sayfa var
    return HttpResponseRedirect('http://localhost:8000')


# register için kullanılan post metodu user_login ile aynı olarak kullanılan metodları tekrardan belirtilmemistir
def register(request):
    if request.method == 'POST':
        # yazdıgımız UserRegistrationForm kullanılıcak diye belirtiyoruz
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            # register kısmı basarılı oldugu icin user_login metodu aktive ediliyor yani login sayfasına atıyor
            return redirect('login')
        else:
            # kayıt surecinde bir hata olursa python consoluna error verilir yazdırır
            print(form.errors)
            return render(request, 'RegisterPage.html', {'form': form, 'errors': form.errors})

    else:
        form = UserRegistrationForm()

    return render(request, 'RegisterPage.html', {'form': form})
