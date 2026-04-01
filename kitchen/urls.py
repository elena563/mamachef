from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

app_name = 'Kitchen'


urlpatterns = [   
    path('', views.home, name='home'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # pages
    path('recipes/', views.recipes, name='recipes'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('profile/', views.profile, name='profile'),

    # crud
    path('recipe/new_recipe/', views.RecipeCreateView.as_view(), name='new_recipe'),
    path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='edit_recipe'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='delete_recipe'),
    path('recipe/<int:pk>/add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
]