from django import forms

from Login.models import User


# Kullanıcı kayıt için kullandığımız form
class UserRegistrationForm(forms.ModelForm):
    # password1 ve password2 propertyleri açıyoruz, widget ile password'un tipinin PasswordInput olduğunu belirtiyoruz
    password1 = forms.CharField(label='password1', widget=forms.PasswordInput)
    password2 = forms.CharField(label='password2', widget=forms.PasswordInput)

    class Meta:
        # User modelini belirtiyoruz
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        # password1 ve password2'yi yerleştiriyoruz
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        # Şifrelerin aynı olup olmadığını kontrol ediyoruz
        if password1 != password2:
            self.add_error('password2', 'Şifreler uyuşmuyor')
        return password2

    # User'i kaydetmek için kullandığımız fonksiyon
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# Kullanıcı girişi için kullandığımız form
class UserLoginForm(forms.Form):
    # username ve password propertyleri açıyoruz
    username = forms.CharField(label='username')
    password = forms.CharField(label='password', widget=forms.PasswordInput)

    def clean(self):
        # username ve password'u yerleştiriyoruz
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        # password'un databasede hash'li şekilde şifrelenmiştir validate_credentials bu şifreyi kırıp şifre ve kullanıcı adının var olup olmadığına bakar ve kontrol eder
        # buna authentication islemi deniliyor
        self.validate_credentials(username, password)
        return self.cleaned_data

    def validate_credentials(self, username, password):
        # if not kullanarak kullanıcı yoksa uyarı verir
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Kullanıcı bulunamadı')

        user = User.objects.get(username=username)
        # if not kullanarak user'ın username'inin şifresine bakar, yanlışsa uyarı verir
        if not user.check_password(password):
            raise forms.ValidationError('Şifreniz yanlış')

        return user
