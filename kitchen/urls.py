from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

app_name = 'Kitchen'


urlpatterns = [   
    path('', views.home, name='home'),
    path('recipes/', views.recipes, name='recipes'),
    
    path('recipe/new_recipe/', views.RecipeCreateView.as_view(), name='new_recipe'),
    path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='edit_recipe'),
]