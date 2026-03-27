from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

app_name = 'Kitchen'


urlpatterns = [   
    path('', views.home, name='home'),
    path('recipes/', views.recipes, name='recipes'),
]