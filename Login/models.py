from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# Custom user modeli kullandıgımız icin UserManager'i olusturmamızı istiyor django
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


# Custom user modeli
# databasedeki tablolarin fiziksel gosterimi
# html ve pythonda kullanırken bu classlari kullanıcaz
class User(AbstractBaseUser, PermissionsMixin):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=50, unique=True)
    favorites = models.BinaryField(blank=True, null=True)
    recipes = models.BinaryField(blank=True, null=True)
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField(blank=True, null=True)
    profile_photo = models.TextField(
        default='https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/340px-Default_pfp.svg.png'
                '?20220226140232 ')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        managed = True
        db_table = 'User'


# Recipe tablosunun modeli
class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    recipe_name = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.BinaryField()
    rating_person = models.IntegerField()
    rating_num = models.IntegerField()
    rating = models.FloatField()
    image = models.BinaryField()
    image_url = models.TextField()

    class Meta:
        managed = False
        db_table = 'Recipe'


# Favori tablosunun modeli
class Favorites(models.Model):
    favoritesid = models.AutoField(primary_key=True)
    recipeid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Favorites'
