from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Recipe
from .forms import RecipeForm

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def recipes(request):
    """Recipes page view"""
    return render(request, 'recipes.html')

class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'
    success_url = reverse_lazy('kitchen:home')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'
    success_url = reverse_lazy('kitchen:home')

