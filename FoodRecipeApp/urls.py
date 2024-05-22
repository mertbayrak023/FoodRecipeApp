from django.urls import include, path

# İlk path sayesinde proje çalıştırıldığında ana sayfa gelir
# Bu sekilde ana sayfaya giris yapmadan erisilenebiliyor
# html kodlarının calısması için gerekli kodlar
# path verilerek views calıstırılıyor, views de template'i calıstırıyor, sonucta html kodları calısıyor
urlpatterns = [
    path("", include("Login.urls")),
    path("", include("Pages.urls")),
]
