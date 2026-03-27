from django.shortcuts import render

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def recipes(request):
    """Recipes page view"""
    return render(request, 'recipes.html')

def create_recipe(request):
    """Create recipe page view"""
    return render(request, 'create_recipe.html')