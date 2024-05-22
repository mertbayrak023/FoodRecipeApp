import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import FileExtensionValidator
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
    favorites = models.BinaryField(blank=True, null=True, default=0)
    recipes = models.BinaryField(blank=True, null=True, default=0)
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField(blank=True, null=True)
    profile_photo_url = models.TextField(
        default='https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/340px-Default_pfp.svg.png'
                '?20220226140232 ')
    profile_photo = models.ImageField(upload_to='Images_Folder/', null=True, blank=True,
                                      validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    is_staff = models.BooleanField()

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
    rating_person = models.IntegerField(default=0)
    rating_num = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    image = models.ImageField(upload_to='Images_Folder/', null=True, blank=True,
                              validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    image_url = models.TextField(null=True, blank=True)
    preparation = models.TextField()
    allowed = models.BooleanField(default=False)

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


# Comments tablosunun modeli
class Comments(models.Model):
    commentid = models.AutoField(primary_key=True)
    description = models.TextField()
    recipeid = models.IntegerField()
    userid = models.IntegerField()
    is_bad = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'Comments'


# Ingredients tablosunun modeli
class Ingredients(models.Model):
    ingreid = models.AutoField(primary_key=True)
    ingrename = models.CharField(max_length=20)
    unit = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'Ingredients'


# Images tablosunun modeli(Suanlik kullanilmiyor)
class Images(models.Model):
    Id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ImageByte = models.BinaryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Id'], name='unique_image_id')
        ]
        managed = False
        db_table = 'Images_Folder'
