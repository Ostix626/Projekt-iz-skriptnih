from django.urls import path

from . import views


urlpatterns = [
    path('', views.ulazniRacun, name='ulazniRacun'),
    path('racuni/', views.racuni, name='racuni'),
    # ex: /racuni/5/racun/
    path('racuni/<int:racun_id>/racun/', views.racun, name='racun'),
    path('info/', views.info, name='info'),
    path('ulaz/', views.ulaz, name='ulaz'),
]
