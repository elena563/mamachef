from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy

from .models import Recipe, RecipeIngredient, Ingredient, RecipeIngredient
from .forms import RecipeForm
from functions.recipe_helpers import save_ingredients

def home(request):
    recipes = Recipe.objects.all()
    return render(request, 'home.html', {'recipes':recipes})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('Kitchen:home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def recipes(request):
    """Recipes page view"""
    recipes = Recipe.objects.all()
    return render(request, 'recipes.html', {'recipes': recipes})

def recipe_detail(request, pk):
    """Recipe detail view"""
    recipe = get_object_or_404(Recipe, pk=pk)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = recipe.steps.all()
    return render(request, 'recipe_detail.html', {'recipe': recipe, 'ingredients': ingredients, 'steps': steps})

class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'
    success_url = reverse_lazy('Kitchen:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit_choices'] = [choice[0] for choice in RecipeIngredient.UNIT_CHOICES]
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        save_ingredients(self.request.POST, self.object)
        return response

class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipe_form.html'
    success_url = reverse_lazy('Kitchen:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit_choices'] = [choice[0] for choice in RecipeIngredient.UNIT_CHOICES]
        return context
    
    def form_valid(self, form):
        self.object = form.save()

        RecipeIngredient.objects.filter(recipe=self.object).delete()
        save_ingredients(self.request.POST, self.object)
        return super().form_valid(form)

def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.delete()
    return redirect('Kitchen:recipes')